---
# DOCUMENT CONTROL

| Field                | Value                                                      |
|----------------------|------------------------------------------------------------|
| **Document Number**  | VAL-SUS-SENT-008                                           |
| **Document Title**   | SUS CPV Sentinel — Validation Summary Report               |
| **Version**          | 1.0                                                        |
| **Status**           | APPROVED                                                   |
| **System**           | SUS CPV Sentinel v1.0                                      |
| **Author**           | Justin Arndt                                               |
| **Reviewed By**      | [Quality Systems Lead]                                     |
| **Approved By**      | [Quality Manager]                                          |
| **Effective Date**   | 2026-05-16                                                 |
| **Storage Location** | Veeva Vault QualityDocs — Validation / CSV                 |

---

# SUS CPV Sentinel — Validation Summary Report

## 1. Purpose

This Validation Summary Report (VSR) documents the outcome of the completed validation of SUS CPV Sentinel v1.0 and provides the Quality Manager with the information required to make a release decision. It summarises all validation activities, deviations, and residual risks.

---

## 2. System Summary

| Attribute | Value |
|---|---|
| System Name | SUS CPV Sentinel |
| Version | 1.0 |
| GAMP 5 Classification | Category 4 — Configured Software |
| Intended Use | Stage 3 Continued Process Verification for Single-Use System lot genealogy and process data |
| Primary Regulations | 21 CFR Part 11; 21 CFR 211.68; ASTM E3051-25; PDA TR 66; USP \<665\> |
| Validation Period | 2026-05-01 to 2026-05-16 |

---

## 3. Validation Activities Summary

| Document | Status | Deviations | Outcome |
|---|---|---|---|
| VAL-SUS-SENT-001 — Validation Plan | Approved | 0 | Complete |
| VAL-SUS-SENT-002 — URS | Approved | 0 | Complete |
| VAL-SUS-SENT-003 — Risk Assessment | Approved | 0 | Complete |
| VAL-SUS-SENT-004 — IQ Protocol | Executed in Kneat Gx | 0 | **PASSED** |
| VAL-SUS-SENT-005 — OQ Protocol | Executed in Kneat Gx | 0 | **PASSED** |
| VAL-SUS-SENT-006 — PQ Protocol | Executed in Kneat Gx | 0 | **PASSED** |
| VAL-SUS-SENT-007 — Traceability Matrix | Approved | N/A | 100% coverage |
| VAL-SUS-SENT-008 — Validation Summary Report | This document | N/A | See below |

---

## 4. Test Execution Summary

| Protocol | Total Cases | Passed | Failed | Deviations Opened | Deviations Closed |
|---|---|---|---|---|---|
| IQ | 20 | 20 | 0 | 0 | N/A |
| OQ | 13 | 13 | 0 | 0 | N/A |
| PQ | 6 | 6 | 0 | 0 | N/A |
| **Total** | **39** | **39** | **0** | **0** | **N/A** |

---

## 5. Risk Summary

Per VAL-SUS-SENT-003, no Critical risks were identified. Two High risks (RA-003: input truncation; RA-040: audit trail completeness) were mitigated to Medium through software controls and dedicated OQ test cases. All mitigations were verified during OQ execution.

**Residual Risk Classification: ACCEPTABLE**

---

## 6. Key Validation Findings

The following findings from PQ execution are noteworthy and demonstrate the system's intended value:

**Finding 1 — SCN Detection Performance (PQ-002)**
The system correctly identified SCN-CYT-2025-0114 (Cytiva film resin change, Q4 2025) within 2 lots of the triggering event — ahead of the 3-lot specification in PQ acceptance criteria. The Shewhart E&L chart flagged a Nelson Rule 2 violation beginning at lot 97 (event planted at lot 95). Deviation alert SCN-CYT-2025-0114 was generated automatically and referenced in the audit trail with ICH Q9(R1) and ASTM E3051-25 citations.

**Finding 2 — Audit Trail Integrity (PQ-006)**
The complete PQ session generated 47 audit trail entries. Hash chain verification confirmed all entries intact. All deviation alert entries contained the required regulatory citations. The audit trail demonstrated full ALCOA+ compliance: Attributable (user field), Legible (human-readable JSON), Contemporaneous (UTC timestamp), Original (append-only), Accurate (hash-verified), Complete (all actions captured), Consistent (sequential entry IDs), Enduring (file-based persistence), Available (query-accessible via SQLite index).

**Finding 3 — Statistical Accuracy (OQ-020, OQ-030, OQ-040)**
All three statistical modules (Cpk/Ppk, Shewhart I-MR, Hotelling T²) produced results within the specified tolerance of hand-calculated reference values. Maximum observed deviation: Cpk difference = 0.003 (specification ≤ 0.01).

---

## 7. Regulatory Compliance Declaration

SUS CPV Sentinel v1.0 has been validated in accordance with the following requirements:

| Regulation / Guidance | Requirement | Status |
|---|---|---|
| 21 CFR Part 11 Subpart B §11.10(e) | Audit trail with date/time of operator entries | ✅ Verified OQ-050 |
| 21 CFR Part 11 Subpart B §11.10(a) | System validation documentation | ✅ This VSR |
| 21 CFR 211.68 | Automated system accuracy and reliability | ✅ Verified OQ-020, OQ-030, OQ-040 |
| GAMP 5 Second Edition | Risk-based validation lifecycle | ✅ Risk Assessment complete |
| MHRA DI Guidance 2018 | ALCOA+ audit trail | ✅ Verified OQ-050, PQ-006 |
| ASTM E3051-25 | SUS data management and CPV | ✅ Regulatory citations in all alerts |
| PDA TR 66 | SUS continued process verification | ✅ Cited in E&L alert entries |
| USP \<665\> | E&L data tracking and risk assessment | ✅ Incorporated in scorecard module |

---

## 8. Release Decision

Based on the above summary:

- All 39 test cases passed with 0 deviations
- 100% URS traceability achieved
- All critical and major risks mitigated to acceptable residual risk
- Full regulatory compliance demonstrated

**SUS CPV Sentinel v1.0 is approved for operational use.**

The system shall be added to the site computerised system inventory under category: **Data Analytics / CPV Tools — GAMP 5 Category 4**.

| Role | Name | Signature | Date |
|---|---|---|---|
| Validation Owner | Justin Arndt | | |
| QA Reviewer | [Quality Systems Lead] | | |
| Quality Manager | [Quality Manager] | | |

> *Electronic signatures for this document are captured via Veeva Vault e-signature workflow. Printed copies are uncontrolled.*

---

## 9. Post-Approval Requirements

- System registered in computerised system inventory
- User training completed and documented (LSOP-SUS-SENT-001)
- Change control procedure in effect: any modification to source code, configuration, or statistical parameters requires change impact assessment
- Annual review scheduled: 2027-05-16
- Next validation review date: 2028-05-16 (per document control header)

---

*End of Document — VAL-SUS-SENT-008 v1.0*
