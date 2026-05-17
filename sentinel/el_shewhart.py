"""
el_shewhart.py — E&L Shewhart I-MR control charts with Nelson Rule detection
URS: URS-020 through URS-026
Risk: RA-020 through RA-023
Regulation: PDA TR 66 §8.2 / ASTM E3051-25
"""

from dataclasses import dataclass, field
from itertools import groupby

import numpy as np
import pandas as pd

from sentinel.audit_trail import AuditTrail
from sentinel.integrity_cpk import DeviationAlert


@dataclass
class ShewhartResult:
    sku_id: str
    supplier_name: str
    compound: str
    n: int
    mean: float
    ucl: float
    lcl: float
    mr_ucl: float
    values: list[float]
    lot_numbers: list[str]
    dates: list[str]
    rule1_violations: list[int]   # indices
    rule2_violations: list[int]   # indices of the triggering (9th) point


def _compute_limits(vals: np.ndarray, d2: float, d4: float) -> tuple:
    vals = vals.astype(np.float64)  # guard against object/mixed dtype arrays
    mean = float(np.mean(vals))
    mr = np.abs(np.diff(vals))
    mr_bar = float(np.mean(mr)) if len(mr) > 0 else 0.0
    sigma_hat = mr_bar / d2 if d2 != 0 else 0.0
    ucl = mean + 3 * sigma_hat
    lcl = mean - 3 * sigma_hat
    mr_ucl = d4 * mr_bar
    return mean, ucl, lcl, mr_ucl, sigma_hat


def _nelson_rule1(vals: np.ndarray, mean: float, sigma: float) -> list[int]:
    """Points beyond ±3σ (URS-022)."""
    return [i for i, v in enumerate(vals) if abs(v - mean) > 3 * sigma]


def _nelson_rule2(vals: np.ndarray, mean: float) -> list[int]:
    """9+ consecutive points same side of centreline (URS-023).
    Returns indices of the 9th point in each run."""
    signs = [1 if v >= mean else -1 for v in vals]
    violations = []
    run_len = 1
    for i in range(1, len(signs)):
        if signs[i] == signs[i - 1]:
            run_len += 1
            if run_len == 9:
                violations.append(i)
        else:
            run_len = 1
    return violations


def run_shewhart(
    df: pd.DataFrame,
    audit: AuditTrail,
    config: dict,
) -> tuple[list[ShewhartResult], list[DeviationAlert]]:
    """
    Compute I-MR control charts and detect Nelson violations per supplier/SKU/compound.
    URS-020: generate charts per supplier per SKU
    URS-021: correct control limits
    URS-022: Nelson Rule 1
    URS-023: Nelson Rule 2
    URS-025: generate deviation alert
    URS-026: audit all evaluations
    """
    d2 = config["integrity_test"]["d2_constant"]
    d4 = config["shewhart"]["d4_constant"]
    citation = config["regulatory_citations"]["shewhart"]

    # Work on rows that have E&L data — force numeric to prevent mixed-type errors
    df = df.copy()
    df["el_measurement"] = pd.to_numeric(df["el_measurement"], errors="coerce")
    el_df = df.dropna(subset=["el_measurement"]).copy()

    # Group by supplier + SKU + compound
    compound_col = "el_compound" if "el_compound" in el_df.columns else None
    group_keys = ["supplier_name", "sku_id"]
    if compound_col:
        group_keys.append(compound_col)

    results: list[ShewhartResult] = []
    alerts: list[DeviationAlert] = []

    for keys, group in el_df.groupby(group_keys):
        group = group.sort_values("test_date")
        supplier = keys[0]
        sku = keys[1]
        compound = keys[2] if len(keys) > 2 else "E&L"
        vals = group["el_measurement"].values.astype(np.float64)
        lot_nums = group["lot_number"].tolist()
        dates = group["test_date"].astype(str).tolist()
        n = len(vals)

        if n < 4:
            continue  # too few to compute meaningful limits

        mean, ucl, lcl, mr_ucl, sigma = _compute_limits(vals, d2, d4)
        r1 = _nelson_rule1(vals, mean, sigma)
        r2 = _nelson_rule2(vals, mean)

        # Generate deviation alerts
        if r1:
            violation_lots = [lot_nums[i] for i in r1]
            alert = DeviationAlert(
                alert_type="NELSON_RULE_1",
                sku_id=sku,
                supplier_name=supplier,
                metric=f"E&L Shewhart I-chart ({compound})",
                value=round(float(vals[r1[0]]), 4),
                criterion=f"Within ±3σ (UCL={ucl:.4f}, LCL={lcl:.4f})",
                lot_numbers=violation_lots,
                regulatory_ref=citation,
            )
            alerts.append(alert)

        if r2:
            violation_lots = [lot_nums[i] for i in r2]
            alert = DeviationAlert(
                alert_type="NELSON_RULE_2",
                sku_id=sku,
                supplier_name=supplier,
                metric=f"E&L Shewhart I-chart ({compound})",
                value=9.0,
                criterion="No run of 9 consecutive points same side of centreline",
                lot_numbers=violation_lots,
                regulatory_ref=citation,
            )
            alerts.append(alert)

        audit.log(
            action="shewhart_calculation",
            inputs={"supplier": supplier, "sku_id": sku, "compound": compound, "n": n},
            outputs={
                "mean": round(mean, 4), "ucl": round(ucl, 4), "lcl": round(lcl, 4),
                "rule1_violations": len(r1), "rule2_violations": len(r2),
            },
            rule_reference=citation,
        )

        results.append(ShewhartResult(
            sku_id=sku, supplier_name=supplier, compound=compound, n=n,
            mean=round(mean, 4), ucl=round(ucl, 4), lcl=round(lcl, 4),
            mr_ucl=round(mr_ucl, 4),
            values=vals.tolist(), lot_numbers=lot_nums, dates=dates,
            rule1_violations=r1, rule2_violations=r2,
        ))

    return results, alerts
