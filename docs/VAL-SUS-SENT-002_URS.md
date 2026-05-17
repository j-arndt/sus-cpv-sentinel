---
# DOCUMENT CONTROL

| Field                | Value                                                      |
|----------------------|------------------------------------------------------------|
| **Document Number**  | VAL-SUS-SENT-002                                           |
| **Document Title**   | SUS CPV Sentinel — User Requirements Specification (URS)   |
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

# SUS CPV Sentinel — User Requirements Specification

## 1. Purpose

This User Requirements Specification (URS) defines the functional, data integrity, audit trail, and performance requirements for SUS CPV Sentinel v1.0. All requirements herein are testable and shall be traced to OQ or PQ test cases in the Requirements Traceability Matrix (VAL-SUS-SENT-007).

Requirements are identified with a unique ID in the format **URS-XXX** and assigned a risk classification:
- **C** — Critical: Direct impact on product quality, patient safety, or data integrity
- **M** — Major: Significant impact on system function or regulatory compliance
- **m** — Minor: Desirable but not critical to core function

---

## 2. Data Ingestion Requirements

| ID | Requirement | Risk |
|---|---|---|
| URS-001 | The system shall accept SUS lot genealogy data in CSV format with a defined schema (see Section 6) | M |
| URS-002 | The system shall validate all required fields are present and non-null before processing | C |
| URS-003 | The system shall reject records where lot_number, sku_id, supplier_name, or test_date are missing, and log the rejection to the audit trail | C |
| URS-004 | The system shall enforce data type validation: numeric fields must be numeric; date fields must conform to ISO 8601 format | M |
| URS-005 | The system shall display a clear error message identifying the specific field and row number of any validation failure | m |
| URS-006 | The system shall not modify, overwrite, or delete input data at any point during processing | C |
| URS-007 | The system shall record the file name, file hash (SHA-256), row count, and ingestion timestamp in the audit trail upon successful ingestion | C |

---

## 3. Integrity Test Statistical Analysis Requirements (Cpk / Ppk)

| ID | Requirement | Risk |
|---|---|---|
| URS-010 | The system shall calculate process capability index Cpk for pressure-decay delta-P data, grouped by SUS SKU | C |
| URS-011 | The system shall calculate process performance index Ppk for pressure-decay delta-P data, grouped by SUS SKU | C |
| URS-012 | Cpk and Ppk shall be calculated using the formulae defined in AIAG Statistical Process Control (SPC) Reference Manual, aligned with USL/LSL specification limits defined in the system configuration | C |
| URS-013 | The system shall flag any SKU with Cpk \< 1.33 as **Out of Specification** and generate a deviation alert | C |
| URS-014 | The system shall flag any SKU with Cpk between 1.33 and 1.67 as **Marginal — Monitor** | M |
| URS-015 | The system shall require a minimum of 25 lot records per SKU to calculate a valid Cpk/Ppk; if fewer are available, the system shall display a warning and exclude that SKU from capability analysis | M |
| URS-016 | All Cpk/Ppk calculations, inputs, and outputs shall be logged to the audit trail with a reference to the applicable specification limit | C |

---

## 4. E&L Shewhart Control Chart Requirements

| ID | Requirement | Risk |
|---|---|---|
| URS-020 | The system shall generate Individuals (I) and Moving Range (MR) control charts for extractables/leachables (E&L) data per supplier per SUS SKU | C |
| URS-021 | Control limits shall be calculated as X̄ ± 3σ for the I chart, and D4 × R̄ for the MR chart upper control limit, per standard Shewhart methodology | C |
| URS-022 | The system shall detect and flag Nelson Rule 1 violations (one point beyond ±3σ) | C |
| URS-023 | The system shall detect and flag Nelson Rule 2 violations (nine consecutive points on the same side of the centreline) | C |
| URS-024 | The system shall visually indicate control limit violations on the chart with a distinct colour or symbol | M |
| URS-025 | Upon detection of any Nelson Rule violation, the system shall generate a deviation alert identifying: the rule violated, the lot number(s) involved, the supplier, and the SKU | C |
| URS-026 | All control limit calculations, rule evaluations, and alerts shall be recorded in the audit trail | C |

---

## 5. Hotelling T² Multivariate Control Requirements

| ID | Requirement | Risk |
|---|---|---|
| URS-030 | The system shall calculate Hotelling T² statistics for the multivariate vector comprising pressure-decay delta-P, contact temperature, and lot age at use | C |
| URS-031 | The upper control limit (UCL) for T² shall be calculated from the F-distribution at α = 0.0027 (equivalent to 3-sigma for univariate) | C |
| URS-032 | The system shall flag any observation exceeding the T² UCL as an out-of-control signal and generate a deviation alert | C |
| URS-033 | The system shall display a T² chart over time with UCL plotted | M |
| URS-034 | All T² calculations shall be logged in the audit trail with the input vector values and computed T² statistic | C |

