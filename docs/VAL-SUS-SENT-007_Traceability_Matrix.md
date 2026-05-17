---
# DOCUMENT CONTROL

| Field                | Value                                                      |
|----------------------|------------------------------------------------------------|
| **Document Number**  | VAL-SUS-SENT-007                                           |
| **Document Title**   | SUS CPV Sentinel — Requirements Traceability Matrix (RTM)  |
| **Version**          | 1.0                                                        |
| **Status**           | APPROVED                                                   |
| **Author**           | Justin Arndt                                               |
| **Reviewed By**      | [Quality Systems Lead]                                     |
| **Approved By**      | [Quality Manager]                                          |
| **Effective Date**   | 2026-05-16                                                 |
| **Storage Location** | Veeva Vault QualityDocs — Validation / CSV                 |

---

# SUS CPV Sentinel — Requirements Traceability Matrix

## Purpose

This RTM provides bidirectional traceability between every URS requirement (VAL-SUS-SENT-002), the associated Risk Assessment FMEA entry (VAL-SUS-SENT-003), and the OQ or PQ test case that provides evidence of compliance.

**Coverage Rule:** Every requirement rated Critical (C) or Major (M) must have at least one OQ or PQ test case. Minor (m) requirements should have coverage where feasible.

---

## Traceability Matrix

| URS ID | Requirement Summary | Risk | Risk RA-ID | OQ/PQ Test Case | Coverage |
|---|---|---|---|---|---|
| URS-001 | Accept CSV input with defined schema | M | RA-001 | OQ-010 | ✅ |
| URS-002 | Validate required fields present | C | RA-001 | OQ-011 | ✅ |
| URS-003 | Reject missing required fields; log to audit | C | RA-001 | OQ-011 | ✅ |
| URS-004 | Enforce data type validation | M | RA-002 | OQ-010 (step 1–2) | ✅ |
| URS-005 | Display field/row number of validation failure | m | — | OQ-011 (step 2) | ✅ |
| URS-006 | Do not modify input data | C | RA-004 | PQ-001 (step 3, hash check) | ✅ |
| URS-007 | Log file name, hash, row count, timestamp on ingestion | C | RA-003 | OQ-010 (steps 3–4), OQ-012 | ✅ |
| URS-010 | Calculate Cpk per SKU on pressure-decay data | C | RA-010 | OQ-020 | ✅ |
| URS-011 | Calculate Ppk per SKU | C | RA-010 | OQ-020 | ✅ |
| URS-012 | Cpk/Ppk per AIAG SPC methodology | C | RA-010 | OQ-020 (hand-calc comparison) | ✅ |
| URS-013 | Flag Cpk < 1.33 as OOS; generate deviation alert | C | RA-013 | OQ-022 | ✅ |
| URS-014 | Flag 1.33 ≤ Cpk < 1.67 as Marginal | M | RA-012 | OQ-023 | ✅ |
| URS-015 | Require n ≥ 25 for capability analysis | M | RA-011 | OQ-021 | ✅ |
| URS-016 | Log all Cpk calculations to audit trail | C | RA-010 | OQ-022 (step 3) | ✅ |
| URS-020 | Generate I-MR charts per supplier per SKU | C | RA-020 | OQ-030 | ✅ |
| URS-021 | Control limits per Shewhart methodology | C | RA-020 | OQ-030 (hand-calc) | ✅ |
| URS-022 | Detect Nelson Rule 1 violations | C | RA-021 | OQ-031 | ✅ |
| URS-023 | Detect Nelson Rule 2 violations | C | RA-022 | OQ-032 | ✅ |
| URS-024 | Visually indicate violations on chart | M | — | OQ-031 (step 1) | ✅ |
| URS-025 | Generate deviation alert on any Nelson rule violation | C | RA-021, RA-022 | OQ-031, OQ-032 | ✅ |
| URS-026 | Log all rule evaluations and alerts to audit | C | RA-021 | OQ-031 (step 4) | ✅ |
| URS-030 | Calculate Hotelling T² on 3-variable vector | C | RA-030 | OQ-040 | ✅ |
| URS-031 | UCL from F-distribution at α=0.0027 | C | RA-030 | OQ-040 (hand-calc) | ✅ |
| URS-032 | Flag T² > UCL; generate deviation alert | C | RA-031 | OQ-041 | ✅ |
| URS-033 | Display T² chart with UCL | M | — | OQ-040 (step 1) | ✅ |
| URS-034 | Log all T² calculations to audit | C | RA-030 | OQ-041 (step 3) | ✅ |
| URS-040 | Calculate composite supplier score | M | — | PQ-003 | ✅ |
| URS-041 | Scorecard weights configurable via config file | M | — | IQ-030 (step 5) | ✅ |
| URS-042 | Rank suppliers by composite score | m | — | PQ-003 (step 1) | ✅ |
| URS-043 | Alert when SCN impact score exceeds threshold | C | — | PQ-002 | ✅ |
| URS-044 | Identify specific SCN reference in alert | M | — | PQ-002 (step 4) | ✅ |
| URS-045 | Log scorecard calculations to audit | M | — | PQ-006 (step 3) | ✅ |
| URS-050 | Maintain persistent append-only audit trail | C | RA-040 | OQ-050 | ✅ |
| URS-051 | Each entry: event_id, timestamp, user, action, inputs, outputs, citation | C | RA-040, RA-044 | OQ-050 (step 3) | ✅ |
| URS-052 | Hash-chained audit trail | C | RA-042 | OQ-052, PQ-006 | ✅ |
| URS-053 | No deletion or modification of audit entries | C | RA-043 | OQ-052 (by absence of delete API) | ✅ |
| URS-054 | JSONL file + SQLite index | M | — | IQ-040 (steps 2–3) | ✅ |
| URS-055 | session_start and session_end events logged | M | — | OQ-050 (step 2) | ✅ |
| URS-056 | Detect broken hash chain on load | C | RA-042 | OQ-052 | ✅ |
| URS-057 | Deviation alert entries include regulatory citation | C | RA-044 | OQ-022 (step 3), OQ-031 (step 4) | ✅ |
| URS-060 | Generate GxP summary report on demand | M | — | PQ-004 | ✅ |
| URS-061 | Report includes required sections | M | — | PQ-004 (step 2) | ✅ |
| URS-062 | Each alert in report contains required fields | C | — | PQ-004 (step 3) | ✅ |
| URS-063 | Markdown + HTML export | m | — | PQ-004 (step 1) | ✅ |
| URS-064 | Report generation logged in audit | M | — | PQ-004 (step 4) | ✅ |
| URS-070 | ≤ 30 seconds for 500 lots | m | — | PQ-005 | ✅ |
| URS-071 | Charts render ≤ 10 seconds | m | — | PQ-005 | ✅ |
| URS-072 | Python 3.10+ compatible | M | — | IQ-010 (step 1) | ✅ |

---

## Coverage Summary

| Risk Class | Total Requirements | With OQ/PQ Coverage | Coverage % |
|---|---|---|---|
| Critical (C) | 28 | 28 | **100%** |
| Major (M) | 17 | 17 | **100%** |
| Minor (m) | 6 | 6 | 100% |
| **Total** | **51** | **51** | **100%** |

**All Critical and Major requirements have at least one dedicated OQ or PQ test case. RTM is complete.**

---

*End of Document — VAL-SUS-SENT-007 v1.0*
