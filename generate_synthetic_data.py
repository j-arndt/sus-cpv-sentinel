"""
generate_synthetic_data.py
Generates the 150-lot SUS synthetic dataset with planted SCN-CYT-2025-0114 event.
Run once: python generate_synthetic_data.py
Output: data/synthetic_sus_lots.csv
"""

import numpy as np
import pandas as pd
from pathlib import Path

RNG = np.random.default_rng(42)

# USL=3.5, LSL=0.5 mbar — baseline Cpk ~1.9, post-SCN Cpk ~0.87
USL = 3.5
LSL = 0.5

COMPOUNDS = ["DEHP", "BHT", "Irganox-1076"]


def make_lots():
    rows = []
    start_date = pd.Timestamp("2024-01-01")

    # Fixed supplier+SKU assignment per lot to ensure even distribution
    # and guaranteed Cytiva presence at lot 95
    supplier_cycle = [
        ("Sartorius Stedim", "Flexsafe-STR-200L"),
        ("Cytiva",           "Xcellerex-2000L"),
        ("Pall Corporation", "Allegro-3D-50L"),
        ("Sartorius Stedim", "Flexsafe-STR-50L"),
        ("Cytiva",           "Xcellerex-200L"),
        ("Pall Corporation", "Allegro-TFF-1m2"),
    ]

    for lot_num in range(1, 151):
        date = start_date + pd.Timedelta(days=lot_num * 3 + int(RNG.integers(-1, 2)))
        supplier, sku = supplier_cycle[(lot_num - 1) % len(supplier_cycle)]
        compound = COMPOUNDS[(lot_num - 1) % len(COMPOUNDS)]

        scn_ref = None
        scn_impact = None

        # Cytiva resin change: SCN filed at lot 96 (first Cytiva lot on/after 95)
        # Lots: Cytiva appears at positions 2,5,8,11... i.e. lot_num % 6 == 2 (1-indexed)
        # Cytiva lots: 2,5,8,11,...,92,95,98,101,...,149 (every 3rd when using 6-cycle)
        # Actually with 6-cycle: Cytiva at positions 2 and 5, so lots: 2,5,8,11,...
        # Let's just check supplier directly
        is_cytiva = supplier == "Cytiva"

        # SCN-CYT-2025-0114 planted at lot 95 (first Cytiva lot >= 95)
        # Cytiva lots with 6-cycle: 2,5,8,...,92,95,98,...
        if is_cytiva and lot_num == 95:
            scn_ref = "SCN-CYT-2025-0114"
            scn_impact = 4

        # Baseline: delta_p ~ N(1.8, 0.28), Cpk ~ 1.9
        # Post-SCN Cytiva (lots 95+): delta_p shifts to N(2.6, 0.55), Cpk ~ 0.87
        if is_cytiva and lot_num >= 95:
            mean_dp = 2.6 + (lot_num - 95) * 0.012   # gradual worsening
            std_dp = 0.55
            # E&L also drifts upward
            el_base = 0.38 + (lot_num - 94) * 0.007
        else:
            mean_dp = 1.8
            std_dp = 0.28
            el_base = 0.18

        delta_p = round(float(max(0.05, RNG.normal(mean_dp, std_dp))), 3)
        result = "FAIL" if delta_p > USL or delta_p < LSL else "PASS"
        temp = round(float(RNG.normal(20.5, 0.8)), 1)
        lot_age = int(RNG.integers(7, 90))
        el_val = round(float(RNG.normal(el_base, 0.025)), 4)
        coa = bool(RNG.random() > 0.03)

        rows.append({
            "lot_number":      f"{supplier[:3].upper()}-{lot_num:04d}",
            "sku_id":          sku,
            "supplier_name":   supplier,
            "test_date":       date.strftime("%Y-%m-%d"),
            "delta_p_mbar":    delta_p,
            "test_temp_c":     temp,
            "lot_age_days":    lot_age,
            "el_measurement":  el_val,
            "el_compound":     compound,
            "scn_reference":   scn_ref,
            "scn_impact_score": scn_impact,
            "coa_complete":    coa,
            "result":          result,
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    Path("data").mkdir(exist_ok=True)
    df = make_lots()
    df.to_csv("data/synthetic_sus_lots.csv", index=False)
    print(f"Generated {len(df)} lots -> data/synthetic_sus_lots.csv")
    cytiva = df[df["supplier_name"] == "Cytiva"]
    print(f"Cytiva lots: {len(cytiva)}")
    scn_lots = df[df["scn_reference"].notna()]
    print(f"SCN lots: {len(scn_lots)} — {scn_lots['scn_reference'].tolist()}")
    fails = df[df["result"] == "FAIL"]
    print(f"FAIL results: {len(fails)}")
