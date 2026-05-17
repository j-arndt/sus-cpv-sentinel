"""
app.py — SUS CPV Sentinel v1.0 | GAMP 5 Category 4 | VAL-SUS-SENT-001
Streamlit interactive dashboard for Stage 3 Continued Process Verification
"""

import io
import tempfile
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yaml

from sentinel import __version__
from sentinel.audit_trail import AuditTrail, AuditIntegrityError
from sentinel.ingest import load_and_validate, IngestValidationError
from sentinel.integrity_cpk import run_capability
from sentinel.el_shewhart import run_shewhart
from sentinel.hotelling_t2 import run_hotelling
from sentinel.supplier_scorecard import run_scorecard
from sentinel.report import generate_report

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SUS CPV Sentinel",
    page_icon="⚗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load config ──────────────────────────────────────────────────────────────
@st.cache_data
def load_config():
    with open("config.yaml") as f:
        return yaml.safe_load(f)

CONFIG = load_config()

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"] { background: #0a0f1e; }
.metric-card { background:#111827; border-radius:8px; padding:1rem;
               border-left:4px solid #3b82f6; margin-bottom:0.5rem; }
.alert-oos    { border-left:4px solid #ef4444 !important; }
.alert-warn   { border-left:4px solid #f59e0b !important; }
.alert-ok     { border-left:4px solid #22c55e !important; }
.badge        { display:inline-block; padding:2px 10px; border-radius:12px;
                font-size:0.75rem; font-weight:700; }
.badge-oos    { background:#7f1d1d; color:#fca5a5; }
.badge-warn   { background:#78350f; color:#fcd34d; }
.badge-ok     { background:#14532d; color:#86efac; }
h1 { color: #e2e8f0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚗️ SUS CPV Sentinel")
    st.markdown(f"**v{__version__}** · GAMP 5 Cat 4")
    st.markdown("---")
    st.markdown("**Regulatory Basis**")
    st.markdown("- FDA PV 2011 Stage 3 CPV\n- ASTM E3051-25\n- PDA TR 66\n- USP \\<665\\>\n- 21 CFR Part 11 / ALCOA+")
    st.markdown("---")
    st.markdown("**Execution Platform**")
    st.markdown("Kneat Gx · Veeva Vault QualityDocs")
    st.markdown("---")
    uploaded = st.file_uploader("Upload SUS lot genealogy CSV", type="csv")
    use_demo = st.button("Load demo dataset (150 lots)", use_container_width=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = None
    st.session_state.cpk_results = []
    st.session_state.cpk_alerts = []
    st.session_state.shewhart_results = []
    st.session_state.shewhart_alerts = []
    st.session_state.hotelling_result = None
    st.session_state.hotelling_alerts = []
    st.session_state.scores = []
    st.session_state.score_alerts = []
    st.session_state.all_alerts = []
    st.session_state.audit = None

def run_analysis(df: pd.DataFrame, audit: AuditTrail):
    cpk_res, cpk_alerts = run_capability(df, audit, CONFIG)
    sh_res, sh_alerts = run_shewhart(df, audit, CONFIG)
    h_res, h_alerts = run_hotelling(df, audit, CONFIG)
    scores, sc_alerts = run_scorecard(df, audit, CONFIG)
    all_alerts = cpk_alerts + sh_alerts + h_alerts + sc_alerts

    st.session_state.update({
        "df": df, "cpk_results": cpk_res, "cpk_alerts": cpk_alerts,
        "shewhart_results": sh_res, "shewhart_alerts": sh_alerts,
        "hotelling_result": h_res, "hotelling_alerts": h_alerts,
        "scores": scores, "score_alerts": sc_alerts,
        "all_alerts": all_alerts, "audit": audit,
    })

# ── Data loading ──────────────────────────────────────────────────────────────
audit = AuditTrail("audit/audit_trail.jsonl")

if use_demo and st.session_state.df is None:
    audit.session_start()
    df = load_and_validate("data/synthetic_sus_lots.csv", audit)
    run_analysis(df, audit)
    st.rerun()

if uploaded and st.session_state.df is None:
    audit.session_start()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(uploaded.read())
        tmp_path = tmp.name
    try:
        df = load_and_validate(tmp_path, audit)
        run_analysis(df, audit)
        st.rerun()
    except IngestValidationError as e:
        st.error(f"❌ Ingestion failed: {e}")

# ── Landing page ──────────────────────────────────────────────────────────────
if st.session_state.df is None:
    st.title("⚗️ SUS CPV Sentinel")
    st.markdown("""
    **Stage 3 Continued Process Verification for Single-Use Systems**

    Upload a SUS lot genealogy CSV or load the 150-lot demo dataset to begin analysis.

    | Module | Analysis |
    |---|---|
    | Integrity Test CPV | Cpk/Ppk per SKU · OOS and Marginal flagging |
    | E&L Shewhart Monitor | I-MR control charts · Nelson Rule 1 & 2 detection |
    | Hotelling T² | Multivariate SPC across delta-P, temperature, lot age |
    | Supplier Scorecard | Composite ranking · SCN impact alerting |
    | Audit Trail | ALCOA+-compliant · Hash-chained · 21 CFR Part 11 |

    > ⚠️ **USP \\<665\\> effective 1 May 2026** — end users bear responsibility for PERL assessment across their full plastic manufacturing train.
    """)
    st.stop()

# ── Main dashboard ────────────────────────────────────────────────────────────
df = st.session_state.df
all_alerts = st.session_state.all_alerts

st.title("⚗️ SUS CPV Sentinel — Dashboard")

# Alert banner
if all_alerts:
    oos = [a for a in all_alerts if "OOS" in a.alert_type or "OOC" in a.alert_type]
    st.error(f"🚨 **{len(all_alerts)} active deviation alert(s)** — {len(oos)} OOS/OOC")
else:
    st.success("✅ All CPV metrics within acceptance criteria")

# KPI row
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Lots analysed", len(df))
c2.metric("Suppliers", df["supplier_name"].nunique())
c3.metric("SKUs", df["sku_id"].nunique())
c4.metric("Active alerts", len(all_alerts))
c5.metric("FAIL results", (df["result"] == "FAIL").sum())

st.divider()

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 CPV Overview", "📈 E&L Charts", "🔵 Hotelling T²",
    "🏭 Supplier Scorecard", "🚨 Deviation Alerts",
    "📋 Audit Trail", "📄 GxP Report"
])

# ── Tab 1: CPV Overview ───────────────────────────────────────────────────────
with tab1:
    st.subheader("Process Capability by SKU")
    st.caption(f"USL = {CONFIG['integrity_test']['usl_mbar']} mbar · LSL = {CONFIG['integrity_test']['lsl_mbar']} mbar · Min n = {CONFIG['integrity_test']['min_lots_cpk']}")

    rows = []
    for r in st.session_state.cpk_results:
        badge = ("🔴 OOS" if "OUT_OF_SPECIFICATION" in r.status
                 else "🟡 MARGINAL" if "MARGINAL" in r.status
                 else "🟢 CAPABLE" if "CAPABLE" in r.status
                 else "⚪ " + r.status)
        rows.append({
            "SKU": r.sku_id, "Supplier": r.supplier_name, "n": r.n,
            "Mean (mbar)": round(r.mean, 3),
            "Cpk": f"{r.cpk:.3f}" if r.cpk == r.cpk else "N/A",
            "Ppk": f"{r.ppk:.3f}" if r.ppk == r.ppk else "N/A",
            "Status": badge,
        })
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ── Tab 2: E&L Shewhart ───────────────────────────────────────────────────────
with tab2:
    st.subheader("E&L Shewhart I-MR Control Charts")
    sh_results = st.session_state.shewhart_results
    if not sh_results:
        st.info("No E&L data present in dataset.")
    else:
        options = [f"{r.supplier_name} | {r.sku_id} | {r.compound}" for r in sh_results]
        choice = st.selectbox("Select series", options)
        idx = options.index(choice)
        r = sh_results[idx]

        fig = go.Figure()
        colors = ["red" if i in r.rule1_violations or i in r.rule2_violations
                  else "#3b82f6" for i in range(r.n)]
        fig.add_trace(go.Scatter(
            x=r.lot_numbers, y=r.values, mode="lines+markers",
            marker=dict(color=colors, size=8), name="E&L",
        ))
        for label, val, color in [
            ("UCL", r.ucl, "#ef4444"), ("Mean", r.mean, "#22c55e"), ("LCL", r.lcl, "#ef4444")
        ]:
            fig.add_hline(y=val, line_dash="dash", line_color=color,
                          annotation_text=f"{label}={val:.4f}", annotation_position="right")
        fig.update_layout(
            title=f"I-Chart: {r.supplier_name} · {r.compound}",
            plot_bgcolor="#111827", paper_bgcolor="#111827",
            font=dict(color="#e2e8f0"), height=400,
            xaxis=dict(title="Lot Number", gridcolor="#1f2937"),
            yaxis=dict(title="E&L Measurement", gridcolor="#1f2937"),
        )
        st.plotly_chart(fig, use_container_width=True)
        if r.rule1_violations:
            st.error(f"Nelson Rule 1 violation(s) at lots: {[r.lot_numbers[i] for i in r.rule1_violations]}")
        if r.rule2_violations:
            st.warning(f"Nelson Rule 2 (9-point run) detected at lots: {[r.lot_numbers[i] for i in r.rule2_violations]}")

# ── Tab 3: Hotelling T² ───────────────────────────────────────────────────────
with tab3:
    st.subheader("Hotelling T² Multivariate Monitor")
    h = st.session_state.hotelling_result
    if h is None:
        st.info(f"Insufficient data for T² (minimum {CONFIG['hotelling']['min_observations']} observations).")
    else:
        st.caption(f"Variables: {', '.join(h.variables)} · UCL = {h.ucl} · α = {CONFIG['hotelling']['alpha']}")
        colors = ["red" if i in h.ooc_indices else "#3b82f6" for i in range(h.n)]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=h.lot_numbers, y=h.t2_values, mode="lines+markers",
            marker=dict(color=colors, size=7), name="T²",
        ))
        fig.add_hline(y=h.ucl, line_dash="dash", line_color="#ef4444",
                      annotation_text=f"UCL={h.ucl}", annotation_position="right")
        fig.update_layout(
            title="Hotelling T² — Multivariate SPC",
            plot_bgcolor="#111827", paper_bgcolor="#111827",
            font=dict(color="#e2e8f0"), height=400,
            xaxis=dict(title="Lot", gridcolor="#1f2937"),
            yaxis=dict(title="T² Statistic", gridcolor="#1f2937"),
        )
        st.plotly_chart(fig, use_container_width=True)
        if h.ooc_indices:
            st.error(f"Out-of-control lots: {[h.lot_numbers[i] for i in h.ooc_indices]}")

# ── Tab 4: Supplier Scorecard ─────────────────────────────────────────────────
with tab4:
    st.subheader("Supplier Performance Scorecard")
    scores = st.session_state.scores
    if scores:
        rows = [{"Rank": s.rank, "Supplier": s.supplier_name,
                 "Composite Score": f"{s.composite_score:.3f}",
                 "SCN Impact (12mo)": s.scn_total_impact,
                 "CoA Complete": f"{s.coa_completeness:.1%}",
                 "Rejection Rate": f"{s.rejection_rate:.1%}",
                 "Lots": s.lot_count} for s in scores]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    for a in st.session_state.score_alerts:
        st.error(f"🚨 **SCN ALERT** — {a.supplier_name}: Rolling 12-month SCN impact = {a.value} "
                 f"(threshold ≤ {CONFIG['scorecard']['scn_alert_threshold']})\n\n"
                 f"References: {a.regulatory_ref}")

# ── Tab 5: Deviation Alerts ───────────────────────────────────────────────────
with tab5:
    st.subheader("Active Deviation Alerts")
    if not all_alerts:
        st.success("No active alerts.")
    else:
        for i, a in enumerate(all_alerts, 1):
            level = st.error if "OOS" in a.alert_type or "OOC" in a.alert_type or "FAIL" in a.alert_type else st.warning
            level(
                f"**[{a.alert_type}]** {a.supplier_name} · {a.sku_id}\n\n"
                f"Metric: {a.metric} = **{a.value}** (criterion: {a.criterion})\n\n"
                f"Lots: {', '.join(a.lot_numbers[:10])}"
                + (f" +{len(a.lot_numbers)-10} more" if len(a.lot_numbers) > 10 else "") +
                f"\n\nRef: _{a.regulatory_ref}_"
            )

# ── Tab 6: Audit Trail ────────────────────────────────────────────────────────
with tab6:
    st.subheader("Audit Trail — ALCOA+ Compliant")
    try:
        entries = audit.load_entries()
        st.success(f"Hash chain verified — {len(entries)} entries intact")
        if entries:
            action_filter = st.selectbox(
                "Filter by action",
                ["All"] + sorted({e["action"] for e in entries}),
            )
            filtered = entries if action_filter == "All" else [e for e in entries if e["action"] == action_filter]
            display = [{
                "Timestamp (UTC)": e["timestamp_utc"],
                "Action": e["action"],
                "User": e["user"],
                "Rule Reference": e["rule_reference"],
                "Event ID": e["event_id"][:16] + "…",
            } for e in filtered]
            st.dataframe(pd.DataFrame(display), use_container_width=True, hide_index=True)

            # Export
            jsonl_bytes = "\n".join(__import__("json").dumps(e) for e in entries).encode()
            st.download_button("Download full audit trail (.jsonl)", jsonl_bytes,
                               "audit_trail.jsonl", "application/jsonl")
    except AuditIntegrityError as e:
        st.error(f"⛔ AUDIT TRAIL INTEGRITY FAILURE: {e}")

# ── Tab 7: GxP Report ────────────────────────────────────────────────────────
with tab7:
    st.subheader("GxP Summary Report Generator")
    st.caption("URS-060 — URS-064 / VAL-SUS-SENT-005 OQ-Report")

    if st.button("Generate GxP Report", type="primary"):
        date_range = (
            f"{df['test_date'].min().strftime('%Y-%m-%d')} to "
            f"{df['test_date'].max().strftime('%Y-%m-%d')}"
        )
        report_text = generate_report(
            cpk_results=st.session_state.cpk_results,
            hotelling_result=st.session_state.hotelling_result,
            supplier_scores=st.session_state.scores,
            all_alerts=all_alerts,
            audit=audit,
            data_range=date_range,
            lot_count=len(df),
        )
        st.markdown(report_text)
        st.download_button(
            "Download report (.md)", report_text.encode(),
            "cpv_report.md", "text/markdown",
        )
