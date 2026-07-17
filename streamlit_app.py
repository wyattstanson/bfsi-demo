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

st.set_page_config(page_title="Aria, BFSI Personalization Platform",
                   layout="wide", initial_sidebar_state="collapsed")

MODES = [
    ("Concierge", "Customer", "customer"),
    ("Co-pilot", "Advisor", "advisor"),
    ("Control Tower", "Executive", "executive"),
    ("Assurance", "Regulator", "regulator"),
    ("Engine Room", "AI engineer", "developer"),
]
DEV_PASSCODE = os.getenv("DEV_PASSCODE", "Aryansh@Tredence")

_AVA = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">'
        '<rect width="40" height="40" rx="10" fill="#111317"/>'
        '<text x="20" y="26" font-size="18" font-weight="800" text-anchor="middle" fill="#fff">A</text>'
        '<circle cx="27" cy="14" r="3" fill="#F1592A"/></svg>')
AVA = "data:image/svg+xml;base64," + base64.b64encode(_AVA.encode()).decode()

if "theme" not in st.session_state:
    st.session_state.theme = "light"
DARK = st.session_state.theme == "dark"

PAL = {
    "bg": "#0E0F12" if DARK else "#FAFAF8", "panel": "#17191E" if DARK else "#FFFFFF",
    "ink": "#ECEDEB" if DARK else "#141619", "muted": "#98A0AB" if DARK else "#6B7180",
    "line": "#282C33" if DARK else "#E9E8E3", "soft": "#15171B" if DARK else "#F3F3F0",
}

