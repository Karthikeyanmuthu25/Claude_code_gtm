"""
B2B Due Diligence Agent — Streamlit Frontend
"""

import os
import sys

# ── Force UTF-8 before anything touches stdout ────────────────────────────────
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
import traceback
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="B2B Due Diligence Agent",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session state — initialised FIRST, before any widget ─────────────────────
if "state" not in st.session_state:
    st.session_state.state = "idle"   # idle | running | done | error
if "result" not in st.session_state:
    st.session_state.result = None
if "error_msg" not in st.session_state:
    st.session_state.error_msg = ""
if "last_input" not in st.session_state:
    st.session_state.last_input = {}
# Persistent form values so they survive reruns
for _f in ["company_name","company_website","company_location",
           "dm_name","dm_title","dm_linkedin","dm_email"]:
    if _f not in st.session_state:
        st.session_state[_f] = ""

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: #080c10;
    color: #c8d0d8;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1280px; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #1e3a4a; border-radius: 2px; }

/* Header */
.dd-header { border-bottom: 1px solid #0e2233; padding-bottom: 1.5rem; margin-bottom: 2rem; }
.dd-eyebrow { font-family:'IBM Plex Mono',monospace; font-size:0.62rem; letter-spacing:0.28em; color:#1a7fa8; text-transform:uppercase; margin-bottom:0.35rem; }
.dd-title { font-size:1.55rem; font-weight:700; color:#e8edf2; letter-spacing:-0.02em; line-height:1.1; }
.dd-title span { color:#17a2c8; }
.dd-sub { font-family:'IBM Plex Mono',monospace; font-size:0.68rem; color:#2a4a5a; margin-top:0.45rem; letter-spacing:0.05em; }

/* Section label */
.slabel {
    font-family:'IBM Plex Mono',monospace; font-size:0.58rem; letter-spacing:0.3em;
    color:#1a7fa8; text-transform:uppercase; border-left:2px solid #1a7fa8;
    padding-left:0.55rem; margin-bottom:0.85rem; margin-top:0.25rem;
}

/* Form inputs */
.stTextInput > div > div > input {
    background:#0d1520 !important; border:1px solid #0e2233 !important;
    border-radius:3px !important; color:#c8d0d8 !important;
    font-family:'IBM Plex Mono',monospace !important; font-size:0.8rem !important;
}
.stTextInput > div > div > input:focus { border-color:#17a2c8 !important; }
.stTextInput > label {
    font-family:'IBM Plex Mono',monospace !important; font-size:0.65rem !important;
    color:#3a6a7a !important; letter-spacing:0.1em !important; text-transform:uppercase !important;
}

/* Buttons */
.stButton > button, .stFormSubmitButton > button {
    background:#0a1e2e !important; color:#17a2c8 !important;
    border:1px solid #17a2c8 !important; border-radius:3px !important;
    font-family:'IBM Plex Mono',monospace !important; font-size:0.7rem !important;
    letter-spacing:0.2em !important; text-transform:uppercase !important;
    padding:0.55rem 1.5rem !important; width:100% !important;
    transition:all 0.15s !important;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background:#17a2c8 !important; color:#080c10 !important;
}
.stDownloadButton > button {
    background:#081a10 !important; color:#17c87a !important;
    border:1px solid #17c87a !important; border-radius:3px !important;
    font-family:'IBM Plex Mono',monospace !important; font-size:0.68rem !important;
    letter-spacing:0.15em !important; text-transform:uppercase !important;
    width:100% !important; margin-top:0.5rem !important;
}

/* Cards */
.dd-card {
    background:#0a1520; border:1px solid #0e2233; border-radius:5px;
    padding:1.1rem 1.35rem; margin-bottom:0.85rem;
}
.dd-card-title {
    font-family:'IBM Plex Mono',monospace; font-size:0.58rem;
    letter-spacing:0.28em; color:#1a7fa8; text-transform:uppercase; margin-bottom:0.8rem;
}

/* Verdict accents */
.v-proceed { border-left:3px solid #17c87a; }
.v-caution  { border-left:3px solid #c8a217; }
.v-reject   { border-left:3px solid #c82817; }

/* Score bars */
.srow { display:flex; align-items:center; gap:0.7rem; margin-bottom:0.55rem; }
.slbl { font-family:'IBM Plex Mono',monospace; font-size:0.65rem; color:#4a7080; width:115px; flex-shrink:0; }
.strack { flex:1; height:3px; background:#0e2233; border-radius:2px; overflow:hidden; }
.sfill  { height:100%; border-radius:2px; }
.sval   { font-family:'IBM Plex Mono',monospace; font-size:0.72rem; font-weight:600; width:42px; text-align:right; flex-shrink:0; }

/* Flag items */
.fi { display:flex; align-items:flex-start; gap:0.45rem; padding:0.38rem 0; font-size:0.79rem; line-height:1.4; border-bottom:1px solid #0a1826; }
.fi:last-child { border-bottom:none; }
.fd { font-family:'IBM Plex Mono',monospace; font-size:0.62rem; font-weight:600; padding:0.08rem 0.38rem; border-radius:2px; flex-shrink:0; letter-spacing:0.04em; }
.fd-red    { background:#1a0a08; color:#e05050; border:1px solid #401010; }
.fd-yellow { background:#1a1408; color:#c8a217; border:1px solid #402d10; }
.fd-green  { background:#081a10; color:#17c87a; border:1px solid #104030; }
.fd-match  { background:#081a18; color:#17c8c8; border:1px solid #0e3040; }
.fd-miss   { background:#1a0808; color:#c85050; border:1px solid #401010; }
.fd-info   { background:#0a1020; color:#4a88a8; border:1px solid #0e2030; }

/* Evidence */
.ei { padding:0.32rem 0; font-size:0.78rem; color:#6888a0; border-bottom:1px solid #0a1826; line-height:1.45; }
.ei:last-child { border-bottom:none; }
.ep::before { content:'+ '; color:#17c87a; font-family:monospace; }
.en::before { content:'- '; color:#c85050; font-family:monospace; }
.eu::before { content:'· '; color:#2a5060; font-family:monospace; }

/* Action items */
.ai { display:flex; gap:0.55rem; padding:0.38rem 0; font-size:0.79rem; border-bottom:1px solid #0a1826; align-items:flex-start; }
.ai:last-child { border-bottom:none; }
.aa { color:#17a2c8; font-family:monospace; flex-shrink:0; }

/* Pipeline */
.pipeline { display:flex; flex-direction:column; gap:0.28rem; margin:0.5rem 0; }
.srow-pl { display:flex; align-items:center; gap:0.55rem; font-family:'IBM Plex Mono',monospace; font-size:0.67rem; }
.sicon-pl { width:16px; text-align:center; }
.sname-pl { flex:1; }
.sstatus-pl { width:55px; text-align:right; }

/* Summary */
.sumbox { background:#060f18; border:1px solid #0e2233; border-radius:3px; padding:0.9rem 1.1rem; font-size:0.8rem; color:#6888a0; line-height:1.65; font-style:italic; }

/* Conf badge */
.cbadge { display:inline-block; font-family:'IBM Plex Mono',monospace; font-size:0.58rem; letter-spacing:0.1em; padding:0.12rem 0.45rem; border-radius:2px; vertical-align:middle; margin-left:0.45rem; }
.ch { background:#081a10; color:#17c87a; border:1px solid #104030; }
.cm { background:#1a1408; color:#c8a217; border:1px solid #402d10; }
.cl { background:#1a0a08; color:#e05050; border:1px solid #401010; }

/* Error */
.errbox { background:#120808; border:1px solid #401010; border-radius:4px; padding:0.9rem 1.1rem; color:#e05050; font-family:'IBM Plex Mono',monospace; font-size:0.75rem; line-height:1.5; }

/* Status indicator */
.status-ok  { font-family:'IBM Plex Mono',monospace; font-size:0.62rem; color:#1a8a4a; margin-top:0.6rem; }
.status-err { font-family:'IBM Plex Mono',monospace; font-size:0.62rem; color:#8a3a1a; margin-top:0.6rem; }
.status-dim { font-family:'IBM Plex Mono',monospace; font-size:0.6rem; color:#1a3040; margin-top:0.25rem; }

@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.25} }
.dot { display:inline-block; width:5px; height:5px; background:#17a2c8; border-radius:50%; animation:pulse 1.3s ease-in-out infinite; margin-right:0.4rem; vertical-align:middle; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────

def score_color(s: int) -> str:
    return "#17c87a" if s >= 75 else ("#c8a217" if s >= 50 else "#c82817")

def score_bar(label: str, score: int):
    c = score_color(score)
    st.markdown(f"""
    <div class="srow">
        <div class="slbl">{label}</div>
        <div class="strack"><div class="sfill" style="width:{score}%;background:{c};"></div></div>
        <div class="sval" style="color:{c};">{score}<span style="font-size:0.55rem;color:#2a4a5a;">/100</span></div>
    </div>""", unsafe_allow_html=True)

def flags(items, fd_cls, label):
    for item in (items or []):
        st.markdown(f'<div class="fi"><span class="fd {fd_cls}">{label}</span><span>{item}</span></div>', unsafe_allow_html=True)

def evidence(items, cls):
    for item in (items or []):
        st.markdown(f'<div class="ei {cls}">{item}</div>', unsafe_allow_html=True)

STAGES = [
    ("◈", "Input Validation",    "OpenAI GPT-4o"),
    ("◉", "Data Collection",     "Apify · Exa"),
    ("⊕", "Cross-Verification",  "Exa · OpenAI GPT-4o"),
    ("⊗", "Risk Detection",      "Exa · Apify · OpenAI GPT-4o"),
    ("⚡", "Trust Scoring",       "Exa · OpenAI GPT-4o"),
    ("◆", "Evidence Aggregation","Exa · OpenAI GPT-4o"),
    ("✦", "Final Assessment",    "OpenAI GPT-4o"),
]

def pipeline_html(done_up_to: int) -> str:
    # done_up_to=0 → all pending; done_up_to=8 → all done
    out = '<div class="pipeline">'
    for i, (icon, name, tools) in enumerate(STAGES):
        n = i + 1
        if n < done_up_to:
            ic     = f'<span style="color:#17c87a">{icon}</span>'
            st_txt = '<span style="color:#17c87a;font-size:0.58rem;">done</span>'
            nc     = "color:#2a8a5a;"
            tc     = "#1a5a3a"
        elif n == done_up_to:
            ic     = f'<span class="dot"></span><span style="color:#17a2c8">{icon}</span>'
            st_txt = '<span style="color:#17a2c8;font-size:0.58rem;">running</span>'
            nc     = "color:#6aaac0;"
            tc     = "#1a7fa8"
        else:
            ic     = f'<span style="color:#152030">{icon}</span>'
            st_txt = ""
            nc     = "color:#152030;"
            tc     = "#0e1e28"
        out += (
            f'<div class="srow-pl">'
            f'  <div class="sicon-pl">{ic}</div>'
            f'  <div class="sname-pl" style="{nc}">STAGE {n} — {name}'
            f'    <span style="font-size:0.56rem;color:{tc};margin-left:0.4rem;">[{tools}]</span>'
            f'  </div>'
            f'  <div class="sstatus-pl">{st_txt}</div>'
            f'</div>'
        )
    return out + "</div>"

def api_ok() -> bool:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    return bool(key) and not key.startswith("sk-ant-")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="dd-header">
  <div class="dd-eyebrow">Intelligence Platform · v2.0</div>
  <div class="dd-title">B2B <span>Due Diligence</span> Agent</div>
  <div class="dd-sub">7-Stage Autonomous Pipeline · Apify · Exa Search · OpenAI GPT-4o — Each stage independently reasoned</div>
</div>""", unsafe_allow_html=True)

# ── Two-column layout ─────────────────────────────────────────────────────────
left, right = st.columns([1, 1.6], gap="large")

# ══════════════════════════════════════════════════════════════════════════════
# LEFT — Input form
# ══════════════════════════════════════════════════════════════════════════════
with left:
    st.markdown('<div class="slabel">Target Entity</div>', unsafe_allow_html=True)

    with st.form("dd_form"):
        st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.58rem;color:#1a4a5a;letter-spacing:0.22em;text-transform:uppercase;margin-bottom:0.2rem;">Company</div>', unsafe_allow_html=True)
        company_name     = st.text_input("Company Name *",  value=st.session_state.company_name,    placeholder="Acme SaaS Inc.")
        company_website  = st.text_input("Website",         value=st.session_state.company_website,  placeholder="https://acmesaas.com")
        company_location = st.text_input("Location",        value=st.session_state.company_location, placeholder="San Francisco, CA, USA")

        st.markdown('<div style="border-top:1px solid #0e2233;margin:0.6rem 0;"></div>', unsafe_allow_html=True)
        st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.58rem;color:#1a4a5a;letter-spacing:0.22em;text-transform:uppercase;margin-bottom:0.2rem;">Decision Maker</div>', unsafe_allow_html=True)
        dm_name     = st.text_input("Full Name *",    value=st.session_state.dm_name,     placeholder="Jane Smith")
        dm_title    = st.text_input("Job Title",      value=st.session_state.dm_title,    placeholder="Chief Revenue Officer")
        dm_linkedin = st.text_input("LinkedIn URL",   value=st.session_state.dm_linkedin, placeholder="https://linkedin.com/in/janesmith")
        dm_email    = st.text_input("Email Address",  value=st.session_state.dm_email,    placeholder="jane@acmesaas.com")

        st.markdown('<div style="height:0.4rem;"></div>', unsafe_allow_html=True)
        submitted = st.form_submit_button(
            "◈  RUN ANALYSIS",
            disabled=(not api_ok() or st.session_state.state == "running")
        )

    # Load example shortcut
    if st.button("Load Example  (Acme SaaS)"):
        st.session_state.company_name     = "Acme SaaS Inc."
        st.session_state.company_website  = "https://acmesaas.com"
        st.session_state.company_location = "San Francisco, CA, USA"
        st.session_state.dm_name          = "Jane Smith"
        st.session_state.dm_title         = "Chief Revenue Officer"
        st.session_state.dm_linkedin      = "https://linkedin.com/in/janesmith-saas"
        st.session_state.dm_email         = "jane@acmesaas.com"
        st.rerun()

    # Key status
    if api_ok():
        st.markdown('<div class="status-ok">◉ OpenAI GPT-4o API key ready</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-err">◎ OPENAI_API_KEY not set or invalid in .env</div>', unsafe_allow_html=True)

    parts = []
    for env, lbl in [("EXA_API_KEY","Exa"),("APIFY_API_KEY","Apify")]:
        col = "#1a7fa8" if os.environ.get(env) else "#152030"
        parts.append(f'<span style="color:{col}">{lbl}</span>')
    st.markdown(f'<div class="status-dim">Enrichment: {" · ".join(parts)}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# Handle form submission — capture values & trigger pipeline
# ══════════════════════════════════════════════════════════════════════════════
if submitted:
    if not company_name.strip():
        st.warning("Company Name is required.")
    elif not dm_name.strip():
        st.warning("Decision Maker Full Name is required.")
    else:
        # Persist form values across reruns
        st.session_state.company_name     = company_name
        st.session_state.company_website  = company_website
        st.session_state.company_location = company_location
        st.session_state.dm_name          = dm_name
        st.session_state.dm_title         = dm_title
        st.session_state.dm_linkedin      = dm_linkedin
        st.session_state.dm_email         = dm_email

        st.session_state.last_input = {
            "company_name":               company_name.strip(),
            "company_website":            company_website.strip(),
            "company_location":           company_location.strip(),
            "decision_maker_name":        dm_name.strip(),
            "decision_maker_job_title":   dm_title.strip(),
            "decision_maker_linkedin_url":dm_linkedin.strip(),
            "decision_maker_email":       dm_email.strip(),
        }
        st.session_state.state     = "running"
        st.session_state.result    = None
        st.session_state.error_msg = ""
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# RIGHT — Results / pipeline
# ══════════════════════════════════════════════════════════════════════════════
with right:

    # ── RUNNING STATE ─────────────────────────────────────────────────────────
    if st.session_state.state == "running":
        inp = st.session_state.last_input

        st.markdown('<div class="slabel">Pipeline Running</div>', unsafe_allow_html=True)

        pipeline_ph = st.empty()
        pipeline_ph.markdown(pipeline_html(2), unsafe_allow_html=True)

        status_ph = st.empty()
        status_ph.markdown(
            '<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.68rem;color:#17a2c8;margin-top:0.75rem;">'
            '<span class="dot"></span>Collecting enrichment data...</div>',
            unsafe_allow_html=True
        )

        try:
            from agent.orchestrator import run_pipeline
            from agent.validator import validate_input

            def show_stage(n: int, msg: str):
                pipeline_ph.markdown(pipeline_html(n), unsafe_allow_html=True)
                status_ph.markdown(
                    f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.68rem;color:#17a2c8;">'
                    f'<span class="dot"></span>{msg}</div>',
                    unsafe_allow_html=True,
                )

            # Stage 1 — Input Validation (GPT-4o)
            show_stage(1, "Stage 1 — GPT-4o validating fields, URL patterns, email-domain alignment...")
            is_valid, errors, warnings = validate_input(inp)
            if errors:
                raise ValueError("Validation failed: " + " · ".join(errors))

            # Stage 2 — Data Collection (Apify + Exa)
            show_stage(2, "Stage 2 — Collecting data: Apify scraping · Exa web intelligence...")

            # Stage 3 — Cross-Verification (Exa + GPT-4o)
            show_stage(3, "Stage 3 — GPT-4o cross-verifying identity against Exa web intelligence...")

            # Stage 4 — Risk Detection (Exa + Apify + GPT-4o)
            show_stage(4, "Stage 4 — GPT-4o classifying risk flags from Exa signals + Apify data...")

            # Stage 5 — Trust Scoring (Exa + GPT-4o)
            show_stage(5, "Stage 5 — GPT-4o scoring company + DM via Exa intelligence...")

            # Stage 6 — Evidence Aggregation (Exa + GPT-4o)
            show_stage(6, "Stage 6 — GPT-4o aggregating supporting vs contradicting evidence from Exa...")

            # Stage 7 — Final Assessment (GPT-4o only)
            show_stage(7, "Stage 7 — GPT-4o synthesising all stages → final verdict...")

            result = run_pipeline(
                input_data=inp,
                api_key=os.environ.get("OPENAI_API_KEY",""),
                save_report=True,
            )

            st.session_state.result = result
            st.session_state.state  = "done"

        except Exception as exc:
            st.session_state.error_msg = f"{type(exc).__name__}: {exc}\n\n{traceback.format_exc()}"
            st.session_state.state     = "error"

        pipeline_ph.empty()
        status_ph.empty()
        st.rerun()

    # ── ERROR STATE ───────────────────────────────────────────────────────────
    elif st.session_state.state == "error":
        st.markdown('<div class="slabel">Pipeline Error</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="errbox">✕ {st.session_state.error_msg}</div>', unsafe_allow_html=True)
        if st.button("← Try Again"):
            st.session_state.state = "idle"
            st.rerun()

    # ── DONE STATE — render full results ──────────────────────────────────────
    elif st.session_state.state == "done" and st.session_state.result:
        result  = st.session_state.result
        inp     = st.session_state.last_input
        sr      = result.get("stage_results", {})
        fa      = sr.get("final_assessment", {})
        ts      = sr.get("trust_scoring", {})
        rd      = sr.get("risk_detection", {})
        cv      = sr.get("cross_verification", {})
        ea      = sr.get("evidence_aggregation", {})

        rec      = fa.get("recommendation", "CAUTION")
        conf     = fa.get("confidence", "MEDIUM")
        conf_pct = fa.get("confidence_percentage", 50)

        rc_map  = {"PROCEED":"#17c87a","CAUTION":"#c8a217","REJECT":"#c82817"}
        ri_map  = {"PROCEED":"✦","CAUTION":"⚠","REJECT":"✕"}
        rc      = rc_map.get(rec,"#c8d0d8")
        ri      = ri_map.get(rec,"?")
        v_cls   = f"v-{rec.lower()}"
        c_cls   = {"HIGH":"ch","MEDIUM":"cm","LOW":"cl"}.get(conf,"cm")

        st.markdown('<div class="slabel">Analysis Complete</div>', unsafe_allow_html=True)

        # Target line
        st.markdown(
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.65rem;color:#2a6a7a;margin-bottom:1rem;">'
            f'Target: <span style="color:#5a9aaa">{inp.get("company_name","")} · {inp.get("decision_maker_name","")}</span></div>',
            unsafe_allow_html=True
        )

        # ── VERDICT ──
        st.markdown(f"""
        <div class="dd-card {v_cls}">
          <div class="dd-card-title">Final Verdict</div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:1.35rem;font-weight:700;color:{rc};letter-spacing:0.06em;">
            {ri}&nbsp;&nbsp;{rec}
            <span class="cbadge {c_cls}">{conf} · {conf_pct}%</span>
          </div>
          <div style="font-size:0.79rem;color:#4a7880;margin-top:0.55rem;line-height:1.5;">{fa.get('primary_reason','')}</div>
        </div>""", unsafe_allow_html=True)

        # ── TRUST SCORES ──
        cs  = ts.get("company_score", 0)
        dms = ts.get("decision_maker_score", 0)
        ovs = ts.get("overall_score", 0)
        st.markdown('<div class="dd-card">', unsafe_allow_html=True)
        st.markdown('<div class="dd-card-title">Trust Scores</div>', unsafe_allow_html=True)
        score_bar("Company", cs)
        score_bar("Decision Maker", dms)
        st.markdown('<div style="border-top:1px solid #0e2233;margin:0.45rem 0 0.6rem;"></div>', unsafe_allow_html=True)
        score_bar("Overall", ovs)
        co_rat = ts.get("company_score_rationale","")
        dm_rat = ts.get("decision_maker_score_rationale","")
        if co_rat:
            st.markdown(f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.65rem;color:#2a5060;margin-top:0.5rem;line-height:1.5;"><span style="color:#3a7080;">Co.:</span> {co_rat}</div>', unsafe_allow_html=True)
        if dm_rat:
            st.markdown(f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.65rem;color:#2a5060;margin-top:0.25rem;line-height:1.5;"><span style="color:#3a7080;">DM:</span> {dm_rat}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── RISK FLAGS ──
        reds   = rd.get("red_flags", [])
        yellows= rd.get("yellow_flags", [])
        greens = rd.get("green_signals", [])
        if reds or yellows or greens:
            st.markdown('<div class="dd-card">', unsafe_allow_html=True)
            st.markdown('<div class="dd-card-title">Risk Detection</div>', unsafe_allow_html=True)
            flags(reds,   "fd-red",    "RED")
            flags(yellows,"fd-yellow", "YLW")
            flags(greens, "fd-green",  "GRN")
            st.markdown('</div>', unsafe_allow_html=True)

        # ── CROSS-VERIFICATION ──
        matches  = cv.get("matches", [])
        misses   = cv.get("mismatches", [])
        unverf   = cv.get("unverifiable", [])
        if matches or misses or unverf:
            st.markdown('<div class="dd-card">', unsafe_allow_html=True)
            st.markdown('<div class="dd-card-title">Cross-Verification</div>', unsafe_allow_html=True)
            flags(matches, "fd-match", "OK")
            flags(misses,  "fd-miss",  "FAIL")
            flags(unverf,  "fd-info",  "?")
            st.markdown('</div>', unsafe_allow_html=True)

        # ── EVIDENCE ──
        sup = ea.get("supporting_evidence", [])
        con = ea.get("contradicting_signals", [])
        neu = ea.get("neutral_observations", [])
        if sup or con or neu:
            st.markdown('<div class="dd-card">', unsafe_allow_html=True)
            st.markdown('<div class="dd-card-title">Evidence Aggregation</div>', unsafe_allow_html=True)
            evidence(sup, "ep")
            evidence(con, "en")
            evidence(neu, "eu")
            st.markdown('</div>', unsafe_allow_html=True)

        # ── SUMMARY ──
        summary = fa.get("summary","")
        if summary:
            st.markdown('<div class="dd-card">', unsafe_allow_html=True)
            st.markdown('<div class="dd-card-title">Summary</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="sumbox">{summary}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── ACTION ITEMS ──
        actions = fa.get("action_items", [])
        if actions:
            st.markdown('<div class="dd-card">', unsafe_allow_html=True)
            st.markdown('<div class="dd-card-title">Action Items</div>', unsafe_allow_html=True)
            for a in actions:
                st.markdown(f'<div class="ai"><span class="aa">→</span><span>{a}</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── PIPELINE COMPLETE ──
        st.markdown('<div class="slabel" style="margin-top:1rem;">Pipeline Complete</div>', unsafe_allow_html=True)
        st.markdown(pipeline_html(8), unsafe_allow_html=True)

        # ── DOWNLOAD + NEW ANALYSIS ──
        full_report = {"input": inp, "analysis": result}
        slug = inp.get("company_name","report").lower().replace(" ","_")[:25]
        st.download_button(
            label="↓  DOWNLOAD REPORT  (JSON)",
            data=json.dumps(full_report, indent=2, default=str),
            file_name=f"due_diligence_{slug}.json",
            mime="application/json",
        )
        if st.button("← New Analysis"):
            st.session_state.state  = "idle"
            st.session_state.result = None
            st.rerun()

    # ── IDLE STATE ────────────────────────────────────────────────────────────
    else:
        st.markdown("""
        <div style="margin-top:2.5rem;text-align:center;">
          <div style="font-size:2.2rem;opacity:0.15;margin-bottom:0.9rem;">◈</div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:0.68rem;letter-spacing:0.25em;color:#1a4a5a;">AWAITING TARGET INPUT</div>
          <div style="font-size:0.72rem;color:#152030;margin-top:0.4rem;font-family:'IBM Plex Mono',monospace;">Fill in the form on the left and click RUN ANALYSIS</div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="slabel" style="margin-top:2.5rem;">7-Stage Pipeline</div>', unsafe_allow_html=True)
        st.markdown(pipeline_html(0), unsafe_allow_html=True)

        st.markdown("""
        <div style="margin-top:1.5rem;font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#0e2030;line-height:2.2;">
          Stage 1 — Input Validation &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[ OpenAI GPT-4o ]<br>
          Stage 2 — Data Collection &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[ Apify · Exa ]<br>
          Stage 3 — Cross-Verification &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[ Exa · OpenAI GPT-4o ]<br>
          Stage 4 — Risk Detection &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[ Exa · Apify · OpenAI GPT-4o ]<br>
          Stage 5 — Trust Scoring &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[ Exa · OpenAI GPT-4o ]<br>
          Stage 6 — Evidence Aggregation &nbsp;[ Exa · OpenAI GPT-4o ]<br>
          Stage 7 — Final Assessment &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[ OpenAI GPT-4o ]
        </div>""", unsafe_allow_html=True)
