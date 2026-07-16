"""Streamlit front end for the BFSI structural demo, the shareable deploy target.

Streamlit Cloud runs a Streamlit script (not uvicorn), so this UI calls the
five-layer logic in process. The look is a calm enterprise palette (a trustworthy
indigo on a soft off-white canvas, restrained icons, a five-layer pipeline) with
a conversational assistant, "Ava", built on st.chat_message.

Run locally:   streamlit run streamlit_app.py
Deploy:        share.streamlit.io, repo, branch main, main file streamlit_app.py
"""
from __future__ import annotations

import base64
import os
import time

os.environ.setdefault("SEED_PARTIES", "500")

import streamlit as st

from app import bootstrap
from app.agent import agent
from app.layer1_data import db
from app.layer4_decisioning.decisioning import get_engine
from app.layer5_governance import audit, fairness, governance

st.set_page_config(page_title="NBA Studio, BFSI personalization",
                   page_icon="\U0001F4CA", layout="wide", initial_sidebar_state="collapsed")

_AVA_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">'
            '<circle cx="20" cy="20" r="20" fill="#3B4D8F"/>'
            '<path d="M13 22a7 7 0 0014 0" stroke="#fff" stroke-width="2.2" fill="none" stroke-linecap="round"/>'
            '<circle cx="15" cy="17" r="1.3" fill="#fff"/><circle cx="25" cy="17" r="1.3" fill="#fff"/></svg>')
AVA = "data:image/svg+xml;base64," + base64.b64encode(_AVA_SVG.encode()).decode()

