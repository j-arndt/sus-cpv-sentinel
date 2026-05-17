---
# DOCUMENT CONTROL

| Field                | Value                                                      |
|----------------------|------------------------------------------------------------|
| **Document Number**  | VAL-SUS-SENT-004                                           |
| **Document Title**   | SUS CPV Sentinel — Installation Qualification Protocol & Report |
| **Version**          | 1.0                                                        |
| **Status**           | APPROVED                                                   |
| **Execution Platform** | Kneat Gx — Project KNEAT-SUS-SENT-2026-001              |
| **Author**           | Justin Arndt                                               |
| **Reviewed By**      | [Quality Systems Lead]                                     |
| **Approved By**      | [Quality Manager]                                          |
| **Effective Date**   | 2026-05-16                                                 |
| **Storage Location** | Veeva Vault QualityDocs — Validation / CSV                 |

---

# SUS CPV Sentinel — Installation Qualification Protocol

## 1. Purpose and Scope

This IQ Protocol verifies that SUS CPV Sentinel v1.0 is correctly installed and configured in the intended operating environment, and that the software version and all dependencies match the validated configuration.

**Execution:** Recorded in Kneat Gx, Project KNEAT-SUS-SENT-2026-001.

---

## 2. IQ Test Cases

### IQ-010 — Software Version Verification

| Step | Action | Expected Result | Actual Result | P/F |
|---|---|---|---|---|
| 1 | Run `python --version` in project environment | Python 3.10.x or higher | | |
| 2 | Run `pip show streamlit` | Version ≥ 1.30.0 | | |
| 3 | Run `pip show pandas` | Version ≥ 2.0.0 | | |
| 4 | Run `pip show scipy` | Version ≥ 1.11.0 | | |
| 5 | Run `pip show numpy` | Version ≥ 1.25.0 | | |
| 6 | Compare installed versions to `requirements.txt` | All versions match `requirements.txt` exactly | | |

---

### IQ-020 — Application Launch Verification

| Step | Action | Expected Result | Actual Result | P/F |
|---|---|---|---|---|
| 1 | Run `streamlit run app.py` | Application launches without errors | | |
| 2 | Navigate to `http://localhost:8501` | Landing page displayed with application title | | |
| 3 | Confirm application version displayed in UI | Version = "1.0" displayed in header or About panel | | |

---

### IQ-030 — Directory Structure Verification

| Step | Action | Expected Result | Actual Result | P/F |
|---|---|---|---|---|
| 1 | Verify presence of `sentinel/` directory | Directory exists and contains all 7 module files | | |
| 2 | Verify presence of `docs/` directory | Contains all 8 validation documents | | |
| 3 | Verify presence of `tests/` directory | Contains unit test files | | |
| 4 | Verify presence of `data/` directory | Contains synthetic dataset | | |
| 5 | Verify presence of `config.yaml` | Configuration file with USL/LSL and weighting parameters present | | |

---

### IQ-040 — Audit Trail Storage Location

| Step | Action | Expected Result | Actual Result | P/F |
|---|---|---|---|---|
| 1 | Launch application and load any dataset | Audit trail file created at configured path | | |
| 2 | Verify file extension | File is `.jsonl` format | | |
| 3 | Verify file is human-readable | Open file in text editor; valid JSON-Lines format confirmed | | |

---

### IQ-050 — Unit Test Suite Execution

| Step | Action | Expected Result | Actual Result | P/F |
|---|---|---|---|---|
| 1 | Run `python -m pytest tests/ -v` | All tests collected and executed | | |
| 2 | Record pass/fail count | 0 failures, 0 errors | | |
| 3 | Attach pytest output as evidence | Output attached in Kneat evidence field | | |

---

## 3. IQ Summary

| Section | Cases | Passed | Deviations |
|---|---|---|---|
| Software version | 6 | | |
| Application launch | 3 | | |
| Directory structure | 5 | | |
| Audit trail storage | 3 | | |
| Unit test suite | 3 | | |
| **Total** | **20** | | |

**IQ Outcome:** ☐ PASSED — proceed to OQ &nbsp;&nbsp; ☐ FAILED — resolve deviations

| Role | Name | Kneat Gx Signature | Date |
|---|---|---|---|
| Protocol Executor | | [Kneat record] | |
| QA Reviewer | | [Kneat record] | |

---

*End of Document — VAL-SUS-SENT-004 v1.0*
