"""
integrity_cpk.py — Cpk / Ppk process capability analysis per SUS SKU
URS: URS-010 through URS-016
Risk: RA-010 through RA-013
Regulation: ASTM E3244-23 §4.2 / FDA Process Validation 2011 Stage 3
"""

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import yaml

from sentinel.audit_trail import AuditTrail

STATUS_OOS = "OUT_OF_SPECIFICATION"
STATUS_MARGINAL = "MARGINAL — MONITOR"
STATUS_CAPABLE = "CAPABLE"


@dataclass
class CapabilityResult:
    sku_id: str
    supplier_name: str
    n: int
    mean: float
    std_within: float   # σ̂ = R̄/d₂
    std_overall: float  # overall sample std dev
    cpk: float
    ppk: float
    status: str
    alert: str | None = None


@dataclass
class DeviationAlert:
    alert_type: str
    sku_id: str
    supplier_name: str
    metric: str
    value: float
    criterion: str
    lot_numbers: list[str] = field(default_factory=list)
    regulatory_ref: str = ""


def _cpk(mean, std, usl, lsl):
    if std == 0:
        return float("inf")
    return min((usl - mean) / (3 * std), (mean - lsl) / (3 * std))


def run_capability(
    df: pd.DataFrame,
    audit: AuditTrail,
    config: dict,
) -> tuple[list[CapabilityResult], list[DeviationAlert]]:
    """
    Compute Cpk/Ppk per SKU on pressure-decay delta_p_mbar data.

    Returns (results, alerts).
    URS-010: Cpk per SKU
    URS-011: Ppk per SKU
    URS-013: OOS alert when Cpk < threshold
    URS-014: Marginal flag
    URS-015: minimum n enforcement
    URS-016: audit trail for all calculations
    """
    cfg = config["integrity_test"]
    usl = cfg["usl_mbar"]
    lsl = cfg["lsl_mbar"]
    min_n = cfg["min_lots_cpk"]
    oos_thresh = cfg["cpk_oos_threshold"]
    marg_thresh = cfg["cpk_marginal_threshold"]
    d2 = cfg["d2_constant"]
    citation = config["regulatory_citations"]["cpk"]

    results: list[CapabilityResult] = []
    alerts: list[DeviationAlert] = []

    grouped = df.groupby(["sku_id", "supplier_name"])

    for (sku, supplier), group in grouped:
        vals = group["delta_p_mbar"].dropna().values
        n = len(vals)
        lot_nums = group["lot_number"].tolist()

        if n < min_n:
            audit.log(
                action="cpk_skipped",
                inputs={"sku_id": sku, "supplier": supplier, "n": n, "min_n": min_n},
                outputs={"status": "insufficient_data"},
                rule_reference="URS-015",
            )
            results.append(CapabilityResult(
                sku_id=sku, supplier_name=supplier, n=n,
                mean=float(np.mean(vals)), std_within=0, std_overall=0,
                cpk=float("nan"), ppk=float("nan"),
                status=f"INSUFFICIENT DATA (n={n}, min={min_n})",
            ))
            continue

        mean = float(np.mean(vals))
        std_overall = float(np.std(vals, ddof=1))

        # Within-subgroup σ via moving range
        mr = np.abs(np.diff(vals))
        mr_bar = float(np.mean(mr))
        std_within = mr_bar / d2

        cpk = _cpk(mean, std_within, usl, lsl)
        ppk = _cpk(mean, std_overall, usl, lsl)

        if cpk < oos_thresh:
            status = STATUS_OOS
            alert = DeviationAlert(
                alert_type="CPK_OOS",
                sku_id=sku,
                supplier_name=supplier,
                metric="Cpk",
                value=round(cpk, 3),
                criterion=f"≥ {oos_thresh}",
                lot_numbers=lot_nums,
                regulatory_ref=citation,
            )
            alerts.append(alert)
        elif cpk < marg_thresh:
            status = STATUS_MARGINAL
            alert = None
        else:
            status = STATUS_CAPABLE
            alert = None

        audit.log(
            action="cpk_calculation",
            inputs={"sku_id": sku, "supplier": supplier, "n": n, "usl": usl, "lsl": lsl},
            outputs={"cpk": round(cpk, 4), "ppk": round(ppk, 4), "status": status},
            rule_reference=citation,
        )

        results.append(CapabilityResult(
            sku_id=sku, supplier_name=supplier, n=n,
            mean=round(mean, 4), std_within=round(std_within, 4),
            std_overall=round(std_overall, 4),
            cpk=round(cpk, 3), ppk=round(ppk, 3),
            status=status,
            alert=alert.alert_type if alert else None,
        ))

    return results, alerts
