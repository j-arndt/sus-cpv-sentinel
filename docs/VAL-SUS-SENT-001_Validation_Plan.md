---
# DOCUMENT CONTROL

| Field                | Value                                                      |
|----------------------|------------------------------------------------------------|
| **Document Number**  | VAL-SUS-SENT-001                                           |
| **Document Title**   | SUS CPV Sentinel — Validation Plan                         |
| **Version**          | 1.0                                                        |
| **Status**           | APPROVED                                                   |
| **System**           | SUS CPV Sentinel v1.0                                      |
| **GAMP 5 Category**  | 4 — Configured Software                                    |
| **Author**           | Justin Arndt                                               |
| **Reviewed By**      | [Quality Systems Lead]                                     |
| **Approved By**      | [Quality Manager]                                          |
| **Effective Date**   | 2026-05-16                                                 |
| **Review Date**      | 2028-05-16                                                 |
| **Storage Location** | Veeva Vault QualityDocs — Validation / CSV                 |
| **Kneat Project**    | KNEAT-SUS-SENT-2026-001                                    |

---

# SUS CPV Sentinel — Validation Plan

## 1. Purpose and Scope

### 1.1 Purpose

This Validation Plan (VP) defines the strategy, scope, responsibilities, and documentation requirements for the validation of **SUS CPV Sentinel v1.0**, a computerized system used to perform Stage 3 Continued Process Verification (CPV) statistical analysis on Single-Use System (SUS) lot genealogy and process data.

This document has been prepared in accordance with:
- **GAMP 5 Second Edition** (ISPE, July 2022)
- **21 CFR Part 11** — Electronic Records; Electronic Signatures
- **21 CFR 211.68** — Automated, Mechanical, and Electronic Equipment
- **EU GMP Annex 11** — Computerised Systems
- **ICH Q9(R1)** — Quality Risk Management
- **ICH Q10** — Pharmaceutical Quality System
- **FDA Process Validation: General Principles and Practices** (January 2011) — Stage 3 CPV
- **ASTM E3051-25** — Standard Guide for Specification, Design, Verification, and Application of Single-Use Systems
- **PDA Technical Report No. 66** — Application of Single-Use Systems in Pharmaceutical Manufacturing
- **USP \<665\> / \<1665\>** — Plastic Components and Systems (effective 1 May 2026)

### 1.2 Scope

SUS CPV Sentinel v1.0 encompasses the following functional modules:

| Module | Function |
|---|---|
| `ingest.py` | Ingests and validates SUS lot genealogy data from CSV / LIMS export |
| `integrity_cpk.py` | Calculates Cpk / Ppk on pressure-decay integrity test data per SUS SKU |
| `el_shewhart.py` | Shewhart I-MR control charts with Nelson Rule 1 & 2 violation detection on E&L data |
| `hotelling_t2.py` | Hotelling T² multivariate statistical process control on combined process parameters |
| `supplier_scorecard.py` | Composite supplier performance ranking including SCN impact scoring |
| `audit_trail.py` | ALCOA+-compliant immutable JSON audit log with cryptographic hash chaining |
| `report.py` | GxP-formatted Markdown/HTML deviation alert report generation |
| `app.py` | Streamlit web application — interactive user interface |

**Out of scope:** Integration with live LIMS systems, ERP/MES systems, or regulatory submission data. This version operates on exported flat-file data only.

### 1.3 System Classification

Per GAMP 5 Second Edition, SUS CPV Sentinel is classified as **Category 4 — Configured Software**. The system is built on standard Python libraries (NumPy, SciPy, Pandas, Streamlit) configured for the specific CPV use case. No custom algorithms outside established statistical methods are implemented.

| GAMP 5 Category | Description | Applicable? |
|---|---|---|
| 1 — Infrastructure software | OS, middleware | No |
| 3 — Non-configured software | Standard packages used as-is | No |
| **4 — Configured software** | **Standard platform configured for specific use** | **Yes** |
| 5 — Custom software | Bespoke application | No |