# --------------------------------------------------------------------------- #
# Design system
# --------------------------------------------------------------------------- #
st.markdown("""
<style>
:root{--brand:#3B4D8F;--brand-600:#33427A;--brand-700:#2B3566;--brand-50:#EEF1F8;
  --ink:#1C2430;--muted:#6B7686;--line:#E4E7EE;--good:#2F855A;--warn:#B7791F;--bad:#C05252;}
#MainMenu,header[data-testid="stHeader"],footer{visibility:hidden;height:0}
.block-container{padding-top:1rem;max-width:1200px}
.hero{background:linear-gradient(180deg,#2B3566,#33427A);color:#fff;border-radius:14px;
  padding:22px 26px;box-shadow:0 6px 20px rgba(16,24,40,.08)}
.hero .b{display:flex;align-items:center;gap:9px;font-weight:600;font-size:15px;margin-bottom:12px}
.hero .b small{font-weight:400;opacity:.82;font-size:11.5px}
.hero h1{margin:0;font-size:23px;font-weight:700;letter-spacing:-.02em;line-height:1.25;max-width:760px}
.hero p{margin:6px 0 0;opacity:.85;font-size:13.5px;max-width:660px}
.kpis{display:flex;gap:11px;margin-top:18px;flex-wrap:wrap}
.kpi{flex:1;min-width:130px;background:rgba(255,255,255,.09);border:1px solid rgba(255,255,255,.14);
  border-radius:10px;padding:11px 13px}
.kpi .v{font-size:18px;font-weight:700}.kpi .l{font-size:10.5px;opacity:.8;text-transform:uppercase;letter-spacing:.05em}
.pipe{display:flex;gap:8px;align-items:stretch;margin:16px 0 4px}
.pnode{flex:1;background:#fff;border:1px solid var(--line);border-radius:11px;padding:10px 11px;text-align:center;
  box-shadow:0 1px 2px rgba(16,24,40,.04)}
.pnode .n{font-size:10.5px;color:var(--muted);font-weight:600;letter-spacing:.04em}
.pnode .t{font-weight:600;color:var(--brand);margin-top:2px;font-size:13px}
.pnode .d{font-size:10.5px;color:var(--muted)}
.parr{align-self:center;color:#C3C9D4}
.wcard{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px;display:flex;gap:12px;
  align-items:center;margin-top:6px;box-shadow:0 1px 2px rgba(16,24,40,.04)}
.wcard .ico{width:40px;height:40px;border-radius:10px;background:var(--brand-50);color:var(--brand);
  display:grid;place-items:center}
.wcard .ico svg{width:20px;height:20px;stroke:currentColor;fill:none;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}
.wcard .a{font-weight:700;font-size:15px}.wcard .m{color:var(--muted);font-size:12px}
.pill{display:inline-block;padding:5px 10px;border-radius:7px;font-size:12px;font-weight:600;margin:3px 5px 0 0}
.pill.ok{background:#EAF3EE;color:var(--good)}.pill.slow{background:#F6EAEA;color:var(--bad)}
.pill.warn{background:#F6EFDF;color:var(--warn)}.pill.n{background:var(--brand-50);color:var(--brand)}
.reason{display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid var(--line);font-size:13px}
.reason .up{color:var(--good);font-weight:600}.reason .down{color:var(--bad);font-weight:600}
.bar{display:flex;align-items:center;gap:10px;margin:6px 0}
.bar .bl{width:96px;font-size:12px;color:var(--muted);text-transform:capitalize}
.bar .tk{flex:1;height:7px;border-radius:6px;background:#F1F3F7;border:1px solid var(--line);overflow:hidden}
.bar .fl{height:100%;background:var(--brand)}
.bar .bv{width:46px;text-align:right;font-weight:600;font-size:12px}
.seclab{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-weight:600;margin:14px 0 6px}
.escb{padding:10px 13px;border-radius:10px;background:#F6EFDF;border:1px solid var(--warn);color:#8A5A12;font-weight:500;font-size:13px}
.okb{padding:10px 13px;border-radius:10px;background:#EAF3EE;border:1px solid var(--good);color:#23663F;font-weight:500;font-size:13px}
.stepline{font-size:12.5px;color:var(--muted);padding:2px 0}.stepline b{color:var(--ink);text-transform:capitalize}
div[data-testid="stChatMessage"]{background:#fff;border:1px solid var(--line);border-radius:12px}
.stButton>button{border-radius:8px;border:1px solid var(--line);color:var(--brand);font-weight:500}
.stButton>button:hover{border-color:var(--brand);background:var(--brand-50)}
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner="Bootstrapping five layers (seed, features, models, policies)")
def _init():
    bootstrap.ensure()
    return get_engine()


engine = _init()


@st.cache_data
def _personas(limit: int = 18):
    rows = db.fetchall(
        "SELECT party_id, domain, journey_stage, risk_band FROM party LIMIT ?", (limit,))
    return {f"{p}, {d}/{s}, {r}": p for p, d, s, r in rows}


_ICON = {
    "shield": '<path d="M12 3l7 3v5c0 4-3 7-7 8-4-1-7-4-7-8V6l7-3z"/>',
    "bank": '<path d="M3 10l9-5 9 5"/><path d="M5 10v8M9 10v8M15 10v8M19 10v8M3 21h18"/>',
    "card": '<rect x="3" y="6" width="18" height="12" rx="2"/><path d="M3 10h18"/>',
    "chart": '<path d="M4 19V5M4 19h16M8 15l3-4 3 2 4-6"/>',
    "handshake": '<path d="M8 12l3 3 5-5"/><path d="M3 10l4-4 5 3 5-3 4 4"/>',
    "headset": '<path d="M4 13v-1a8 8 0 0116 0v1"/><rect x="3" y="13" width="4" height="6" rx="1"/><rect x="17" y="13" width="4" height="6" rx="1"/>',
    "spark": '<path d="M12 4v16M4 12h16"/>',
}


def _icon_svg(aid: str) -> str:
    key = ("shield" if "fraud" in aid else "bank" if "loan" in aid else "card" if "card" in aid
           else "chart" if "wealth" in aid else "handshake" if "retain" in aid
           else "headset" if "support" in aid else "spark")
    return f'<svg viewBox="0 0 24 24">{_ICON[key]}</svg>'


def _pretty(aid: str) -> str:
    return aid.replace("_", " ").title()


personas = _personas()
backends = db.backends()

st.markdown(f"""
<div class="hero">
  <div class="b">NBA Studio &nbsp;<small>Real-time, agentic personalization for BFSI</small></div>
  <h1>A personalized next-best-action for every interaction, decided, explained and audited in under 98 ms.</h1>
  <p>Five composable layers, an agent that escalates when the stakes are high, and a full reason and audit trail on every decision.</p>
  <div class="kpis">
    <div class="kpi"><div class="v">98 ms</div><div class="l">Latency SLO, p99</div></div>
    <div class="kpi"><div class="v">{audit.count():,}</div><div class="l">Audit rows</div></div>
    <div class="kpi"><div class="v">{backends['ledger']}, {backends['online_store']}</div><div class="l">Backends</div></div>
    <div class="kpi"><div class="v">{'langgraph' if agent._HAS_LANGGRAPH else 'agentic loop'}</div><div class="l">Agent runtime</div></div>
  </div>
</div>
<div class="pipe">
  <div class="pnode"><div class="n">L1</div><div class="t">Data</div><div class="d">ledger, hot store</div></div>
  <div class="parr">&rsaquo;</div>
  <div class="pnode"><div class="n">L2</div><div class="t">Features</div><div class="d">online, sub ms</div></div>
  <div class="parr">&rsaquo;</div>
  <div class="pnode"><div class="n">L3</div><div class="t">Models</div><div class="d">propensity, uplift, fraud</div></div>
  <div class="parr">&rsaquo;</div>
  <div class="pnode"><div class="n">L4</div><div class="t">Decisioning</div><div class="d">rules, bandit</div></div>
  <div class="parr">&rsaquo;</div>
  <div class="pnode"><div class="n">L5</div><div class="t">Governance</div><div class="d">reasons, fairness, audit</div></div>
</div>
""", unsafe_allow_html=True)

left, right = st.columns(2, gap="large")

# --------------------------------------------------------------------------- #
# Decision studio
# --------------------------------------------------------------------------- #
with left:
    st.markdown("#### Next-best-action, Layer 4 and 5")
    persona_label = st.selectbox("Customer, non-PII", list(personas), key="dec_party")
    event_type = st.selectbox("Live context signal",
                              ["session_start", "large_transfer_attempt",
                               "product_page_view", "card_declined"])
    if st.button("Recommend next-best-action", type="primary", use_container_width=True):
        pid = personas[persona_label]
        event = {"event_type": event_type,
                 "amount": 4000 if event_type == "large_transfer_attempt" else 0}
        t0 = time.perf_counter()
        decision = engine.decide(pid, event)
        assessment = governance.assess(engine, decision)
        latency_ms = (time.perf_counter() - t0) * 1000.0
        record = governance.build_record(decision, assessment, "web", latency_ms)
        audit.write(record)
        st.session_state["last_decision"] = (decision, record, latency_ms)

    if "last_decision" in st.session_state:
        decision, record, latency_ms = st.session_state["last_decision"]
        w = decision["winner"]
        st.markdown(f"""
        <div class="wcard"><div class="ico">{_icon_svg(w['action_id'])}</div>
          <div><div class="a">{_pretty(w['action_id'])}</div><div class="m">{w['action_id']}</div></div></div>
        <div style="margin-top:10px">
          <span class="pill {'ok' if latency_ms < 98 else 'slow'}">{latency_ms:.2f} ms, SLO 98</span>
          <span class="pill {'warn' if record['fairness_flag']=='adverse_impact' else 'ok'}">fairness, {record['fairness_flag']}</span>
          <span class="pill n">expected value {w['expected_value']}</span>
        </div>
        <div class="seclab">Why, reason codes</div>
        {''.join(f'<div class="reason"><span>{r["label"]}</span><span class="{"up" if r["direction"]=="increases" else "down"}">{r["direction"]}, {"+" if r["contribution"]>0 else ""}{r["contribution"]}</span></div>' for r in record['reason_codes'])}
        <div class="seclab">Model signals</div>
        {''.join(f'<div class="bar"><span class="bl">{k}</span><div class="tk"><div class="fl" style="width:{min(100,max(3,v*100)):.0f}%"></div></div><span class="bv">{v:.3f}</span></div>' for k,v in decision['model_scores'].items())}
        """, unsafe_allow_html=True)
        rej = ", ".join(f"{_pretty(r['action_id'])} ({r['reason']})" for r in decision["rejected"])
        if rej:
            st.markdown(f'<div class="seclab">Ruled out</div>'
                        f'<div style="font-size:12px;color:#6B7686">{rej}</div>', unsafe_allow_html=True)
        with st.expander(f"Audit record, {record['decision_id']}"):
            st.json(audit.get(record["decision_id"]))

# --------------------------------------------------------------------------- #
# Ava, conversational assistant
# --------------------------------------------------------------------------- #
with right:
    st.markdown("#### Ava, virtual banking assistant")
    st.selectbox("Acting for customer", list(personas), key="agent_party")

    if "chat" not in st.session_state:
        st.session_state.chat = [{"role": "assistant", "greet": True}]

    def _submit(goal: str):
        pid = personas[st.session_state["agent_party"]]
        steps, final = [], None
        for ev in agent.run_stream(pid, goal):
            if ev["type"] == "final":
                final = ev
            else:
                steps.append(ev)
        st.session_state.chat.append({"role": "user", "text": goal})
        st.session_state.chat.append({"role": "assistant", "steps": steps, "final": final})

    st.caption("Quick actions")
    c1, c2, c3 = st.columns(3)
    if c1.button("Loan 50,000", use_container_width=True):
        _submit("I want a pre-approved loan of 50000")
    if c2.button("Dispute 15,000", use_container_width=True):
        _submit("Dispute an unauthorized charge of 15000")
    if c3.button("Financial tip", use_container_width=True):
        _submit("Give me a quick financial tip")

    for m in st.session_state.chat:
        with st.chat_message(m["role"], avatar=AVA if m["role"] == "assistant" else None):
            if m.get("greet"):
                st.write("Hi, I am **Ava**. I can act on a customer request end to end, "
                         "and I bring in a human when the stakes are high. "
                         "Use a quick action or type below.")
            elif m["role"] == "user":
                st.write(m["text"])
            else:
                for ev in m.get("steps", []):
                    esc = ev["node"] == "escalate"
                    st.markdown(f'<div class="stepline">{"!" if esc else "•"} '
                                f'<b>{ev["node"]}</b>, {ev["detail"]}</div>', unsafe_allow_html=True)
                f = m.get("final")
                if f:
                    if f["escalated"]:
                        st.markdown('<div class="escb">Handed to a human specialist. '
                                    + f["answer"].replace("Escalated to human review: ", "")
                                    + '</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="okb">{f["answer"]}</div>', unsafe_allow_html=True)
                    st.caption(f"confidence {f['confidence']}, {f['engine']}")

    with st.form("ava_composer", clear_on_submit=True):
        msg = st.text_input("msg", label_visibility="collapsed",
                            placeholder="Ask Ava to handle something")
        if st.form_submit_button("Send", type="primary", use_container_width=True) and msg.strip():
            _submit(msg.strip())
            st.rerun()

with st.sidebar:
    st.header("Governance")
    st.json({"drift": governance.drift_snapshot(), "fairness": fairness.snapshot(),
             "human_queue": (db.fetchone("SELECT COUNT(*) FROM human_queue") or [0])[0]})
    st.caption("Structural reference demo, synthetic data and illustrative scores. "
               "The architecture, latency and audit trail are the point.")
