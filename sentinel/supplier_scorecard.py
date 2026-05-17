"""
supplier_scorecard.py — Composite supplier performance ranking with SCN alerting
URS: URS-040 through URS-045
Risk: none specific (operational/compliance)
Regulation: ASTM E3051-25 §6 / PDA TR 66 §9
"""

from dataclasses import dataclass, field
from datetime import timedelta

import pandas as pd

from sentinel.audit_trail import AuditTrail
from sentinel.integrity_cpk import DeviationAlert


@dataclass
class SupplierScore:
    supplier_name: str
    lot_count: int
    rejection_rate: float
    scn_total_impact: float
    coa_completeness: float
    integrity_fail_rate: float
    composite_score: float   # 0–1, higher = better
    rank: int = 0


def run_scorecard(
    df: pd.DataFrame,
    audit: AuditTrail,
    config: dict,
) -> tuple[list[SupplierScore], list[DeviationAlert]]:
    """
    Compute composite supplier scorecard and detect SCN threshold breaches.

    URS-040: composite score from 4 metrics
    URS-041: weights from config
    URS-042: rank suppliers
    URS-043: SCN alert when rolling 12-month impact > threshold
    URS-044: alert names specific SCN reference
    URS-045: log to audit trail
    """
    weights = config["scorecard"]["weights"]
    scn_threshold = config["scorecard"]["scn_alert_threshold"]
    citation = config["regulatory_citations"]["scorecard"]

    scores: list[SupplierScore] = []
    alerts: list[DeviationAlert] = []

    cutoff = df["test_date"].max() - timedelta(days=365)

    for supplier, grp in df.groupby("supplier_name"):
        n = len(grp)
        rejection_rate = (grp["result"] == "FAIL").mean()
        coa_completeness = grp["coa_complete"].mean() if "coa_complete" in grp else 1.0
        integrity_fail_rate = rejection_rate  # same source for this schema

        # SCN scoring — rolling 12 months
        scn_grp = grp[grp["test_date"] >= cutoff].copy()
        rolling_scn_impact = 0.0
        scn_refs = []
        if "scn_impact_score" in scn_grp.columns:
            scn_grp["scn_impact_score"] = pd.to_numeric(
                scn_grp["scn_impact_score"], errors="coerce"
            )
            scn_grp = scn_grp.dropna(subset=["scn_impact_score"])
            if len(scn_grp) > 0:
                rolling_scn_impact = float(scn_grp["scn_impact_score"].sum())
                if "scn_reference" in scn_grp.columns:
                    scn_refs = scn_grp["scn_reference"].dropna().unique().tolist()

        # Normalise SCN impact: 0 = good (0 impact), 1 = bad (≥10 impact)
        scn_score_norm = min(rolling_scn_impact / 10.0, 1.0)

        # Composite: weighted average where higher = better supplier
        composite = (
            weights["rejection_rate"] * (1.0 - rejection_rate) +
            weights["scn_impact"] * (1.0 - scn_score_norm) +
            weights["coa_completeness"] * coa_completeness +
            weights["integrity_fail_rate"] * (1.0 - integrity_fail_rate)
        )

        # SCN threshold alert (URS-043, URS-044)
        if rolling_scn_impact > scn_threshold:
            ref_str = ", ".join(scn_refs) if scn_refs else "See supplier SCN register"
            alerts.append(DeviationAlert(
                alert_type="SCN_THRESHOLD_EXCEEDED",
                sku_id="ALL",
                supplier_name=supplier,
                metric="Rolling 12-month SCN impact score",
                value=round(rolling_scn_impact, 1),
                criterion=f"≤ {scn_threshold}",
                lot_numbers=scn_grp["lot_number"].tolist(),
                regulatory_ref=f"{citation} | SCN references: {ref_str}",
            ))

        audit.log(
            action="scorecard_calculation",
            inputs={"supplier": supplier, "n": n, "rolling_window_days": 365},
            outputs={
                "rejection_rate": round(rejection_rate, 4),
                "scn_impact": round(rolling_scn_impact, 2),
                "coa_completeness": round(coa_completeness, 4),
                "composite_score": round(composite, 4),
                "scn_references": scn_refs,
            },
            rule_reference=citation,
        )

        scores.append(SupplierScore(
            supplier_name=supplier, lot_count=n,
            rejection_rate=round(rejection_rate, 4),
            scn_total_impact=round(rolling_scn_impact, 2),
            coa_completeness=round(coa_completeness, 4),
            integrity_fail_rate=round(integrity_fail_rate, 4),
            composite_score=round(composite, 4),
        ))

    # Rank descending by composite score
    scores.sort(key=lambda s: s.composite_score, reverse=True)
    for i, s in enumerate(scores):
        s.rank = i + 1

    return scores, alerts
