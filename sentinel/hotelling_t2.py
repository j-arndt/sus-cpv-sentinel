"""
hotelling_t2.py — Hotelling T² multivariate SPC monitor
URS: URS-030 through URS-034
Risk: RA-030 through RA-032
Regulation: FDA Process Validation 2011 Stage 3 / ICH Q9(R1)
"""

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy import stats

from sentinel.audit_trail import AuditTrail
from sentinel.integrity_cpk import DeviationAlert


@dataclass
class HotellingResult:
    n: int
    p: int
    ucl: float
    t2_values: list[float]
    lot_numbers: list[str]
    dates: list[str]
    ooc_indices: list[int]
    variables: list[str]


def run_hotelling(
    df: pd.DataFrame,
    audit: AuditTrail,
    config: dict,
) -> tuple[HotellingResult | None, list[DeviationAlert]]:
    """
    Compute Hotelling T² for [delta_p_mbar, test_temp_c, lot_age_days].

    URS-030: T² on 3-variable vector
    URS-031: UCL from F-distribution at α=0.0027
    URS-032: flag OOC, generate alert
    URS-034: audit all calculations
    """
    cfg = config["hotelling"]
    variables = cfg["variables"]
    alpha = cfg["alpha"]
    min_obs = cfg["min_observations"]
    citation = config["regulatory_citations"]["hotelling"]

    sub = df[variables + ["lot_number", "test_date"]].dropna(subset=variables).copy()
    sub = sub.sort_values("test_date")
    n = len(sub)
    p = len(variables)

    if n < min_obs:
        audit.log(
            action="hotelling_skipped",
            inputs={"n": n, "min_required": min_obs, "variables": variables},
            outputs={"status": "insufficient_data"},
            rule_reference="URS-030",
        )
        return None, []

    X = sub[variables].values.astype(float)
    lot_nums = sub["lot_number"].tolist()
    dates = sub["test_date"].astype(str).tolist()

    # Fit on first 60% as baseline (stable pre-SCN period)
    baseline_n = max(min_obs, int(n * 0.60))
    X_base = X[:baseline_n]
    x_bar = np.mean(X_base, axis=0)
    S = np.cov(X_base.T)

    try:
        S_inv = np.linalg.inv(S)
    except np.linalg.LinAlgError:
        return None, []

    # UCL from F-distribution: p(n-1)/(n-p) * F(alpha, p, n-p)
    F_crit = stats.f.ppf(1 - alpha, p, baseline_n - p)
    ucl = (p * (baseline_n - 1)) / (baseline_n - p) * F_crit

    # Compute T² for every observation
    def t2_stat(x):
        d = x - x_bar
        return float(d @ S_inv @ d)

    t2_vals = [t2_stat(x) for x in X]
    ooc = [i for i, v in enumerate(t2_vals) if v > ucl]

    alerts: list[DeviationAlert] = []
    if ooc:
        violation_lots = [lot_nums[i] for i in ooc]
        alerts.append(DeviationAlert(
            alert_type="HOTELLING_T2_OOC",
            sku_id="ALL",
            supplier_name="ALL",
            metric="Hotelling T² multivariate monitor",
            value=round(max(t2_vals[i] for i in ooc), 3),
            criterion=f"T² ≤ UCL ({ucl:.3f})",
            lot_numbers=violation_lots,
            regulatory_ref=citation,
        ))

    audit.log(
        action="t2_calculation",
        inputs={"n": n, "p": p, "baseline_n": baseline_n, "alpha": alpha, "variables": variables},
        outputs={"ucl": round(ucl, 4), "ooc_count": len(ooc), "max_t2": round(max(t2_vals), 4)},
        rule_reference=citation,
    )

    result = HotellingResult(
        n=n, p=p, ucl=round(ucl, 4),
        t2_values=[round(v, 4) for v in t2_vals],
        lot_numbers=lot_nums, dates=dates,
        ooc_indices=ooc, variables=variables,
    )
    return result, alerts
