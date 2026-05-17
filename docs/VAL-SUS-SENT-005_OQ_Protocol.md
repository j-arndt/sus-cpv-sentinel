---
# DOCUMENT CONTROL

| Field                | Value                                                      |
|----------------------|------------------------------------------------------------|
| **Document Number**  | VAL-SUS-SENT-005                                           |
| **Document Title**   | SUS CPV Sentinel — OQ Protocol & Report                    |
| **Version**          | 1.0                                                        |
| **Status**           | APPROVED                                                   |
| **System**           | SUS CPV Sentinel v1.0                                      |
| **Execution Platform** | Kneat Gx — Project KNEAT-SUS-SENT-2026-001              |
| **Author**           | Justin Arndt                                               |
| **Reviewed By**      | [Quality Systems Lead]                                     |
| **Approved By**      | [Quality Manager]                                          |
| **Effective Date**   | 2026-05-16                                                 |
| **Storage Location** | Veeva Vault QualityDocs — Validation / CSV                 |

---

# SUS CPV Sentinel — Operational Qualification Protocol

## 1. Purpose and Scope

This OQ Protocol verifies that SUS CPV Sentinel v1.0 operates per its URS (VAL-SUS-SENT-002) across the full range of intended operational conditions, including boundary conditions and planted failure scenarios.

**Prerequisite:** IQ (VAL-SUS-SENT-004) must be completed with all test cases Passed or Deviations closed.

**Execution:** All test cases are executed and recorded in **Kneat Gx**, Project KNEAT-SUS-SENT-2026-001. Electronic signatures and evidence attachments are captured in Kneat. This document is the authored protocol; the Kneat execution record is the primary evidence of execution.

---

## 2. Reference Test Datasets

All datasets are synthetic. Files are version-controlled under `tests/fixtures/`.

| ID | File | Contents | Purpose |
|---|---|---|---|
| DS-001 | `oq_clean_150lots.csv` | 150 lots, 3 suppliers, 4 SKUs, all passing | Baseline testing |
| DS-002 | `oq_missing_fields.csv` | DS-001 with 5 rows missing required fields | Schema validation |
| DS-003 | `oq_oos_cpk.csv` | Cytiva Flexsafe-STR-200L shifted to Cpk=0.87 | OOS alert testing |
| DS-004 | `oq_marginal_cpk.csv` | Pall Allegro-3D-50L at Cpk=1.45 | Marginal flag testing |
| DS-005 | `oq_nelson_rule1.csv` | DS-001 with planted Rule 1 violation at lot 87 | Nelson R1 detection |
| DS-006 | `oq_nelson_rule2.csv` | 9 consecutive Sartorius lots below centreline | Nelson R2 detection |
| DS-007 | `oq_hotelling_oos.csv` | T²=18.4 planted at lot 112 (UCL=14.2) | T² OOC detection |
| DS-008 | `oq_scn_trigger.csv` | SCN-CYT-2025-0114 with impact_score=5 | SCN alert detection |
| DS-009 | `oq_tampered_audit.jsonl` | Valid audit trail with entry 42 hash corrupted | Tamper detection |
| DS-010 | `oq_n_less_25.csv` | 18 lots for one SKU only | Minimum n enforcement |

---

## 3. Test Cases

### OQ-010 — Valid Dataset Ingestion
**URS:** URS-001, URS-007 | **Risk:** RA-001

| Step | Action | Expected Result | Actual Result | P/F |
|---|---|---|---|---|
| 1 | Load DS-001 via file upload | Accepted without error | | |
| 2 | Observe status message | "150 records loaded successfully" | | |
| 3 | Open Audit Trail viewer | Entry present: file name, SHA-256 hash, row_count=150, UTC timestamp | | |
| 4 | Verify hash matches DS-001 | SHA-256 in audit entry matches independent hash of file | | |

---

### OQ-011 — Missing Required Field Rejection
**URS:** URS-002, URS-003 | **Risk:** RA-001

| Step | Action | Expected Result | Actual Result | P/F |
|---|---|---|---|---|
| 1 | Load DS-002 | Error message identifying rows and fields with missing values | | |
| 2 | Verify all 5 rejected rows listed | All 5 rows identified by row number and field name | | |
| 3 | Confirm no analysis proceeds | No CPV charts or scores displayed | | |
| 4 | Check audit trail | Rejection event recorded with row numbers and field names | | |

---

### OQ-020 — Cpk Calculation Accuracy
**URS:** URS-010, URS-012 | **Risk:** RA-010
**Config:** USL=3.5 mbar, LSL=0.5 mbar

| Step | Action | Expected Result | Actual Result | P/F |
|---|---|---|---|---|
| 1 | Load DS-001; navigate to Capability Analysis | Cpk values displayed per SKU | | |
| 2 | Record system Cpk for "Sartorius-Flexsafe-STR-200L" | Value recorded: _______ | | |
| 3 | Hand-calculate Cpk from DS-001 for that SKU | Hand-calc: _______ | | |
| 4 | Compare | Difference ≤ 0.01 | | |

---

### OQ-021 — Minimum n Enforcement
**URS:** URS-015 | **Risk:** RA-011

| Step | Action | Expected Result | Actual Result | P/F |
|---|---|---|---|---|
| 1 | Load DS-010 | "Pall-Allegro-TFF-1m2" shows warning: "n=18, minimum 25 required" | | |
| 2 | Verify SKU excluded from summary | Not present in capability ranking table | | |

---

### OQ-022 — OOS Cpk Deviation Alert
**URS:** URS-013 | **Risk:** RA-013