st.markdown(f"""
<style>
:root{{--orange:#F1592A;--orange-600:#D84A1D;--ink:{PAL['ink']};--muted:{PAL['muted']};
  --line:{PAL['line']};--panel:{PAL['panel']};--soft:{PAL['soft']};--good:#1F9D57;--warn:#B4791A;--bad:#D64541;}}
.stApp{{background:{PAL['bg']}}}
#MainMenu,header[data-testid="stHeader"],footer{{visibility:hidden;height:0}}
.block-container{{padding-top:.8rem;max-width:1180px}}
h1,h2,h3,h4,p,span,label,div{{color:{PAL['ink']}}}
.hero{{background:linear-gradient(180deg,#1c1e24,#111317);color:#fff;border-radius:14px;padding:22px 26px}}
.hero .b{{display:flex;align-items:center;gap:9px;font-weight:700;font-size:15px;margin-bottom:10px;color:#fff}}
.hero .b small{{font-weight:400;opacity:.8;font-size:11.5px}}
.hero h1{{margin:0;font-size:24px;font-weight:800;letter-spacing:-.02em;color:#fff}}
.hero p{{margin:6px 0 0;opacity:.85;font-size:13.5px;color:#fff;max-width:680px}}
.kpis{{display:flex;gap:11px;margin-top:16px;flex-wrap:wrap}}
.kpi{{flex:1;min-width:130px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.14);border-radius:10px;padding:11px 13px}}
.kpi .v{{font-size:18px;font-weight:800;color:#fff}}.kpi .l{{font-size:10.5px;opacity:.8;text-transform:uppercase;letter-spacing:.05em;color:#fff}}
.pipe{{display:flex;gap:8px;margin:16px 0 4px}}
.pnode{{flex:1;background:var(--panel);border:1px solid var(--line);border-radius:11px;padding:10px 11px;text-align:center}}
.pnode .n{{font-size:10.5px;color:var(--muted);font-weight:700}}.pnode .t{{font-weight:700;color:var(--orange-600);font-size:13px}}.pnode .d{{font-size:10.5px;color:var(--muted)}}
.parr{{align-self:center;color:var(--line)}}
.wcard{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:15px;margin-top:6px}}
.wcard .a{{font-weight:800;font-size:16px}}.wcard .m{{color:var(--muted);font-size:12px}}
.pill{{display:inline-block;padding:5px 10px;border-radius:8px;font-size:12px;font-weight:600;margin:3px 5px 0 0}}
.pill.ok{{background:rgba(31,157,87,.14);color:var(--good)}}.pill.slow{{background:rgba(214,69,65,.14);color:var(--bad)}}
.pill.warn{{background:rgba(180,121,26,.16);color:var(--warn)}}.pill.n{{background:rgba(241,89,42,.12);color:var(--orange-600)}}
.reason{{display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid var(--line);font-size:13px}}
.reason .up{{color:var(--good);font-weight:600}}.reason .down{{color:var(--bad);font-weight:600}}
.bar{{display:flex;align-items:center;gap:10px;margin:6px 0}}
.bar .bl{{width:150px;font-size:12px;color:var(--muted)}}
.bar .tk{{flex:1;height:8px;border-radius:6px;background:var(--soft);border:1px solid var(--line);overflow:hidden}}
.bar .fl{{height:100%;background:var(--orange)}}.bar .bv{{width:50px;text-align:right;font-weight:700;font-size:12px}}
.seclab{{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-weight:700;margin:14px 0 6px}}
.ccard{{background:var(--soft);border:1px solid var(--line);border-radius:18px;padding:22px}}
.ctitle{{font-size:21px;font-weight:800}}.cmsg{{font-size:15px;margin-top:6px}}
.escb{{padding:10px 13px;border-radius:10px;background:rgba(180,121,26,.12);border:1px solid var(--warn);color:var(--warn);font-weight:500;font-size:13px}}
.okb{{padding:10px 13px;border-radius:10px;background:rgba(31,157,87,.12);border:1px solid var(--good);color:var(--good);font-weight:500;font-size:13px}}
.stepline{{font-size:12.5px;color:var(--muted);padding:2px 0}}.stepline b{{color:var(--ink);text-transform:capitalize}}
.frow{{display:flex;gap:10px;padding:8px 2px;border-bottom:1px solid var(--line);font-size:13px}}
.frow .tg{{font-size:11px;color:var(--muted);width:64px}}.frow .rg{{margin-left:auto;font-size:11.5px;color:var(--muted)}}
div[data-testid="stChatMessage"]{{background:var(--panel);border:1px solid var(--line);border-radius:12px}}
.stButton>button{{border-radius:8px;border:1px solid var(--line);color:var(--ink);font-weight:600;background:var(--panel)}}
.stButton>button:hover{{border-color:var(--orange);color:var(--orange-600)}}
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
        "SELECT party_id, domain, journey_stage, region, currency, risk_band FROM party LIMIT ?", (limit,))
    from app import config
    return {f"{p} · {config.DOMAIN_LABELS.get(d, d)} · {rg} · {rb} risk": p
            for p, d, s, rg, cur, rb in rows}


def _pretty(a):
    return a.replace("_", " ").title()


personas = _personas()
backends = db.backends()

top = st.columns([6, 1])
with top[0]:
    st.markdown(f"""
    <div class="hero"><div class="b">Aria &nbsp;<small>BFSI Personalization Platform</small></div>
    <h1>A next-best-action for every interaction, decided, explained and audited in under 98 ms.</h1>
    <p>The same decision engine, seen through five points of view. Real-time, explainable, agentic.</p>
    <div class="kpis">
      <div class="kpi"><div class="v">98 ms</div><div class="l">Latency SLO, p99</div></div>
      <div class="kpi"><div class="v">{audit.count():,}</div><div class="l">Audit rows</div></div>
      <div class="kpi"><div class="v">{backends['ledger']}, {backends['online_store']}</div><div class="l">Backends</div></div>
      <div class="kpi"><div class="v">10 x 6</div><div class="l">Sub-verticals x regions</div></div>
    </div></div>""", unsafe_allow_html=True)
with top[1]:
    st.write("")
    if st.button(("Light" if DARK else "Dark") + " mode", use_container_width=True):
        st.session_state.theme = "light" if DARK else "dark"
        st.rerun()

names = [f"{n} ({r})" for n, r, _ in MODES]
choice = st.radio("View", names, horizontal=True, label_visibility="collapsed")
mode_id = MODES[names.index(choice)][2]

st.markdown("""
<div class="pipe">
  <div class="pnode"><div class="n">L1</div><div class="t">Data</div><div class="d">ledger, hot store</div></div>
  <div class="parr">›</div>
  <div class="pnode"><div class="n">L2</div><div class="t">Features</div><div class="d">online, sub-ms</div></div>
  <div class="parr">›</div>
  <div class="pnode"><div class="n">L3</div><div class="t">Models</div><div class="d">propensity, uplift, fraud</div></div>
  <div class="parr">›</div>
  <div class="pnode"><div class="n">L4</div><div class="t">Decisioning</div><div class="d">rules, bandit</div></div>
  <div class="parr">›</div>
  <div class="pnode"><div class="n">L5</div><div class="t">Governance</div><div class="d">SHAP, fairness, audit</div></div>
</div>""", unsafe_allow_html=True)

FRIENDLY = {
    "payments_fraud_stepup_auth": ("Let us keep your account safe",
        "We noticed something unusual, so we would like to quickly confirm it is really you.", "Recent activity looked different from your usual pattern."),
    "retail_cross_sell_credit_card": ("A card that fits how you spend",
        "A different card could earn you more each month.", "Your spending pattern matches customers who benefit from this card."),
    "wealth_advisory_upgrade": ("A quick review could go a long way",
        "A short portfolio check-in could help you reach your goals faster.", "Your balance and goals suggest room to optimise."),
    "nbfc_preapproved_loan": ("Good news, you are pre-approved",
        "You are pre-approved for a loan with terms tailored to you.", "Your history qualifies you for a tailored offer."),
    "retain_retention_offer": ("We are glad you are here",
        "Here is a little something to say thanks for staying with us.", "You are a valued long-term customer."),
    "service_proactive_support": ("Need a hand?",
        "We spotted you might have a question. We are here whenever you need us.", "Recent activity suggests you may want support."),
    "engage_financial_tip": ("A quick tip for you",
        "A small change this month could help your money go further.", "A timely nudge based on your activity."),
}


def run_decision(pid, event):
    t0 = time.perf_counter()
    decision = engine.decide(pid, event)
    assessment = governance.assess(engine, decision)
    latency_ms = (time.perf_counter() - t0) * 1000.0
    record = governance.build_record(decision, assessment, "web", latency_ms)
    audit.write(record)
    return decision, record, latency_ms


def agent_turn(pid, goal, friendly):
    steps, final = [], None
    for ev in agent.run_stream(pid, goal):
        if ev["type"] == "final":
            final = ev
        else:
            steps.append(ev)
    return steps, final


if mode_id == "customer":
    c = st.columns(2, gap="large")
    with c[0]:
        st.markdown("#### Concierge, the customer moment")
        label = st.selectbox("Profile", list(personas), key="c_p")
        if st.button("Show my moment", type="primary"):
            d, rec, lat = run_decision(personas[label], {"event_type": "session_start"})
            t, m, why = FRIENDLY.get(d["winner"]["action_id"], ("Here is something for you", "A suggestion based on your activity.", "Tailored to you."))
            st.markdown(f'<div class="ccard"><div class="ctitle">{t}</div><div class="cmsg">{m}</div>'
                        f'<div class="seclab">Why you are seeing this</div>{why}'
                        f'<div style="margin-top:12px;font-size:11.5px;color:var(--muted)">Decided in {lat:.1f} ms.</div></div>',
                        unsafe_allow_html=True)
    with c[1]:
        st.markdown("#### Ava, your assistant")
        if "chat" not in st.session_state:
            st.session_state.chat = [{"role": "assistant", "greet": True}]
        for msg in st.session_state.chat:
            with st.chat_message(msg["role"], avatar=AVA if msg["role"] == "assistant" else None):
                if msg.get("greet"):
                    st.write("Hi, I am Ava. Ask me anything and I will sort it, or bring in a specialist when needed.")
                elif msg["role"] == "user":
                    st.write(msg["text"])
                else:
                    f = msg["final"]
                    if f and f["escalated"]:
                        st.markdown('<div class="escb">A specialist will take it from here.</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="okb">All sorted. Anything else I can help with?</div>', unsafe_allow_html=True)
        for q in ["Am I pre-approved for a loan?", "A payment I do not recognise", "A quick money tip"]:
            if st.button(q, key="cq_" + q):
                _, final = agent_turn(personas[st.session_state["c_p"]], q, True)
                st.session_state.chat += [{"role": "user", "text": q}, {"role": "assistant", "final": final}]
                st.rerun()

elif mode_id == "advisor":
    st.markdown("#### Co-pilot, relationship brief")
    label = st.selectbox("Client", list(personas))
    if st.button("Prepare brief", type="primary") or True:
        d, rec, lat = run_decision(personas[label], {"event_type": "session_start"})
        a, w = d["attrs"], d["winner"]
        cc = st.columns(2, gap="large")
        with cc[0]:
            st.markdown('<div class="seclab">Recommended next best action</div>', unsafe_allow_html=True)
            st.markdown(f"**{_pretty(w['action_id'])}**")
            st.markdown("".join(f'<div class="reason"><span>{r["label"]}</span><span class="{"up" if r["direction"]=="increases" else "down"}">{r["direction"]}</span></div>' for r in rec["reason_codes"]), unsafe_allow_html=True)
            st.markdown(f'<span class="pill n">expected value {w["expected_value"]}</span><span class="pill ok">{a.get("region")} · {a.get("currency")}</span>', unsafe_allow_html=True)
        with cc[1]:
            st.markdown('<div class="seclab">Talking points</div>', unsafe_allow_html=True)
            st.markdown(f"- Lead with the **{_pretty(w['action_id']).lower()}**, the highest-value action for this {a.get('domain')} client.\n"
                        f"- Anchor on the driver: **{rec['reason_codes'][0]['label']}**.\n"
                        f"- Client is in the **{a.get('journey_stage')}** stage, **{a.get('risk_band')}** risk. Tailor tone.\n"
                        f"- Suitability and audit are handled automatically.")

elif mode_id == "executive":
    from app.layer1_data import db as _db
    st.markdown("#### Control Tower, the book of decisions")
    lat = [r[0] for r in _db.fetchall("SELECT latency_ms FROM audit_log ORDER BY ts DESC LIMIT 2000")]
    p99 = sorted(lat)[int(0.99 * (len(lat) - 1))] if lat else 0.0
    by_action = _db.fetchall("SELECT action_id, COUNT(*) FROM audit_log GROUP BY action_id ORDER BY 2 DESC")
    by_region = _db.fetchall("SELECT p.region, COUNT(*) FROM audit_log a JOIN party p ON a.party_id=p.party_id GROUP BY p.region ORDER BY 2 DESC")
    k = st.columns(4)
    k[0].metric("Decisions served", f"{audit.count():,}")
    k[1].metric("Latency p99", f"{p99:.1f} ms")
    k[2].metric("Customers", f"{(_db.fetchone('SELECT COUNT(*) FROM party') or [0])[0]:,}")
    k[3].metric("Fairness", "monitored")
    cc = st.columns(2, gap="large")
    with cc[0]:
        st.markdown('<div class="seclab">Decisions by action</div>', unsafe_allow_html=True)
        mx = max([c for _, c in by_action], default=1)
        st.markdown("".join(f'<div class="bar"><span class="bl">{_pretty(a)}</span><div class="tk"><div class="fl" style="width:{c/mx*100:.0f}%"></div></div><span class="bv">{c}</span></div>' for a, c in by_action[:6]) or '<div class="stepline">No decisions yet.</div>', unsafe_allow_html=True)
    with cc[1]:
        st.markdown('<div class="seclab">Decisions by region</div>', unsafe_allow_html=True)
        rmx = max([c for _, c in by_region], default=1)
        st.markdown("".join(f'<div class="bar"><span class="bl">{rg or "—"}</span><div class="tk"><div class="fl" style="width:{c/rmx*100:.0f}%"></div></div><span class="bv">{c}</span></div>' for rg, c in by_region) or '<div class="stepline">No decisions yet.</div>', unsafe_allow_html=True)

elif mode_id == "regulator":
    st.markdown("#### Assurance, every decision explained")
    label = st.selectbox("Subject", list(personas))
    if st.button("Produce an explained decision", type="primary"):
        d, rec, lat = run_decision(personas[label], {"event_type": "large_transfer_attempt", "amount": 4000})
        row = audit.get(rec["decision_id"])
        cc = st.columns(2, gap="large")
        with cc[0]:
            st.markdown('<div class="seclab">SHAP reason codes</div>', unsafe_allow_html=True)
            st.markdown("".join(f'<div class="reason"><span>{r["label"]}</span><span class="{"up" if r["direction"]=="increases" else "down"}">{r["direction"]} · {"+" if r["contribution"]>0 else ""}{r["contribution"]}</span></div>' for r in rec["reason_codes"]), unsafe_allow_html=True)
            st.markdown(f'<span class="pill {"warn" if rec["fairness_flag"]=="adverse_impact" else "ok"}">fairness · {rec["fairness_flag"]}</span>', unsafe_allow_html=True)
        with cc[1]:
            st.markdown('<div class="seclab">Audit record, 16 fields</div>', unsafe_allow_html=True)
            st.json({k: row[k] for k in ["decision_id", "party_id", "channel", "use_case", "action_id", "fairness_flag", "mode", "latency_ms", "consent_ref", "human_reviewed"]})

elif mode_id == "developer":
    st.markdown("#### Engine Room")
    if not st.session_state.get("dev_ok"):
        p = st.text_input("Passcode", type="password")
        if st.button("Unlock", type="primary"):
            if p == DEV_PASSCODE:
                st.session_state.dev_ok = True
                st.rerun()
            else:
                st.error("Incorrect passcode.")
    else:
        h = db.backends()
        st.markdown(f'<span class="pill n">ledger · {h["ledger"]}</span><span class="pill n">hot store · {h["online_store"]}</span>'
                    f'<span class="pill n">agent · {"langgraph" if agent._HAS_LANGGRAPH else "hand-rolled"}</span>'
                    f'<span class="pill ok">{(db.fetchone("SELECT COUNT(*) FROM party") or [0])[0]:,} parties</span>', unsafe_allow_html=True)
        st.selectbox("Party", list(personas), key="d_p")
        goal = st.text_input("Goal", value="I want a pre-approved loan of 50000")
        if st.button("Run agent", type="primary"):
            steps, final = agent_turn(personas[st.session_state["d_p"]], goal, False)
            for ev in steps:
                st.markdown(f'<div class="stepline">{"!" if ev["node"]=="escalate" else "•"} <b>{ev["node"]}</b> · {ev["detail"]}</div>', unsafe_allow_html=True)
            if final:
                cls = "escb" if final["escalated"] else "okb"
                st.markdown(f'<div class="{cls}">{final["answer"]}</div>', unsafe_allow_html=True)
                st.caption(f"confidence {final['confidence']} · {final['engine']}")
