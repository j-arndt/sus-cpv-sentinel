---
title: SUS CPV Sentinel
emoji: ⚗️
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: "1.35.0"
app_file: app.py
pinned: true
license: apache-2.0
short_description: Stage 3 CPV for SUS | GAMP 5 Cat 4 | 21 CFR Part 11
---

# SUS CPV Sentinel

**Stage 3 Continued Process Verification for Single-Use Systems**

[![Validation Status](https://img.shields.io/badge/Validation-GAMP%205%20Cat%204-blue)](docs/VAL-SUS-SENT-008_Validation_Summary_Report.md)
[![Regulation](https://img.shields.io/badge/21%20CFR%20Part%2011-Compliant-green)](docs/VAL-SUS-SENT-002_URS.md)
[![USP 665](https://img.shields.io/badge/USP%20%3C665%3E-May%202026-orange)](docs/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](requirements.txt)

> **USP \<665\> became enforceable 1 May 2026.** End users — not suppliers — now bear regulatory responsibility for assessing Process Equipment-Related Leachables (PERLs) across their entire plastic manufacturing train. This tool operationalizes that requirement.

---

## The Problem

Single-Use System lot data lives in three places simultaneously: paper integrity test logs, supplier CoA PDFs, and disconnected LIMS exports. There is no systematic way to detect a Cytiva film resin change before it shows up as a leachable exceedance in your drug product.

**FDA Process Validation (2011) Stage 3** requires ongoing statistical surveillance of commercial process performance. For facilities running SUS-based bioprocesses, that means:

1. Pressure-decay integrity test trending per SUS SKU (Cpk/Ppk)
2. Extractables/leachables trend monitoring (Shewhart I-MR)
3. Multivariate process drift detection (Hotelling T²)
4. Supplier change notification (SCN) impact scoring

SUS CPV Sentinel builds that programme as a validated, ALCOA+-compliant analytical platform.

---

## What It Detects

On a 150-lot synthetic dataset spanning 18 months across 3 suppliers and 6 SKUs, the system detected:

| Signal | Detected | Lots After Event |
|---|---|---|
| SCN-CYT-2025-0114 (Cytiva film resin change) | ✅ | 0 (at filing) |
| E&L drift — Nelson Rule violations (Cytiva) | ✅ | \< 3 lots |
| Cpk OOS — Xcellerex-200L | ✅ | Immediate |
| Hotelling T² out-of-control observation | ✅ | Immediate |

---

## Key Numbers

| Metric | Value |
|---|---|
| Lots in validation dataset | 150 |
| Suppliers | 3 (Sartorius Stedim, Cytiva, Pall Corporation) |
| SKUs | 6 |
| URS requirements | 51 |
| OQ test cases | 13 / 13 passed |
| PQ test cases | 6 / 6 passed |
| Audit trail entries (PQ session) | 47 |
| Hash chain integrity | Verified — 0 tamper events |
| Regulatory citations in alerts | 100% |

---

## Modules

| Module | Analysis | URS |
|---|---|---|
| `sentinel/ingest.py` | CSV ingestion, schema validation, SHA-256 hash, ALCOA+ logging | URS-001–007 |
| `sentinel/integrity_cpk.py` | Cpk/Ppk per SKU · OOS (< 1.33) · Marginal (1.33–1.67) flagging | URS-010–016 |
| `sentinel/el_shewhart.py` | Shewhart I-MR control charts · Nelson Rule 1 & 2 detection | URS-020–026 |
| `sentinel/hotelling_t2.py` | Hotelling T² multivariate SPC · F-distribution UCL at α=0.0027 | URS-030–034 |
| `sentinel/supplier_scorecard.py` | Composite supplier ranking · Rolling 12-month SCN impact alerting | URS-040–045 |
| `sentinel/audit_trail.py` | Append-only JSONL · SHA-256 hash chain · SQLite index · 21 CFR Part 11 | URS-050–057 |
| `sentinel/report.py` | GxP-formatted Markdown/HTML deviation alert report | URS-060–064 |
| `app.py` | Streamlit dashboard — 7 tabs, dark theme, Plotly charts | — |

---

## Regulatory Alignment

| Standard | Requirement | Module |
|---|---|---|
| **FDA Process Validation 2011** | Stage 3 Continued Process Verification | All |
| **ASTM E3051-25** (Jan 2025) | SUS digital data management for qualification and CPV | `ingest`, `scorecard` |
| **ASTM E3244-23** | SUS integrity testing practices and data requirements | `integrity_cpk` |
| **PDA Technical Report No. 66** | SUS continued process verification · E&L monitoring | `el_shewhart` |
| **USP \<665\>** (eff. 1 May 2026) | PERL assessment across plastic manufacturing train | `scorecard`, `report` |
| **21 CFR Part 11 §11.10(e)** | Audit trail — date/time of all operator entries | `audit_trail` |
| **21 CFR 211.68** | Accuracy and reliability of automated equipment | `integrity_cpk`, `hotelling_t2` |
| **MHRA GxP Data Integrity 2018** | ALCOA+ — Attributable, Legible, Contemporaneous, Original, Accurate | `audit_trail` |
| **GAMP 5 Second Edition** | Risk-based validation — Category 4 Configured Software | `docs/` |
| **ICH Q9(R1)** | Quality Risk Management — FMEA methodology | `docs/VAL-SUS-SENT-003` |

---

## Validation Package

This tool ships with a complete GAMP 5-aligned validation package. All documents are authored for execution in **Kneat Gx** with document control and approval in **Veeva Vault QualityDocs**.

| Document | File |
|---|---|
| Validation Plan | [VAL-SUS-SENT-001](docs/VAL-SUS-SENT-001_Validation_Plan.md) |
| User Requirements Specification | [VAL-SUS-SENT-002](docs/VAL-SUS-SENT-002_URS.md) |
| Risk Assessment (FMEA) | [VAL-SUS-SENT-003](docs/VAL-SUS-SENT-003_Risk_Assessment.md) |
| IQ Protocol & Report | [VAL-SUS-SENT-004](docs/VAL-SUS-SENT-004_IQ_Protocol.md) |
| OQ Protocol & Report | [VAL-SUS-SENT-005](docs/VAL-SUS-SENT-005_OQ_Protocol.md) |
| PQ Protocol & Report | [VAL-SUS-SENT-006](docs/VAL-SUS-SENT-006_PQ_Protocol.md) |
| Requirements Traceability Matrix | [VAL-SUS-SENT-007](docs/VAL-SUS-SENT-007_Traceability_Matrix.md) |
| Validation Summary Report | [VAL-SUS-SENT-008](docs/VAL-SUS-SENT-008_Validation_Summary_Report.md) |

> **51 requirements · 100% Critical and Major coverage · 39 test cases · 0 deviations**

*Executed in Kneat Gx · Document control in Veeva Vault QualityDocs · GAMP 5 Category 4*

---

## Stack

```
Python 3.10+  ·  pandas  ·  numpy  ·  scipy  ·  Streamlit  ·  Plotly
JSONL audit trail  ·  SQLite index  ·  SHA-256 hash chain
```

---

## Quick Start

```bash
git clone https://github.com/j-arndt/sus-cpv-sentinel
cd sus-cpv-sentinel
pip install -r requirements.txt
python generate_synthetic_data.py   # generates 150-lot demo dataset
streamlit run app.py
```

Navigate to `http://localhost:8501` and click **"Load demo dataset (150 lots)"** in the sidebar to run the full CPV analysis.

---

## Audit Trail

Every calculation, alert, and user action is logged to an immutable, SHA-256 hash-chained JSONL file. Each entry contains:

```json
{
  "event_id": "a3f8c2d1...",
  "prev_hash": "7e4b91a0...",
  "timestamp_utc": "2026-05-16T22:31:05Z",
  "user": "system",
  "action": "shewhart_calculation",
  "inputs": {"supplier": "Cytiva", "sku_id": "Xcellerex-2000L", "n": 25},
  "outputs": {"mean": 0.4812, "ucl": 0.5931, "rule1_violations": 8, "rule2_violations": 2},
  "rule_reference": "PDA TR 66 §8.2 / ASTM E3051-25"
}
```

Tamper detection: loading a modified audit trail raises `AuditIntegrityError` and refuses to display the data.

---

## Author

**Justin Arndt** — Regulated AI & Data Validation Engineer

MSAT · GxP Data Engineering · Single-Use Systems · 21 CFR Part 11 · GAMP 5

[GitHub](https://github.com/j-arndt) · [LinkedIn](https://www.linkedin.com/in/qualityai/)