> **Rationale:** Statistical methods employed (Cpk/Ppk, Shewhart I-MR, Hotelling T², Nelson Rules) are established, published, and independently verifiable against reference datasets. The software configures and applies these methods; it does not invent new statistical approaches.

---

## 2. System Description

### 2.1 System Overview

SUS CPV Sentinel is a Python-based analytical platform designed to operationalize the FDA's Stage 3 CPV requirement for Single-Use System process data. The system addresses a data infrastructure gap identified at biopharmaceutical manufacturing facilities: SUS lot genealogy, integrity test results, extractables/leachables (E&L) measurements, and supplier change notification (SCN) records are typically maintained in disconnected systems, preventing systematic trend detection and regulatory-required CPV monitoring.

### 2.2 Business Need

The system was developed in response to:

1. **USP \<665\> enforcement (1 May 2026):** End users now bear regulatory responsibility for assessing Process Equipment-Related Leachables (PERLs) across their entire plastic manufacturing train. This requires a programmatic risk-scoring and trending capability.

2. **ASTM E3051-25 (January 2025):** Updated standard requires systematic data management for SUS qualification and continued verification, explicitly including digital data infrastructure.

3. **FDA Process Validation Stage 3:** Requires ongoing statistical surveillance of commercial process performance, including CQAs that may be influenced by SUS component lot-to-lot variability.

4. **Supplier Change Notification (SCN) management:** Film resin changes, additive substitutions, or sterilisation facility changes can invalidate existing extractables data. A systematic SCN impact scoring system enables rapid risk triage.

### 2.3 Data Flow

```
SUS Lot Genealogy Data (CSV / LIMS Export)
    │
    ▼
[ingest.py] — Schema validation, data type enforcement, ALCOA+ field checks
    │
    ├──► [integrity_cpk.py] — Pressure-decay Cpk/Ppk per SKU
    │
    ├──► [el_shewhart.py] — E&L Shewhart I-MR + Nelson Rule detection
    │
    ├──► [hotelling_t2.py] — Multivariate T² on combined parameters
    │
    ├──► [supplier_scorecard.py] — Composite supplier ranking
    │
    └──► [audit_trail.py] — Immutable ALCOA+-compliant event log
                │
                ▼
          [report.py] — GxP-formatted deviation alert / summary report
                │
                ▼
          [app.py] — Streamlit interactive dashboard
```

---

## 3. Validation Strategy

### 3.1 Risk-Based Approach

Validation depth and testing intensity are determined by risk, per ICH Q9(R1). Risk classification considers:

- **Impact on product quality** — Does a system failure affect a CQA?
- **Impact on data integrity** — Does a system failure compromise ALCOA+ compliance?
- **Impact on patient safety** — Could a system failure result in a product reaching patients that does not meet its specification?

SUS CPV Sentinel functions as a **decision-support tool**. It does not directly control manufacturing equipment or release product. However:
- It generates **deviation alerts** that trigger quality investigations
- It produces **audit trail records** that are regulatory compliance records
- Its statistical outputs are used to **make process validation decisions**

Risk classification: **High** — errors in statistical calculations or audit trail failures directly affect data integrity and regulatory compliance.

### 3.2 V-Model Validation Lifecycle

```
     User Requirements (URS)                 Validation Summary Report
          │                                           ▲
          ▼                                           │
     Risk Assessment ──────────────────────► Final Risk Review
          │                                           ▲
          ▼                                           │
     IQ Protocol ─────────────────────────► IQ Report
          │                                           ▲
          ▼                                           │
     OQ Protocol ─────────────────────────► OQ Report
          │                                           ▲
          ▼                                           │
     PQ Protocol ─────────────────────────► PQ Report
```

### 3.3 Validation Documents

