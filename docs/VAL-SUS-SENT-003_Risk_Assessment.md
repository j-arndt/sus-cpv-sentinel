---
# DOCUMENT CONTROL

| Field                | Value                                                      |
|----------------------|------------------------------------------------------------|
| **Document Number**  | VAL-SUS-SENT-003                                           |
| **Document Title**   | SUS CPV Sentinel — Risk Assessment                         |
| **Version**          | 1.0                                                        |
| **Status**           | APPROVED                                                   |
| **System**           | SUS CPV Sentinel v1.0                                      |
| **Author**           | Justin Arndt                                               |
| **Reviewed By**      | [Quality Systems Lead]                                     |
| **Approved By**      | [Quality Manager]                                          |
| **Effective Date**   | 2026-05-16                                                 |
| **Review Date**      | 2028-05-16                                                 |
| **Storage Location** | Veeva Vault QualityDocs — Validation / CSV                 |

---

# SUS CPV Sentinel — Risk Assessment

## 1. Purpose and Methodology

This Risk Assessment identifies potential failure modes of SUS CPV Sentinel v1.0 and evaluates their impact on product quality, patient safety, and data integrity. The assessment follows the Failure Mode and Effects Analysis (FMEA) methodology per **ICH Q9(R1) — Quality Risk Management** and **GAMP 5 Second Edition Appendix M2**.

### Risk Scoring

Each failure mode is scored on three dimensions (1–5 scale):

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| **Severity (S)** | No impact | Moderate quality/compliance impact | Direct patient safety or critical data integrity impact |
| **Probability (P)** | Very unlikely | Occasional | Likely without controls |
| **Detectability (D)** | Immediately obvious | Detectable with testing | May not be detected |

**Risk Priority Number (RPN) = S × P × D**

| RPN Range | Risk Level | Required Action |
|---|---|---|
| 1–8 | Low | Accept; monitor |
| 9–27 | Medium | Mitigate; include OQ test case |
| 28–75 | High | Mandatory mitigation before release; dedicated OQ/PQ test case |
| 76–125 | Critical | System must not be released until mitigated to Medium or below |

---

## 2. FMEA Table

### 2.1 Data Ingestion Module (`ingest.py`)

| ID | Failure Mode | Effect | S | P | D | RPN | Risk | Mitigation | Residual Risk |
|---|---|---|---|---|---|---|---|---|---|
| RA-001 | Missing required field not detected | Invalid/incomplete lot record processed; incorrect CPV conclusions | 5 | 2 | 2 | 20 | Medium | URS-002: Schema validation rejects records with missing required fields; logged to audit trail | Low |
| RA-002 | Incorrect data type accepted (e.g., text in numeric field) | Statistical calculation error; incorrect Cpk/Ppk | 5 | 2 | 2 | 20 | Medium | URS-004: Type validation enforced at ingestion; OQ-010 tests boundary conditions | Low |
| RA-003 | Input file silently truncated | Subset of lots analysed without user awareness; incorrect CPV conclusion | 5 | 2 | 3 | 30 | High | URS-007: Row count logged in audit trail; OQ-011 verifies count matches source | Medium |
| RA-004 | Input data modified during processing | Data integrity violation; ALCOA+ breach | 5 | 1 | 2 | 10 | Medium | URS-006: Read-only processing; no write-back to source; PQ-001 verifies with hash check | Low |

### 2.2 Integrity Test Capability Analysis (`integrity_cpk.py`)

| ID | Failure Mode | Effect | S | P | D | RPN | Risk | Mitigation | Residual Risk |
|---|---|---|---|---|---|---|---|---|---|
| RA-010 | Cpk calculated with incorrect USL/LSL | False compliance or false OOS signal | 5 | 2 | 2 | 20 | Medium | Spec limits defined in config file; OQ-020 verifies calculation against hand-calculated reference | Low |
| RA-011 | Cpk calculated with n < 25 lots | Unreliable capability estimate used for decision | 4 | 3 | 2 | 24 | Medium | URS-015: System warns and excludes SKU if n < 25; OQ-021 tests minimum sample enforcement | Low |
| RA-012 | Marginal SKU (1.33 ≤ Cpk < 1.67) not flagged for monitoring | Missing signal; increasing risk undetected | 4 | 2 | 3 | 24 | Medium | URS-014: Marginal flag logic; OQ-022 uses boundary-condition dataset | Low |
| RA-013 | OOS SKU (Cpk < 1.33) deviation alert not generated | Failed batch of SUS lots used without investigation | 5 | 1 | 2 | 10 | Medium | URS-013: Alert generation mandatory; OQ-023 verifies with planted OOS dataset | Low |

### 2.3 E&L Shewhart Control Charts (`el_shewhart.py`)

