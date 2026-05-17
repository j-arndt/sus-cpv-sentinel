"""
audit_trail.py — ALCOA+-compliant immutable audit trail
URS: URS-050 through URS-057
Risk: RA-040 through RA-044
Regulation: 21 CFR Part 11 §11.10(e) / MHRA GxP Data Integrity Guidance 2018
"""

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class AuditIntegrityError(Exception):
    """Raised when hash chain verification fails (URS-056)."""
    pass


class AuditTrail:
    """
    Append-only, hash-chained JSON-Lines audit trail.

    Each entry contains:
      event_id    : SHA-256 of the entry content (excluding event_id itself)
      prev_hash   : SHA-256 of the previous entry ('GENESIS' if first)
      timestamp_utc: ISO 8601 UTC timestamp
      user        : actor identity
      action      : action type string
      inputs      : dict of input parameters
      outputs     : dict of output values
      rule_reference: applicable regulatory citation

    URS-052: Hash chain — tamper detection on load.
    URS-053: No delete or update API exposed.
    URS-054: JSONL primary file + SQLite index.
    """

    def __init__(self, path: str, user: str = "system"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.user = user
        self._last_hash = self._load_last_hash()

    # ------------------------------------------------------------------ #
    # Public write API                                                     #
    # ------------------------------------------------------------------ #

    def log(
        self,
        action: str,
        inputs: dict[str, Any],
        outputs: dict[str, Any],
        rule_reference: str = "",
    ) -> dict:
        """Append one ALCOA+-compliant entry and return it."""
        entry = self._build_entry(action, inputs, outputs, rule_reference)
        self._append(entry)
        self._last_hash = entry["event_id"]
        self._index(entry)
        return entry

    def session_start(self) -> dict:
        return self.log("session_start", {}, {}, "21 CFR Part 11 §11.10(e)")

    def session_end(self) -> dict:
        return self.log("session_end", {}, {}, "21 CFR Part 11 §11.10(e)")

    # ------------------------------------------------------------------ #
    # Read / verify API                                                    #
    # ------------------------------------------------------------------ #

    def load_entries(self) -> list[dict]:
        """Load all entries and verify hash chain integrity (URS-056)."""
        if not self.path.exists():
            return []
        entries = []
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        self._verify_chain(entries)
        return entries

    def verify(self) -> bool:
        """Return True if hash chain is intact, raise AuditIntegrityError otherwise."""
        self.load_entries()
        return True

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _build_entry(self, action, inputs, outputs, rule_reference) -> dict:
        core = {
            "prev_hash": self._last_hash,
            "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "user": self.user,
            "action": action,
            "inputs": inputs,
            "outputs": outputs,
            "rule_reference": rule_reference,
        }
        core_json = json.dumps(core, sort_keys=True, default=str)
        event_id = hashlib.sha256(core_json.encode()).hexdigest()
        return {"event_id": event_id, **core}

    def _append(self, entry: dict) -> None:
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")

    def _load_last_hash(self) -> str:
        """Return hash of last entry, or 'GENESIS' if file is empty."""
        if not self.path.exists():
            return "GENESIS"
        last = None
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    last = json.loads(line)
        return last["event_id"] if last else "GENESIS"

    def _verify_chain(self, entries: list[dict]) -> None:
        """Walk the hash chain; raise AuditIntegrityError on any mismatch."""
        prev = "GENESIS"
        for i, entry in enumerate(entries):
            if entry["prev_hash"] != prev:
                raise AuditIntegrityError(
                    f"Audit trail integrity verification failed — "
                    f"hash chain broken at entry {i} (action={entry.get('action')}). "
                    f"Expected prev_hash={prev!r}, got {entry['prev_hash']!r}."
                )
            # Recompute event_id to confirm entry wasn't tampered
            core = {k: v for k, v in entry.items() if k != "event_id"}
            core_json = json.dumps(core, sort_keys=True, default=str)
            expected_id = hashlib.sha256(core_json.encode()).hexdigest()
            if entry["event_id"] != expected_id:
                raise AuditIntegrityError(
                    f"Audit trail integrity verification failed — "
                    f"event_id mismatch at entry {i}. Entry content has been modified."
                )
            prev = entry["event_id"]

    def _index(self, entry: dict) -> None:
        """Upsert entry into SQLite index for query performance (URS-054)."""
        db_path = self.path.parent / "audit_index.db"
        with sqlite3.connect(str(db_path)) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS audit_entries (
                    event_id TEXT PRIMARY KEY,
                    timestamp_utc TEXT,
                    user TEXT,
                    action TEXT,
                    rule_reference TEXT,
                    entry_json TEXT
                )"""
            )
            conn.execute(
                """INSERT OR IGNORE INTO audit_entries
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    entry["event_id"],
                    entry["timestamp_utc"],
                    entry["user"],
                    entry["action"],
                    entry["rule_reference"],
                    json.dumps(entry, default=str),
                ),
            )
