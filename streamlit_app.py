"""Streamlit front-end for the BFSI structural demo — the shareable deploy target.

Streamlit Cloud runs a Streamlit script (not uvicorn), so this UI calls the
five-layer logic in-process. The look is an enterprise-analytics design system
(violet→magenta gradient, KPI cards, a five-layer pipeline) with an Erica-style
conversational assistant ("Ava") built on st.chat_message.

Run locally:   streamlit run streamlit_app.py
Deploy:        share.streamlit.io → repo, branch main, main file streamlit_app.py
"""
from __future__ import annotations

import os
import time

os.environ.setdefault("SEED_PARTIES", "500")

import streamlit as st

from app import bootstrap
from app.agent import agent
from app.layer1_data import db
from app.layer4_decisioning.decisioning import get_engine
from app.layer5_governance import audit, fairness, governance

st.set_page_config(page_title="NBA Studio · BFSI personalization",
                   page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

# --------------------------------------------------------------------------- #
# Design system (injected CSS)
# --------------------------------------------------------------------------- #
st.markdown("""
<style>
:root{--violet:#6D28D9;--magenta:#C026D3;--ink:#171334;--muted:#6B6690;--line:#E9E6F5;}
#MainMenu,header[data-testid="stHeader"],footer{visibility:hidden;height:0}
.block-container{padding-top:1.1rem;max-width:1240px}
.hero{background:linear-gradient(120deg,#6D28D9 0%,#9333EA 45%,#C026D3 100%);color:#fff;
  border-radius:18px;padding:22px 26px;box-shadow:0 18px 48px rgba(76,29,149,.22)}
.hero h1{margin:0;font-size:25px;font-weight:800;letter-spacing:-.03em;line-height:1.2}
.hero p{margin:6px 0 0;opacity:.92;font-size:14px;max-width:760px}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;font-size:16px;margin-bottom:12px}
.brand small{font-weight:500;opacity:.85;font-size:11.5px}
.kpis{display:flex;gap:12px;margin-top:16px;flex-wrap:wrap}
.kpi{flex:1;min-width:130px;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.22);
  border-radius:13px;padding:11px 14px}
.kpi .v{font-size:21px;font-weight:800}.kpi .l{font-size:11px;opacity:.85;text-transform:uppercase;letter-spacing:.06em}
.pipe{display:flex;gap:8px;align-items:stretch;margin:16px 0 6px}
.pnode{flex:1;background:#fff;border:1px solid var(--line);border-radius:13px;padding:11px 12px;
  box-shadow:0 6px 20px rgba(76,29,149,.07);text-align:center}
.pnode .n{font-size:11px;color:var(--muted);font-weight:800;letter-spacing:.05em}
.pnode .t{font-weight:800;color:var(--violet);margin-top:2px;font-size:13.5px}
.pnode .d{font-size:11px;color:var(--muted)}
.parr{align-self:center;color:#CFC9EA;font-weight:800}
.wcard{background:#fff;border:1px solid var(--line);border-radius:14px;padding:15px;
  box-shadow:0 6px 20px rgba(76,29,149,.07);display:flex;gap:13px;align-items:center;margin-top:6px}
.wcard .ico{width:44px;height:44px;border-radius:12px;font-size:22px;display:grid;place-items:center;
  background:linear-gradient(120deg,#6D28D9,#C026D3)}
.wcard .a{font-weight:800;font-size:16px}.wcard .m{color:var(--muted);font-size:12px}
.pill{display:inline-block;padding:5px 11px;border-radius:999px;font-size:12px;font-weight:700;margin:3px 5px 0 0}
.pill.ok{background:rgba(22,163,74,.12);color:#16A34A}.pill.slow{background:rgba(220,38,38,.12);color:#DC2626}
.pill.warn{background:rgba(217,119,6,.14);color:#D97706}.pill.ev{background:rgba(109,40,217,.1);color:#6D28D9}
.reason{display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px dashed var(--line);font-size:13px}
.reason .up{color:#16A34A;font-weight:600}.reason .down{color:#DC2626;font-weight:600}
.bar{display:flex;align-items:center;gap:10px;margin:6px 0}
.bar .bl{width:92px;font-size:12px;color:var(--muted);text-transform:capitalize}
.bar .track{flex:1;height:8px;border-radius:99px;background:#F4F3FA;border:1px solid var(--line);overflow:hidden}
.bar .fill{height:100%;background:linear-gradient(120deg,#6D28D9,#C026D3)}
.bar .bv{width:46px;text-align:right;font-weight:700;font-size:12px}
.seclab{font-size:11px;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);font-weight:800;margin:14px 0 6px}
.escb{padding:11px 13px;border-radius:11px;background:rgba(217,119,6,.1);border:1px solid rgba(217,119,6,.3);
  color:#B45309;font-weight:600;font-size:13px}
.okb{padding:11px 13px;border-radius:11px;background:rgba(22,163,74,.1);border:1px solid rgba(22,163,74,.3);
  color:#15803D;font-weight:600;font-size:13px}
.stepline{font-size:12.5px;color:var(--muted);padding:2px 0}
.stepline b{color:var(--ink);text-transform:capitalize}
div[data-testid="stChatMessage"]{background:#fff;border:1px solid var(--line);border-radius:14px}
.stButton>button{border-radius:999px;border:1px solid var(--line);color:var(--violet);font-weight:600}
.stButton>button:hover{border-color:var(--violet);background:rgba(109,40,217,.06)}
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner="Bootstrapping five layers (seed → features → models → policies)…")
def _init():
    bootstrap.ensure()
    return get_engine()


engine = _init()


@st.cache_data
def _personas(limit: int = 18):
    rows = db.fetchall(
        "SELECT party_id, domain, journey_stage, risk_band FROM party LIMIT ?", (limit,))
    return {f"{p} · {d}/{s} · {r}": p for p, d, s, r in rows}


def _icon(aid: str) -> str:
    for key, ico in (("fraud", "🛡️"), ("loan", "🏦"), ("card", "💳"), ("wealth", "📈"),
                     ("retain", "🤝"), ("support", "🎧")):
        if key in aid:
            return ico
    return "✨"


def _pretty(aid: str) -> str:
    return aid.replace("_", " ").title()


personas = _personas()
backends = db.backends()

# --------------------------------------------------------------------------- #
# Hero + KPIs
# --------------------------------------------------------------------------- #
st.markdown(f"""
<div class="hero">
  <div class="brand">🌀 NBA Studio &nbsp;<small>Real-time · agentic personalization for BFSI</small></div>
  <h1>Every interaction, a personalized next-best-action — decided, explained and audited in under 98&nbsp;ms.</h1>
  <p>Five composable layers, an agent that escalates when the stakes are high, and a full reason + audit trail on every decision.</p>
  <div class="kpis">
    <div class="kpi"><div class="v">98 ms</div><div class="l">Latency SLO (p99)</div></div>
    <div class="kpi"><div class="v">{audit.count():,}</div><div class="l">Audit rows</div></div>
    <div class="kpi"><div class="v">{backends['ledger']} · {backends['online_store']}</div><div class="l">Backends</div></div>
    <div class="kpi"><div class="v">{'langgraph' if agent._HAS_LANGGRAPH else 'agentic loop'}</div><div class="l">Agent runtime</div></div>
  </div>
</div>
""", unsafe_allow_html=True)

# Five-layer pipeline
st.markdown("""
<div class="pipe">
  <div class="pnode"><div class="n">L1</div><div class="t">Data</div><div class="d">ledger + hot store</div></div>
  <div class="parr">→</div>
  <div class="pnode"><div class="n">L2</div><div class="t">Features</div><div class="d">online, sub-ms</div></div>
  <div class="parr">→</div>
  <div class="pnode"><div class="n">L3</div><div class="t">Models</div><div class="d">propensity·uplift·fraud</div></div>
  <div class="parr">→</div>
  <div class="pnode"><div class="n">L4</div><div class="t">Decisioning</div><div class="d">rules + bandit</div></div>
  <div class="parr">→</div>
  <div class="pnode"><div class="n">L5</div><div class="t">Governance</div><div class="d">reasons·fairness·audit</div></div>
</div>
""", unsafe_allow_html=True)

left, right = st.columns(2, gap="large")

# --------------------------------------------------------------------------- #
# Decision studio
# --------------------------------------------------------------------------- #
with left:
    st.markdown("#### 🎯 Next-best-action &nbsp;·&nbsp; Layer 4·5")
    persona_label = st.selectbox("Customer (non-PII)", list(personas), key="dec_party")
    event_type = st.selectbox("Live context signal",
                              ["session_start", "large_transfer_attempt",
                               "product_page_view", "card_declined"])
    if st.button("Recommend next-best-action", type="primary", use_container_width=True):
        party_id = personas[persona_label]
        event = {"event_type": event_type,
                 "amount": 4000 if event_type == "large_transfer_attempt" else 0}
        t0 = time.perf_counter()
        decision = engine.decide(party_id, event)
        assessment = governance.assess(engine, decision)
        latency_ms = (time.perf_counter() - t0) * 1000.0
        record = governance.build_record(decision, assessment, "web", latency_ms)
        audit.write(record)
        st.session_state["last_decision"] = (decision, record, latency_ms)

    if "last_decision" in st.session_state:
        decision, record, latency_ms = st.session_state["last_decision"]
        w = decision["winner"]
        st.markdown(f"""
        <div class="wcard"><div class="ico">{_icon(w['action_id'])}</div>
          <div><div class="a">{_pretty(w['action_id'])}</div><div class="m">{w['action_id']}</div></div></div>
        <div style="margin-top:10px">
          <span class="pill {'ok' if latency_ms < 98 else 'slow'}">{latency_ms:.2f} ms · SLO 98</span>
          <span class="pill {'warn' if record['fairness_flag']=='adverse_impact' else 'ok'}">fairness: {record['fairness_flag']}</span>
          <span class="pill ev">expected value {w['expected_value']}</span>
        </div>
        <div class="seclab">Why — reason codes</div>
        {''.join(f'<div class="reason"><span>{r["label"]}</span><span class="{"up" if r["direction"]=="increases" else "down"}">{r["direction"]} · {"+" if r["contribution"]>0 else ""}{r["contribution"]}</span></div>' for r in record['reason_codes'])}
        <div class="seclab">Model signals</div>
        {''.join(f'<div class="bar"><span class="bl">{k}</span><div class="track"><div class="fill" style="width:{min(100,max(3,v*100)):.0f}%"></div></div><span class="bv">{v:.3f}</span></div>' for k,v in decision['model_scores'].items())}
        """, unsafe_allow_html=True)
        rej = " · ".join(f"{_pretty(r['action_id'])} ({r['reason']})" for r in decision["rejected"])
        if rej:
            st.markdown(f'<div class="seclab">Ruled out</div><div style="font-size:12px;color:#6B6690">{rej}</div>',
                        unsafe_allow_html=True)
        with st.expander(f"Audit record · {record['decision_id']}"):
            st.json(audit.get(record["decision_id"]))

# --------------------------------------------------------------------------- #
# Ava — conversational assistant (Erica-style)
# --------------------------------------------------------------------------- #
with right:
    st.markdown("#### 🌀 Ava &nbsp;·&nbsp; virtual banking assistant")
    agent_label = st.selectbox("Acting for customer", list(personas), key="agent_party")

    if "chat" not in st.session_state:
        st.session_state.chat = [{"role": "assistant", "greet": True}]

    def _submit(goal: str):
        pid = personas[st.session_state["agent_party"]]
        steps, final = [], None
        for ev in agent.run_stream(pid, goal):
            (steps.append(ev) if ev["type"] != "final" else None)
            if ev["type"] == "final":
                final = ev
        st.session_state.chat.append({"role": "user", "text": goal})
        st.session_state.chat.append({"role": "assistant", "steps": steps, "final": final})

    st.caption("Quick actions")
    c1, c2, c3 = st.columns(3)
    if c1.button("Loan ₹50,000", use_container_width=True):
        _submit("I want a pre-approved loan of 50000")
    if c2.button("Dispute ₹15,000", use_container_width=True):
        _submit("Dispute an unauthorized charge of 15000")
    if c3.button("Financial tip", use_container_width=True):
        _submit("Give me a quick financial tip")

    # Render the conversation.
    for m in st.session_state.chat:
        with st.chat_message(m["role"], avatar="🌀" if m["role"] == "assistant" else "🧑"):
            if m.get("greet"):
                st.write("Hi, I'm **Ava**. I can act on a customer's request end-to-end — "
                         "and I'll bring in a human when the stakes are high. "
                         "Use a quick action or type below.")
            elif m["role"] == "user":
                st.write(m["text"])
            else:
                for ev in m.get("steps", []):
                    esc = ev["node"] == "escalate"
                    st.markdown(f'<div class="stepline">{"⚠️" if esc else "•"} '
                                f'<b>{ev["node"]}</b> — {ev["detail"]}</div>', unsafe_allow_html=True)
                f = m.get("final")
                if f:
                    if f["escalated"]:
                        st.markdown(f'<div class="escb">⚠️ Handed to a human specialist — '
                                    f'{f["answer"].replace("Escalated to human review: ", "")}</div>',
                                    unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="okb">✓ {f["answer"]}</div>', unsafe_allow_html=True)
                    st.caption(f"confidence {f['confidence']} · {f['engine']}")

    # A form (not st.chat_input, which can't be nested in a column) keeps the
    # composer inside Ava's panel.
    with st.form("ava_composer", clear_on_submit=True):
        msg = st.text_input("msg", label_visibility="collapsed",
                            placeholder="Ask Ava to handle something…")
        if st.form_submit_button("Send", type="primary", use_container_width=True) and msg.strip():
            _submit(msg.strip())
            st.rerun()

# Sidebar — governance
with st.sidebar:
    st.header("Governance")
    st.json({"drift": governance.drift_snapshot(), "fairness": fairness.snapshot(),
             "human_queue": (db.fetchone("SELECT COUNT(*) FROM human_queue") or [0])[0]})
    st.caption("Structural reference demo: synthetic data, illustrative scores. "
               "The architecture, latency and audit trail are the point.")