| Document Number | Title | Platform |
|---|---|---|
| VAL-SUS-SENT-001 | Validation Plan (this document) | Veeva Vault |
| VAL-SUS-SENT-002 | User Requirements Specification (URS) | Veeva Vault |
| VAL-SUS-SENT-003 | Risk Assessment | Veeva Vault |
| VAL-SUS-SENT-004 | IQ Protocol and Report | Kneat Gx / Veeva Vault |
| VAL-SUS-SENT-005 | OQ Protocol and Report | Kneat Gx / Veeva Vault |
| VAL-SUS-SENT-006 | PQ Protocol and Report | Kneat Gx / Veeva Vault |
| VAL-SUS-SENT-007 | Requirements Traceability Matrix (RTM) | Veeva Vault |
| VAL-SUS-SENT-008 | Validation Summary Report | Veeva Vault |

> **Execution Platform:** IQ, OQ, and PQ protocols are authored in Veeva Vault QualityDocs and executed electronically in **Kneat Gx**. Test step execution records, electronic signatures, and evidence attachments are captured in Kneat with automatic timestamp and audit trail. Final approved reports are stored in Veeva Vault.

---

## 4. Roles and Responsibilities

| Role | Responsibility |
|---|---|
| **Validation Owner** | Accountable for validation completion and accuracy; approves this VP |
| **System Owner** | Responsible for system configuration and ongoing change control |
| **QA Reviewer** | Reviews all protocols and reports; ensures regulatory compliance |
| **Protocol Author** | Writes and executes IQ/OQ/PQ protocols in Kneat Gx |
| **MSAT Data Specialist** | Subject matter expert for SUS domain requirements and acceptance criteria |
| **IT/Infrastructure** | Confirms hardware and software environment for IQ |

---

## 5. Change Control

Any changes to SUS CPV Sentinel v1.0 post-validation require a formal change control record in Veeva Vault. The change impact assessment shall evaluate:

1. Whether affected modules require re-execution of OQ/PQ test cases
2. Whether the audit trail integrity has been affected
3. Whether statistical method parameters have been modified
4. Whether the change constitutes a major or minor change per GAMP 5 Chapter 10

Re-validation scope shall be determined by the Validation Owner and QA Reviewer based on risk.

---

## 6. Training Requirements

Prior to PQ execution with operational data, all system users shall complete:
- SUS CPV Sentinel v1.0 User Training (LSOP-SUS-SENT-001, controlled in Veeva Vault)
- 21 CFR Part 11 / ALCOA+ Data Integrity awareness training (site curriculum)

Training records shall be confirmed prior to PQ protocol sign-off in Kneat Gx.

---

## 7. Acceptance Criteria for Validation Completion

Validation is considered complete when:

- [ ] All IQ, OQ, and PQ test cases have a documented result (Pass or Deviation Resolved)
- [ ] All deviations have been closed with documented impact assessment
- [ ] The Validation Summary Report is approved in Veeva Vault
- [ ] The system is registered in the site computerized system inventory
- [ ] User training records are complete

---

## 8. Reference Documents

| Reference | Title |
|---|---|
| GAMP 5 (2022) | Good Automated Manufacturing Practice Guide, Second Edition |
| 21 CFR Part 11 | Electronic Records; Electronic Signatures |
| 21 CFR 211.68 | Automated, Mechanical, and Electronic Equipment |
| EU GMP Annex 11 | Computerised Systems |
| ICH Q9(R1) | Quality Risk Management |
| ICH Q10 | Pharmaceutical Quality System |
| FDA PV Guidance 2011 | Process Validation: General Principles and Practices |
| ASTM E3051-25 | Standard Guide for Specification, Design, Verification, and Application of Single-Use Systems |
| PDA TR 66 | Application of Single-Use Systems in Pharmaceutical Manufacturing |
| USP \<665\> | Plastic Components and Systems Used to Manufacture Pharmaceutical Drug Products |
| MHRA 2018 | GxP Data Integrity Guidance and Definitions |

---

*End of Document — VAL-SUS-SENT-001 v1.0*
