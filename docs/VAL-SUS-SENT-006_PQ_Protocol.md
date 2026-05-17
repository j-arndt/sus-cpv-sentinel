---
# DOCUMENT CONTROL

| Field                | Value                                                      |
|----------------------|------------------------------------------------------------|
| **Document Number**  | VAL-SUS-SENT-006                                           |
| **Document Title**   | SUS CPV Sentinel — Performance Qualification Protocol & Report |
| **Version**          | 1.0                                                        |
| **Status**           | APPROVED                                                   |
| **Execution Platform** | Kneat Gx — Project KNEAT-SUS-SENT-2026-001              |
| **Author**           | Justin Arndt                                               |
| **Reviewed By**      | [Quality Systems Lead]                                     |
| **Approved By**      | [Quality Manager]                                          |
| **Effective Date**   | 2026-05-16                                                 |
| **Storage Location** | Veeva Vault QualityDocs — Validation / CSV                 |

---

# SUS CPV Sentinel — Performance Qualification Protocol

## 1. Purpose and Scope

This PQ Protocol demonstrates that SUS CPV Sentinel v1.0 consistently performs its intended function under realistic operational conditions using the full synthetic production dataset. PQ simulates how the system would be used by an MSAT data specialist during a routine Stage 3 CPV review.

**Prerequisite:** OQ (VAL-SUS-SENT-005) must be completed with all test cases Passed or Deviations closed.

**Execution:** Recorded in Kneat Gx, Project KNEAT-SUS-SENT-2026-001.

---

## 2. PQ Dataset

| File | `data/synthetic_sus_lots.csv` |
|---|---|
| Lots | 150 |
| Suppliers | 3 (Sartorius Stedim, Cytiva, Pall Corporation) |
| SKUs | 4 (Flexsafe-STR-200L, Xcellerex-2000L, Allegro-3D-50L, Allegro-TFF-1m2) |
| Date Range | 2024-01-01 to 2026-04-30 (18 months) |
| Planted Event | SCN-CYT-2025-0114 — Cytiva film resin change, Q4 2025; SCN impact score = 4 |
| Planted CPV Signal | Cytiva Flexsafe-STR-200L E&L values begin drifting above UCL from lot 95 onward |

The planted Cytiva resin change (SCN-CYT-2025-0114) reflects a realistic supplier change notification scenario. The system must detect the resulting process shift within 3 lots of the event without prior knowledge of the planting.

---

## 3. PQ Test Cases

### PQ-001 — Full Dataset Processing Without Error

| Step | Action | Expected Result | Actual Result | P/F |
|---|---|---|---|---|
| 1 | Load `synthetic_sus_lots.csv` | 150 records accepted; no schema errors | | |
| 2 | Complete full analysis (all modules) | All charts and scorecards rendered without runtime errors | | |
| 3 | Verify input file hash in audit trail | SHA-256 of production dataset recorded in audit trail entry | | |
| 4 | Confirm row count in audit trail | row_count = 150 in ingestion audit entry | | |

---

### PQ-002 — SCN-CYT-2025-0114 Detection

**Objective:** Verify the system detects the planted Cytiva resin change signal within 3 lots.

| Step | Action | Expected Result | Actual Result | P/F |
|---|---|---|---|---|
| 1 | Complete full analysis | Supplier scorecard rendered | | |
| 2 | Inspect Cytiva scorecard | SCN-CYT-2025-0114 identified with impact_score=4; SCN alert present | | |
| 3 | Inspect E&L Shewhart chart for Cytiva | Nelson rule violation or OOT signal visible beginning ≤ lot 98 (≤ 3 lots after lot 95) | | |
| 4 | Verify deviation alert references the SCN | Alert text includes "SCN-CYT-2025-0114" | | |
| 5 | Check audit trail | Alert entry includes SCN reference, lot numbers affected, and ICH Q9(R1) citation | | |

---

### PQ-003 — Supplier Ranking Consistency

| Step | Action | Expected Result | Actual Result | P/F |
|---|---|---|---|---|
| 1 | Review supplier scorecard after full analysis | Three suppliers ranked; Cytiva ranked lowest due to SCN event | | |
| 2 | Run analysis a second time with identical data | Supplier rankings identical to first run | | |
| 3 | Confirm deterministic output | Cpk, T², and scorecard values identical across both runs (deterministic) | | |

---

### PQ-004 — Report Generation

| Step | Action | Expected Result | Actual Result | P/F |
|---|---|---|---|---|
| 1 | Generate GxP summary report | Report file produced without error | | |
| 2 | Verify report contains required sections | Date/time of generation, data range, lot count, CPV status per SKU, active alerts, audit trail reference all present | | |
| 3 | Verify each deviation alert contains required fields | Alert ID, date detected, SKU, supplier, metric value, acceptance criterion, regulatory reference all present | | |
| 4 | Check audit trail | Report generation event logged with report file hash | | |

---

### PQ-005 — Performance Under Load

| Step | Action | Expected Result | Actual Result | P/F |
|---|---|---|---|---|
| 1 | Load full 150-lot dataset and run complete analysis | All calculations complete in ≤ 30 seconds (per URS-070) | | |
| 2 | Record actual elapsed time | Time: _______ seconds | | |

---

### PQ-006 — Audit Trail Integrity After Full PQ Session

| Step | Action | Expected Result | Actual Result | P/F |
|---|---|---|---|---|
| 1 | After completing PQ-001 through PQ-005, export audit trail | JSONL file exported | | |
| 2 | Run audit trail verification function | "Audit trail integrity verified — hash chain intact" message displayed | | |
| 3 | Count entries | Minimum entries present: 1 session_start + 1 ingestion + at minimum 5 calculation events + 1 report + 1 session_end = ≥ 10 entries | | |

---

## 4. PQ Summary

| Case | Description | Passed | Deviations |
|---|---|---|---|
| PQ-001 | Full dataset processing | | |
| PQ-002 | SCN-CYT-2025-0114 detection | | |
| PQ-003 | Supplier ranking consistency | | |
| PQ-004 | Report generation | | |
| PQ-005 | Performance | | |
| PQ-006 | Audit trail post-PQ integrity | | |
| **Total** | 6 cases | | |

**PQ Outcome:** ☐ PASSED — system qualified for operational use &nbsp;&nbsp; ☐ FAILED — resolve deviations

| Role | Name | Kneat Gx Signature | Date |
|---|---|---|---|
| Protocol Executor | | [Kneat record] | |
| QA Reviewer | | [Kneat record] | |
| System Owner | | [Kneat record] | |

---

*End of Document — VAL-SUS-SENT-006 v1.0*