---

## 6. Supplier Scorecard Requirements

| ID | Requirement | Risk |
|---|---|---|
| URS-040 | The system shall calculate a composite supplier performance score for each supplier based on: lot rejection rate, SCN frequency, SCN impact score, CoA completeness rate, and integrity test failure rate | M |
| URS-041 | The weighting of each scorecard component shall be configurable in the system configuration file; default weights shall be documented in the system configuration | M |
| URS-042 | The system shall rank suppliers from highest to lowest composite score | m |
| URS-043 | The system shall detect any supplier whose SCN impact score exceeds the configured threshold within a rolling 12-month window and generate an alert | C |
| URS-044 | The system shall identify the specific SCN event (by SCN reference number) that triggered any alert | M |
| URS-045 | All scorecard calculations shall be recorded in the audit trail | M |

---

## 7. Audit Trail Requirements (ALCOA+ / 21 CFR Part 11)

| ID | Requirement | Risk |
|---|---|---|
| URS-050 | The system shall maintain a persistent, append-only audit trail log for all system actions | C |
| URS-051 | Each audit trail entry shall contain: event_id (SHA-256 hash of entry content), timestamp_utc (ISO 8601), user identity, action type, input parameters, output results, and applicable regulatory citation | C |
| URS-052 | The audit trail shall be implemented as a hash-chained log: each entry's SHA-256 hash is recorded in the subsequent entry, enabling tamper detection | C |
| URS-053 | The system shall not permit deletion, modification, or overwriting of any audit trail entry | C |
| URS-054 | The audit trail shall be stored as a human-readable JSON-Lines file (.jsonl) with a secondary SQLite index for query performance | M |
| URS-055 | The audit trail shall record a session_start and session_end event for each user session | M |
| URS-056 | Any attempt to load a tampered audit trail file (hash chain broken) shall be detected and reported as an error | C |
| URS-057 | All audit trail entries involving a deviation alert shall include the specific regulatory reference (e.g., "ASTM E3244-23 §4.2") | C |

> **Regulatory basis:** 21 CFR Part 11 Subpart B §11.10(e) requires audit trails that capture date/time of operator entries and actions that create, modify, or delete electronic records. MHRA GxP Data Integrity Guidance (2018) requires audit trails to be ALCOA+: Attributable, Legible, Contemporaneous, Original, Accurate, Complete, Consistent, Enduring, Available.

---

## 8. Reporting Requirements

| ID | Requirement | Risk |
|---|---|---|
| URS-060 | The system shall generate a GxP-formatted summary report upon user request | M |
| URS-061 | The report shall include: date/time of report generation, data range analysed, number of lots processed, CPV status per SKU, list of active deviation alerts, and audit trail reference | M |
| URS-062 | Each deviation alert in the report shall include: alert ID, date detected, metric affected, lot number(s), supplier, SKU, statistical value, acceptance criterion, and regulatory reference | C |
| URS-063 | The report shall be generated in Markdown format with an HTML export option | m |
| URS-064 | Report generation shall be logged in the audit trail | M |

---

## 9. Performance Requirements

| ID | Requirement | Risk |
|---|---|---|
| URS-070 | The system shall complete all statistical calculations for a dataset of 500 lots within 30 seconds on standard laboratory hardware | m |
| URS-071 | The Streamlit interface shall render all charts within 10 seconds of data load | m |
| URS-072 | The system shall operate correctly on Python 3.10+ | M |

---

## 10. Input Data Schema

The system expects the following CSV schema for SUS lot genealogy data:

| Column | Data Type | Required | Description |
|---|---|---|---|
| `lot_number` | string | Yes | Supplier lot number (e.g., "CYT-2025-0114") |
| `sku_id` | string | Yes | SUS SKU identifier (e.g., "Flexsafe-STR-200L") |
| `supplier_name` | string | Yes | Supplier name (e.g., "Cytiva", "Sartorius", "Pall") |
| `test_date` | ISO 8601 date | Yes | Date of integrity test (YYYY-MM-DD) |
| `delta_p_mbar` | float | Yes | Pressure-decay delta-P in mbar |
| `test_temp_c` | float | Yes | Temperature at time of test in °C |
| `lot_age_days` | integer | Yes | Age of lot at time of use (days from manufacture) |
| `el_measurement` | float | No | E&L measurement value (compound-specific unit) |
| `el_compound` | string | No | Extractable compound identifier |
| `scn_reference` | string | No | Supplier Change Notification reference number |
| `scn_impact_score` | integer (1–5) | No | SCN impact score per change impact assessment |
| `coa_complete` | boolean | Yes | Whether CoA documentation is complete |
| `result` | string | Yes | Integrity test result: "PASS" or "FAIL" |

---

*End of Document — VAL-SUS-SENT-002 v1.0*
