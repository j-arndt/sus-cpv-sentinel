"""
ingest.py — CSV ingestion with schema validation and ALCOA+ audit logging
URS: URS-001 through URS-007
Risk: RA-001 through RA-004
"""

import hashlib
from pathlib import Path

import pandas as pd
import yaml

from sentinel.audit_trail import AuditTrail

REQUIRED_FIELDS = [
    "lot_number", "sku_id", "supplier_name", "test_date",
    "delta_p_mbar", "test_temp_c", "lot_age_days",
    "coa_complete", "result",
]
NUMERIC_FIELDS = ["delta_p_mbar", "test_temp_c", "lot_age_days"]
BOOLEAN_FIELDS = ["coa_complete"]
VALID_RESULTS = {"PASS", "FAIL"}


class IngestValidationError(Exception):
    """Raised when input data fails schema validation (URS-002, URS-003)."""
    pass


def _sha256_file(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_and_validate(filepath: str, audit: AuditTrail) -> pd.DataFrame:
    """
    Load CSV, validate schema, return clean DataFrame.

    URS-001: accepts CSV with defined schema
    URS-002: validates required fields present
    URS-003: rejects and logs on missing required fields
    URS-004: enforces data types
    URS-006: does not modify source file
    URS-007: logs file name, SHA-256 hash, row count, timestamp
    """
    path = Path(filepath)
    file_hash = _sha256_file(filepath)

    df = pd.read_csv(filepath, dtype=str)  # load all as str first
    raw_row_count = len(df)

    # URS-002 / URS-003 — required field check
    missing_cols = [c for c in REQUIRED_FIELDS if c not in df.columns]
    if missing_cols:
        audit.log(
            action="ingest_rejected",
            inputs={"file": path.name, "sha256": file_hash},
            outputs={"error": "missing_columns", "columns": missing_cols},
            rule_reference="URS-003 / MHRA GxP Data Integrity 2018",
        )
        raise IngestValidationError(
            f"Missing required columns: {missing_cols}"
        )

    # Row-level validation
    errors = []
    for idx, row in df.iterrows():
        row_errors = []
        for field in REQUIRED_FIELDS:
            val = row.get(field)
            if pd.isna(val) or str(val).strip() == "":
                row_errors.append(f"row {idx+2}: field '{field}' is null or empty")
        if row_errors:
            errors.extend(row_errors)

    if errors:
        audit.log(
            action="ingest_rejected",
            inputs={"file": path.name, "sha256": file_hash, "row_count": raw_row_count},
            outputs={"error": "missing_required_values", "details": errors[:20]},
            rule_reference="URS-003 / 21 CFR Part 11 §11.10(e)",
        )
        raise IngestValidationError(
            f"Required field validation failed ({len(errors)} error(s)):\n" +
            "\n".join(errors[:10]) +
            (f"\n... and {len(errors)-10} more" if len(errors) > 10 else "")
        )

    # URS-004 — type coercion
    for field in NUMERIC_FIELDS:
        df[field] = pd.to_numeric(df[field], errors="coerce")
        bad = df[df[field].isna()].index.tolist()
        if bad:
            audit.log(
                action="ingest_rejected",
                inputs={"file": path.name, "field": field},
                outputs={"error": "type_coercion_failed", "rows": bad},
                rule_reference="URS-004",
            )
            raise IngestValidationError(
                f"Type error: field '{field}' contains non-numeric values at rows {bad[:5]}"
            )

    df["coa_complete"] = df["coa_complete"].str.upper().map(
        {"TRUE": True, "FALSE": False, "1": True, "0": False, "YES": True, "NO": False}
    )
    df["test_date"] = pd.to_datetime(df["test_date"], format="%Y-%m-%d", errors="coerce")
    bad_dates = df[df["test_date"].isna()].index.tolist()
    if bad_dates:
        raise IngestValidationError(
            f"Invalid ISO 8601 date in 'test_date' at rows {bad_dates[:5]}"
        )

    bad_results = df[~df["result"].isin(VALID_RESULTS)].index.tolist()
    if bad_results:
        raise IngestValidationError(
            f"'result' must be PASS or FAIL; invalid values at rows {bad_results[:5]}"
        )

    # Optional numeric fields — coerce safely (URS-004)
    for opt_field in ["el_measurement", "scn_impact_score"]:
        if opt_field in df.columns:
            df[opt_field] = pd.to_numeric(df[opt_field], errors="coerce")

    # URS-007 — successful ingestion audit entry
    audit.log(
        action="file_ingestion",
        inputs={"file": path.name, "sha256": file_hash},
        outputs={"row_count": raw_row_count, "status": "success"},
        rule_reference="URS-007 / ALCOA+ Attributable+Original",
    )

    return df.reset_index(drop=True)