| ID | Failure Mode | Effect | S | P | D | RPN | Risk | Mitigation | Residual Risk |
|---|---|---|---|---|---|---|---|---|---|
| RA-020 | Control limits calculated incorrectly | False alarms or missed real shifts | 5 | 2 | 2 | 20 | Medium | OQ-030 verifies I-MR limits against AIAG SPC reference manual calculation | Low |
| RA-021 | Nelson Rule 1 violation not detected | Resin shift or E&L spike missed | 5 | 2 | 2 | 20 | Medium | OQ-031 uses planted Rule 1 violation; verifies alert generated | Low |
| RA-022 | Nelson Rule 2 violation not detected | Gradual trend missed | 4 | 2 | 3 | 24 | Medium | OQ-032 uses planted 9-consecutive-point run; verifies alert generated | Low |
| RA-023 | Alert generated but not linked to correct lot numbers | Investigation targets wrong lots | 4 | 2 | 2 | 16 | Medium | OQ-033 verifies lot number list in alert matches planted violation lots | Low |

### 2.4 Hotelling T² Multivariate Monitor (`hotelling_t2.py`)

| ID | Failure Mode | Effect | S | P | D | RPN | Risk | Mitigation | Residual Risk |
|---|---|---|---|---|---|---|---|---|---|
| RA-030 | T² UCL calculated at wrong alpha | Excessive false alarms or missed signals | 4 | 2 | 3 | 24 | Medium | OQ-040 verifies UCL against reference calculation (F-distribution, α=0.0027, p=3 variables) | Low |
| RA-031 | Out-of-control observation not flagged | Multivariate drift not detected | 5 | 2 | 2 | 20 | Medium | OQ-041 uses planted out-of-control observation; verifies alert | Low |
| RA-032 | Covariance matrix computed on insufficient data | Unreliable UCL | 4 | 2 | 2 | 16 | Medium | Minimum 30 observations required; URS-030 enforced in code; OQ-042 tests | Low |

### 2.5 Audit Trail (`audit_trail.py`)

| ID | Failure Mode | Effect | S | P | D | RPN | Risk | Mitigation | Residual Risk |
|---|---|---|---|---|---|---|---|---|---|
| RA-040 | Audit trail entry not written for a system action | ALCOA+ breach; regulatory non-compliance | 5 | 2 | 3 | 30 | **High** | URS-050: All actions instrumented; OQ-050 exhaustively tests each action type produces an entry | Medium |
| RA-041 | Timestamp incorrect or absent | ALCOA+ Contemporaneous attribute violated | 5 | 1 | 2 | 10 | Medium | Timestamps sourced from `datetime.utcnow()`; OQ-051 verifies timestamp format and proximity | Low |
| RA-042 | Hash chain broken without detection | Tampered audit trail accepted as valid | 5 | 1 | 1 | 5 | Low | URS-056: Hash chain verification on load; OQ-052 plants a tampered entry and verifies error raised | Low |
| RA-043 | Audit trail entry deleted | ALCOA+ Enduring attribute violated | 5 | 1 | 1 | 5 | Low | Append-only file; no delete function exposed; OQ-053 confirms no delete API exists | Low |
| RA-044 | Regulatory citation missing from deviation alert entry | Alert cannot be cross-referenced to standard | 3 | 2 | 3 | 18 | Medium | URS-057: Citation required field; OQ-054 verifies citation present in all alert entries | Low |

### 2.6 Streamlit Application (`app.py`)

| ID | Failure Mode | Effect | S | P | D | RPN | Risk | Mitigation | Residual Risk |
|---|---|---|---|---|---|---|---|---|---|
| RA-050 | Chart renders incorrect data | User makes decisions on wrong visualisation | 4 | 2 | 2 | 16 | Medium | PQ-010 verifies chart values against known dataset; user can inspect underlying data table | Low |
| RA-051 | Session data persists between users in multi-user deployment | Data confusion; potential privacy issue | 3 | 3 | 2 | 18 | Medium | Streamlit session state scoped per session; PQ-011 tests with two concurrent sessions | Low |

---

## 3. Pre-Release Risk Summary

| Risk Level | Count at Assessment | Count After Mitigation |
|---|---|---|
| Critical (76–125) | 0 | 0 |
| High (28–75) | 2 (RA-003, RA-040) | 0 (reduced to Medium) |
| Medium (9–27) | 14 | 16 (some Low elevated) |
| Low (1–8) | 1 | 1 |

**Conclusion:** No critical risks identified. All high risks are mitigated to Medium through built-in controls and dedicated OQ/PQ test cases. System is approved for validation execution.

---

*End of Document — VAL-SUS-SENT-003 v1.0*