| Step | Action | Expected Result | Actual Result | P/F |
|---|---|---|---|---|
| 1 | Load DS-003; navigate to Capability | "Cytiva-Flexsafe-STR-200L" flagged OUT OF SPECIFICATION | | |
| 2 | Check Deviation Alerts panel | Alert listing: SKU, Cpk=0.87, criterion ≥1.33, supplier=Cytiva | | |
| 3 | Check audit trail | Entry with Cpk value, USL, LSL, ASTM E3244-23 citation | | |

---

### OQ-023 — Marginal Cpk Flag
**URS:** URS-014 | **Risk:** RA-012

| Step | Action | Expected Result | Actual Result | P/F |
|---|---|---|---|---|
| 1 | Load DS-004 | "Pall-Allegro-3D-50L" flagged MARGINAL — MONITOR (amber) | | |
| 2 | Verify not listed as OOS | Not in OOS Deviation Alerts | | |

---

### OQ-030 — Shewhart Control Limit Accuracy
**URS:** URS-021 | **Risk:** RA-020

| Step | Action | Expected Result | Actual Result | P/F |
|---|---|---|---|---|
| 1 | Load DS-001; navigate to E&L chart for Sartorius | I-MR chart with UCL, LCL, centreline | | |
| 2 | Record system UCL | Value: _______ | | |
| 3 | Hand-calculate UCL = X̄ + 3×(R̄/d₂) from DS-001 | Value: _______ | | |
| 4 | Compare | Difference ≤ 0.001 | | |

---

### OQ-031 — Nelson Rule 1 Detection
**URS:** URS-022, URS-025 | **Risk:** RA-021

| Step | Action | Expected Result | Actual Result | P/F |
|---|---|---|---|---|
| 1 | Load DS-005; navigate to E&L chart | Lot 87 marked as violation (red indicator) | | |
| 2 | Check Deviation Alerts | Alert: "Nelson Rule 1 — [lot 87 ID] — beyond ±3σ" | | |
| 3 | Verify correct lot in alert | Lot reference matches DS-005 planted lot | | |
| 4 | Check audit trail | Entry: lot number, measured value, UCL, PDA TR 66 citation | | |

---

### OQ-032 — Nelson Rule 2 Detection
**URS:** URS-023, URS-025 | **Risk:** RA-022

| Step | Action | Expected Result | Actual Result | P/F |
|---|---|---|---|---|
| 1 | Load DS-006; navigate to Sartorius E&L chart | Run of 9 visually indicated | | |
| 2 | Check Deviation Alerts | Alert: "Nelson Rule 2 — 9 consecutive below centreline — Sartorius" | | |
| 3 | Verify all 9 lot numbers listed in alert | All 9 from planted run present | | |

---

### OQ-040 — Hotelling T² UCL Accuracy
**URS:** URS-031 | **Risk:** RA-030

| Step | Action | Expected Result | Actual Result | P/F |
|---|---|---|---|---|
| 1 | Load DS-001; navigate to T² chart | Chart with UCL displayed | | |
| 2 | Record system UCL | Value: _______ | | |
| 3 | Hand-calculate UCL via F-dist (p=3, n=150, α=0.0027) | Value: _______ | | |
| 4 | Compare | Difference ≤ 0.05 | | |

---

### OQ-041 — Hotelling T² OOC Detection
**URS:** URS-032 | **Risk:** RA-031

| Step | Action | Expected Result | Actual Result | P/F |
|---|---|---|---|---|
| 1 | Load DS-007; navigate to T² chart | Lot 112 marked OOC | | |
| 2 | Check Deviation Alerts | Alert: "T²=18.4 exceeds UCL=14.2 — Lot [112 ID]" | | |
| 3 | Check audit trail | Entry with T² value, UCL, input vector, lot reference | | |

---

### OQ-050 — Audit Trail Completeness
**URS:** URS-050, URS-051 | **Risk:** RA-040

| Step | Action | Expected Result | Actual Result | P/F |
|---|---|---|---|---|
| 1 | Run full analysis session with DS-001; export audit trail | JSONL file downloaded | | |
| 2 | Verify action types present | session_start, file_ingestion, cpk_calculation, shewhart_calculation, t2_calculation, scorecard_calculation, report_generation, session_end all present | | |
| 3 | Verify each entry has required fields | event_id, timestamp_utc, user, action, inputs, outputs, rule_reference in every entry | | |

---

### OQ-052 — Audit Trail Tamper Detection
**URS:** URS-056 | **Risk:** RA-042

| Step | Action | Expected Result | Actual Result | P/F |
|---|---|---|---|---|
| 1 | Load DS-009 as audit trail | Error: "Audit trail integrity failed — hash chain broken at entry 42" | | |
| 2 | Verify tampered data not displayed as valid | No records from tampered trail shown as valid | | |

---

## 4. OQ Summary

| Module | Cases | Passed | Deviations |
|---|---|---|---|
| Ingestion | 2 | | |
| Cpk/Ppk | 4 | | |
| Shewhart | 3 | | |
| Hotelling T² | 2 | | |
| Audit Trail | 2 | | |
| **Total** | **13** | | |

**OQ Outcome:** ☐ PASSED — proceed to PQ &nbsp;&nbsp; ☐ FAILED — resolve deviations

| Role | Name | Kneat Gx Signature | Date |
|---|---|---|---|
| Protocol Executor | | [Kneat record] | |
| QA Reviewer | | [Kneat record] | |

---

*End of Document — VAL-SUS-SENT-005 v1.0*
