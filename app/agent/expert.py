"""Ava's expert brain: a grounded, offline retrieval engine over the BFSI corpus.

This is the deterministic equivalent of a domain-tuned language model served with
RAG: instead of generating from weights, Ava retrieves from a curated, auditable
corpus (the jargon workbook + the research paper) and composes an expert answer with
a source citation. No external LLM is required, so it runs free, offline, and the
same way every time, which is exactly the control-and-compliance posture a regulated
BFSI assistant wants (the Bank-of-America-Erica design point, not the black box).

Priority of knowledge:
  1. FRAMEWORK   hand-authored flagship answers straight from Aryansh's paper
  2. GLOSSARY    156 terms with definition + BFSI relevance
  3. FACTS       40+ memorize-cold numbers
  4. USE_CASES   30 cross-vertical AI use cases
"""

from __future__ import annotations

import hashlib
import re

from . import bfsi_kb as kb

SOURCE = "the Aria personalization dossier"

# Words that carry no topic signal when scoring a query.
_STOP = {
    "the", "a", "an", "of", "to", "in", "on", "for", "and", "or", "is", "are", "was",
    "with", "by", "as", "at", "per", "via", "vs", "not", "no", "how", "does", "do",
    "did", "what", "whats", "what's", "why", "when", "who", "which", "i", "my", "me",
    "you", "your", "it", "this", "that", "can", "could", "would", "should", "tell",
    "explain", "define", "meaning", "mean", "means", "about", "work", "works", "use",
    "used", "using", "know", "want", "need", "please", "give", "show", "some", "any",
    "much", "many", "into", "from", "be", "am", "if", "there", "get", "got", "make",
    "really", "actually", "exactly", "basically", "just", "so", "like", "more",
}

# Intent phrases that signal a genuine "teach me this" question.
_DEFINE_CUES = ("what is", "what's", "what are", "whats", "define", "explain", "meaning of",
                "tell me about", "how does", "how do", "what does", "describe", "walk me through")


def _pick(seed: str, arr):
    return arr[int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(arr)]


def _toks(s: str):
    return [w for w in re.findall(r"[a-z0-9][a-z0-9\-\+]*", s.lower())]


# ---------------------------------------------------------------------------
# FRAMEWORK: flagship, hand-authored answers grounded in the research paper.
# Each: id, aliases (phrases/acronyms that should trigger it), a rich answer.
# ---------------------------------------------------------------------------
FRAMEWORK = [
    {
        "id": "demographics_free",
        "title": "Behavior-first, demographics-free personalization",
        "aliases": ["demographics-free", "demographics free", "behavior-first", "behaviour-first",
                    "behavior first", "without demographics", "no demographics", "demographic",
                    "age gender income", "protected attribute", "protected characteristic"],
        "answer": "The core thesis of Aria is that personalization should be built on what a customer "
                  "does, not who they are. Demographics, age, gender, income band, geography, fail three "
                  "tests at once in a regulated setting: they predict the individual poorly, they proxy the "
                  "protected characteristics fair-lending law forbids, and they leave no per-decision "
                  "explanation. Rebuilding on behavioral and contextual signals fixes all three together. "
                  "On the paper's synthetic benchmark, behavioral signals reach test AUC 0.817 versus 0.629 "
                  "for demographics, and adding demographics on top of behavior moves AUC by just 0.001, so "
                  "you drop a whole category of legal risk at essentially zero accuracy cost. Protected "
                  "attributes live only in a separated fairness-testing store, never on the serving path, so "
                  "the firm can truthfully say it does not decide on demographics yet still measures "
                  "demographic fairness.",
    },
    {
        "id": "two_gate_framework",
        "title": "The two-gate, twelve-test data-acceptability framework",
        "aliases": ["data acceptability", "acceptability framework", "two gate", "two-gate", "twelve test",
                    "twelve tests", "12 tests", "acceptability gate", "value gate", "which data",
                    "should we use this data", "data governance framework"],
        "answer": "The most consequential choice a personalization program makes is not which model to train "
                  "but which data to admit, so Aria gates every dataset through two ordered gates of six "
                  "tests each. The acceptability gate asks whether you may and should use the data at all: "
                  "(1) lawful basis and consent, (2) provenance and lineage, (3) sensitivity and "
                  "identifiability, (4) fairness and proxy risk, (5) security and residency, (6) purpose and "
                  "retention. The value gate asks whether it actually beats what you already have: (7) "
                  "incremental lift by ablation, (8) freshness and latency-fit, (9) coverage and "
                  "representativeness, (10) stability under drift, (11) interpretability-fit for adverse-action "
                  "notices, (12) total cost of ownership. The order is deliberate, a highly predictive but "
                  "unlawful feature is rejected regardless of its lift, and every rejection is itself logged "
                  "as a governed decision.",
    },
    {
        "id": "five_layers",
        "title": "The five-layer, three-plane architecture",
        "aliases": ["five layer", "five layers", "5 layers", "5-layer", "architecture", "three plane",
                    "three-plane", "3 plane", "reference architecture", "the stack", "how is it built",
                    "how it works", "layers of the platform", "build plane", "serve plane", "govern plane"],
        "answer": "Aria is the same five layers everywhere, spanning three cloud planes. The layers: (1) a "
                  "data foundation of streaming events and resolved identity, (2) a feature store that kills "
                  "training-serving skew, (3) the model layer, propensity, uplift, recommendation, fraud "
                  "graphs, grounded LLMs and agents, (4) a real-time decisioning engine that turns scores "
                  "into a governed action under the latency budget, and (5) a governance overlay that touches "
                  "every single decision. The three planes let each platform do what it is best at: a build "
                  "plane engineers features and trains models on open table formats (Databricks), a govern "
                  "plane serves a certified source of truth (Snowflake), and a serve plane returns the "
                  "decision in real time (AWS). Firms differ not in the layers but in the quality of what "
                  "sits inside each, and demo becomes production by swapping boxes behind stable interfaces, "
                  "not by rewriting.",
    },
    {
        "id": "ten_step_flow",
        "title": "One decision, end to end: the ten-step flow",
        "aliases": ["ten step", "ten-step", "10 step", "10-step", "decision flow", "end to end flow",
                    "one decision", "how a decision is made", "next best action flow", "decision path"],
        "answer": "A single decision is a ten-step traversal of the five layers, engineered to finish inside "
                  "the budget. A customer event arrives on the stream; pre-computed features are read from the "
                  "online store by customer key; the decisioning engine gets the request and context; "
                  "eligibility and do-no-harm rules filter the action catalogue; the eligible actions are "
                  "scored; they are ranked by expected value under suitability, with a contextual bandit "
                  "balancing exploration; the top action passes a final fairness and suitability check; the "
                  "decision, its features, model versions, reasons and fairness flag are written to the audit "
                  "log; the action is adapted to the channel and delivered; and the outcome is captured as a "
                  "reward that feeds the bandit and the models. Everything on the hot path is a keyed lookup "
                  "and a score, never an on-demand computation, which is why the tail stays bounded.",
    },
    {
        "id": "causal_uplift_result",
        "title": "Causal targeting beats propensity",
        "aliases": ["uplift vs propensity", "causal targeting", "why uplift", "uplift result", "1.35x",
                    "propensity vs uplift", "incremental gain", "who to target", "persuadable", "swing customer"],
        "answer": "Targeting is causal, not merely predictive. Propensity ranks who is likely to act and so "
                  "spends incentives on customers who would have converted anyway; uplift ranks who acts "
                  "because you reached them, the persuadable swing customers. On the benchmark, at a fixed "
                  "thirty-percent budget uplift targeting captured 0.466 of the total available incremental "
                  "gain against 0.346 for propensity and 0.30 for random, a 1.35x advantage for causal over "
                  "propensity, which matches the industry's 20-40% ROI-uplift benchmark. Aria estimates it "
                  "with a two-model T-learner trained on randomized-holdout data, and measures it against a "
                  "real holdout so every headline number is incremental, not just correlated.",
    },
    {
        "id": "fairness_result",
        "title": "Removing a proxy improves fairness almost for free",
        "aliases": ["disparate impact", "fairness result", "proxy feature", "four fifths", "4/5ths",
                    "adverse impact ratio", "air", "parity", "0.996", "0.69", "fairness cost"],
        "answer": "Fairness and accuracy are not the trade-off people assume. In the fairness study, a model "
                  "that includes a proxy feature reaches AUC 0.832 but a disparate-impact ratio of only 0.693, "
                  "below the conventional 0.80 four-fifths parity floor. Removing the proxy lifts the "
                  "disparate-impact ratio to 0.996, near-perfect parity, while AUC falls only to 0.817, a cost "
                  "of 0.014. So the demographics-free design does not merely omit a protected attribute; it "
                  "materially cuts the proxy influence that produces disparate impact, and does it almost for "
                  "free. Fairness is then tested continuously (AIR / SMD) against protected labels held in the "
                  "separated store, which is a stronger guarantee than just leaving demographics out.",
    },
    {
        "id": "latency_result",
        "title": "The sub-98ms latency budget",
        "aliases": ["latency", "98ms", "98 ms", "sub-98", "p99", "p95", "p50", "how fast", "milliseconds",
                    "latency budget", "real time budget", "35.5", "tail latency", "decision latency"],
        "answer": "The hardest promise in real-time personalization is speed: a fully governed decision inside "
                  "a sub-98-millisecond 99th-percentile budget. The modeled end-to-end decision holds a median "
                  "of 24.7 ms, a 95th percentile of 31.7 ms, and a 99th percentile of 35.5 ms, comfortably "
                  "inside budget with headroom reserved for the governance steps a regulated decision needs. "
                  "Two engineering choices buy that: colocating the online store, the model and the rules in "
                  "one region to kill cross-region hops, and reading pre-materialized features by key instead "
                  "of computing them on demand. Payments pushes it further to a sub-50ms p99 for fraud on "
                  "instant rails.",
    },
    {
        "id": "audit_log",
        "title": "The 16-field decision audit log",
        "aliases": ["audit log", "audit record", "16 field", "sixteen field", "16-field", "decision log",
                    "auditable", "audit schema", "how is it auditable", "reason codes", "governance record"],
        "answer": "Governance is a property of every decision, not a downstream review. Each decision emits an "
                  "additive feature-attribution explanation (SHAP), a fairness flag, and an append-only "
                  "audit row of sixteen fields: decision_id, party_id, channel, use_case, action_id, "
                  "features_snapshot, model_version, rule_version, consent_state, explanation, fairness_flags, "
                  "outcome_link, human_oversight, regulatory_tags, timestamp and any override. Because every "
                  "feature carries its lawful basis and every decision logs the features it used, compliance "
                  "with a specific regime becomes a query against the log rather than a bespoke project. That "
                  "one schema is designed to satisfy SR 11-7, the EU AI Act, ECOA/Reg B, the NAIC AI "
                  "Bulletin, MiFID II, FINRA 2111 and the RBI Digital Lending Master Direction simultaneously.",
    },
    {
        "id": "agentic_layer",
        "title": "The governed agentic layer",
        "aliases": ["agentic", "agent layer", "agentic layer", "perceive reason act", "mcp",
                    "model context protocol", "human in the loop", "escalation", "autonomous agent",
                    "how does the agent work", "tool use", "agent safety"],
        "answer": "Beyond single decisions, Aria has a governed agentic layer that completes routine tasks "
                  "end to end. The agent runs a perceive-reason-act-observe loop and calls tools through a "
                  "registry modeled on the Model Context Protocol, so every side-effecting action is mediated "
                  "and logged. Four disciplines make autonomy safe in a regulated setting: PII is kept out of "
                  "the model payload (the agent reasons over tokens while tools resolve sensitive details "
                  "server-side); memory is a consented, retention-limited vector store, not an unbounded log; "
                  "the tool space is fenced to an approved set of operations; and a policy routes "
                  "low-confidence or high-stakes cases to a human queue, where the agent stops and hands over "
                  "the context it gathered. Every tool call lands in the same audit log as a synchronous "
                  "decision, so an autonomous action is as reconstructable as a human one. Bajaj Finance runs "
                  "this shape in production with 800+ agents.",
    },
    {
        "id": "eight_patterns",
        "title": "The eight machine-learning patterns",
        "aliases": ["eight patterns", "8 patterns", "eight models", "which models", "model patterns",
                    "types of models", "ml patterns", "the patterns", "model toolkit"],
        "answer": "You do not need a hundred models, you need eight patterns done well, and almost every BFSI "
                  "use case is a combination of them. (1) Tabular gradient boosting (XGBoost, LightGBM, "
                  "CatBoost) for credit, fraud and churn. (2) Causal uplift modeling (T/X-learner, causal "
                  "forests) for who to target. (3) Recommendation and ranking (two-tower embeddings) for "
                  "offers. (4) Graph neural networks (GraphSAGE, HinSAGE) for relational fraud and AML. (5) "
                  "Grounded language models (RAG) for text and copilots. (6) Agentic AI (LangGraph) for "
                  "multi-step action. (7) Reinforcement learning and contextual bandits (Thompson, LinUCB) for "
                  "real-time NBA and dynamic pricing. (8) Sequence and transformer models (LSTM, TFT) for "
                  "soft-churn and lifetime value. Depth in each beats a sprawl of shallow one-off models you "
                  "cannot govern.",
    },
    {
        "id": "six_journey",
        "title": "The six-stage customer journey",
        "aliases": ["six stage", "6 stage", "customer journey", "journey stages", "discover originate",
                    "the journey", "lifecycle stages", "customer lifecycle"],
        "answer": "Personalization is not a feature bolted onto a product, it is the journey instrumented end "
                  "to end, and the same six stages hold across all ten sub-verticals. (1) Discover: lookalike "
                  "and intent ML for acquisition. (2) Originate: cash-flow XGBoost underwriting, RL dynamic "
                  "pricing and agentic onboarding, where legacy loses 40-60% to drop-off. (3) Engage: "
                  "real-time next-best-action on every event, in an 8-12 second mobile session. (4) "
                  "Cross-sell: life-event NBA fired 60-120 days early with causal uplift. (5) Service: "
                  "agentic AI handling 50-65% of low-complexity cases with grounded self-service. (6) Retain: "
                  "soft-churn detection ~90 days early with uplift-modeled save offers, because retaining is "
                  "5-7x cheaper than acquiring.",
    },
    {
        "id": "five_lenses",
        "title": "The five 360-degree stakeholder lenses",
        "aliases": ["five lens", "five lenses", "5 lenses", "360 view", "360-degree", "stakeholder views",
                    "the lenses", "points of view", "concierge co-pilot control tower", "stakeholder lens"],
        "answer": "Aria is one decision engine seen through five lenses, which is exactly the five views in "
                  "this app. The Customer lens (Concierge): relevant offers, fair pricing, service that does "
                  "not make you re-explain, the feeling of being known for years. The Advisor/RM lens "
                  "(Co-pilot): briefs drafted in minutes, cross-sell with talking points, soft-churn warnings "
                  "60-120 days early, +25-40% productivity. The Executive lens (Control Tower): five-year "
                  "cumulative P&L, causal-lift measurement, governance posture. The Regulator lens "
                  "(Assurance): a SHAP explanation per decision, current fairness testing, a replayable audit "
                  "log. The AI Engineer lens (Engine Room): feature store, model registry, sub-100ms "
                  "decisioning, drift dashboards, the agent framework. Same engine, five sets of eyes.",
    },
    {
        "id": "maturity_model",
        "title": "The four-stage maturity model",
        "aliases": ["maturity model", "four stage", "4 stage", "stages of maturity", "rules batch real-time",
                    "personalization maturity", "how mature", "maturity curve"],
        "answer": "Firms climb a four-stage maturity curve, and most Tier-1 banks sit at stage 2-3. Stage 1 is "
                  "hard-coded rules and a handful of static segments. Stage 2 is batch machine-learning scores "
                  "acting on a day-old view. Stage 3 is a unified real-time decisioning brain, one engine "
                  "serving every channel under 100ms. Stage 4 is autonomous agents completing journeys end to "
                  "end. Segments are a stage-1 crutch; the destination is one-to-one, a decision computed for "
                  "the individual in the moment. The job is to move a firm from 1-2 to 3-4 without a rebuild, "
                  "by swapping components behind stable interfaces.",
    },
    {
        "id": "ten_subverticals",
        "title": "The ten BFSI sub-verticals",
        "aliases": ["ten sub-vertical", "ten subvertical", "10 sub-vertical", "sub-verticals", "subverticals",
                    "which domains", "all of bfsi", "the domains", "verticals covered"],
        "answer": "Aria covers all of BFSI as three verticals and ten sub-verticals under one architecture. "
                  "Banking: Retail and Transaction Banking, Corporate and Commercial, Wealth and Capital "
                  "Markets. Financial Services: Asset Management, Payments, NBFCs (non-bank lenders). "
                  "Insurance: Personal (life and health), General (auto, home, P&C), and Commercial "
                  "(cyber, liability, MGA). The claim is that the same five layers, six-stage journey and "
                  "eight ML patterns hold across all ten; only the action catalogue, the data sources and the "
                  "regulations change per market.",
    },
    {
        "id": "papaa",
        "title": "The PAPAA canonical data model",
        "aliases": ["papaa", "party agreement product account activity", "canonical data model",
                    "data model entities", "party account activity", "canonical model"],
        "answer": "Under the hood every sub-vertical shares one canonical data model, PAPAA: Party, Agreement, "
                  "Product, Account, Activity, extended with a sixth entity, Action, for personalization. A "
                  "party can be a person or a business; an agreement binds a party to a product; an account is "
                  "the running instance; activity is the event stream; and action is the governed next-best-"
                  "action Aria decides and logs. That six-entity superset is what lets one engine serve a "
                  "mortgage, a motor policy and a prime-brokerage relationship without a bespoke schema each.",
    },
    {
        "id": "economics",
        "title": "The economics: where $200M-$1B comes from",
        "aliases": ["economics", "roi", "business case", "how much is it worth", "200 million", "1 billion",
                    "value of personalization", "p&l", "revenue lift", "the money", "how much value",
                    "personalization worth", "worth", "how much is personalization"],
        "answer": "The value is built bottom-up, sub-vertical by sub-vertical, never as a slogan. Retail "
                  "banking earns +5-15% revenue per active customer; wealth lifts advisor productivity "
                  "+25-40%; payments add +10-20% card volume and cut fraud (HSBC's federated GNN cut alerts "
                  "60% while catching 2-4x more fraud); insurance improves loss ratios 3-5 points; NBFCs cut "
                  "loan-approval time 30-50%. Sum the measured effects for a Tier-1 firm and it is a "
                  "$200M-$1B+ annual swing. The discipline is to measure each against a randomized holdout so "
                  "every number is causal and a CFO can check the arithmetic.",
    },
    {
        "id": "what_is_aria",
        "title": "What Aria is",
        "aliases": ["what is aria", "what is this platform", "what is this", "about aria", "what does aria do",
                    "aria platform", "this platform", "what are you built on"],
        "answer": "Aria is a real-time, agentic, auditable personalization platform for banking, financial "
                  "services and insurance, a Tredence reference build. It decides the next-best-action for "
                  "every interaction in under ~98 milliseconds, explains it in plain language with a SHAP "
                  "reason and a fairness check, and writes an append-only audit record for every decision. "
                  "It is behavior-first and demographics-free by design, runs the same five-layer architecture "
                  "across all ten BFSI sub-verticals, and exposes one engine through five stakeholder views. "
                  "I am Ava, the assistant inside it, and I am grounded in its research dossier rather than "
                  "guessing, so what I tell you is what the platform actually does.",
    },
]

# Build a fast lookup for framework by id (used by tests / callers).
FRAMEWORK_BY_ID = {f["id"]: f for f in FRAMEWORK}


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------
# Common English words that must never act as a strong (acronym-style) alias, even
# when short, so "life", "fair", "bank" cannot hijack a technical entry.
_COMMON = {"life", "fair", "bank", "loan", "risk", "care", "home", "auto", "cash",
           "rate", "fund", "data", "cost", "time", "work", "wire", "card", "days"}


def _alias_score(aliases, message: str, qtoks: set) -> float:
    """Score how strongly a set of aliases matches the message."""
    best = 0.0
    for a in aliases:
        a = a.lower()
        if len(a) <= 4 or a.isupper():
            # short/acronym: require a whole-token hit to avoid 'rag' in 'storage'
            if a in qtoks and a not in _COMMON:
                best = max(best, 6.0)
        else:
            if a in message:
                # longer, more specific phrase = stronger signal
                best = max(best, 4.0 + len(a.split()))
            else:
                # partial: enough of the alias's distinctive words are present, even if
                # the user typed a shorter phrase than the full stored name
                aw = [w for w in a.split() if w not in _STOP and len(w) > 2]
                if aw:
                    present = [w for w in aw if w in qtoks]
                    if len(present) == len(aw):
                        best = max(best, 3.0 + len(aw))
                    elif len(present) >= 2 and len(present) / len(aw) >= 0.5:
                        best = max(best, 3.0 + len(present))
    return best


def _overlap(text: str, qtoks: set) -> float:
    twords = set(w for w in _toks(text) if w not in _STOP and len(w) > 2)
    return len(twords & qtoks) * 0.5


def _has_define_cue(message: str) -> bool:
    return any(c in message for c in _DEFINE_CUES)


def retrieve(message: str):
    """Return the best grounded hit as a dict {kind,title,score,...} or None."""
    m = " " + (message or "").lower().strip() + " "
    qtoks = set(w for w in _toks(message) if w not in _STOP)
    if not qtoks:
        return None
    define = _has_define_cue(m)

    cands = []  # (score, kind, payload)

    # 1) FRAMEWORK
    for f in FRAMEWORK:
        s = _alias_score(f["aliases"], m, qtoks)
        if s:
            s += _overlap(f["title"], qtoks)
            if define:
                s += 2
            cands.append((s, "framework", f))

    # 2) GLOSSARY
    for g in kb.GLOSSARY:
        s = _alias_score(g["aliases"], m, qtoks)
        if s:
            s += _overlap(g["definition"] + " " + g["relevance"], qtoks) * 0.5
            if define:
                s += 2
            cands.append((s, "glossary", g))

    # 3) USE_CASES — match only on the full use-case name (a specific phrase), never on
    # loose single tokens, so common words like "life" or "pricing" cannot hijack.
    for u in kb.USE_CASES:
        s = _alias_score([u["name"].lower()], m, qtoks)
        if s:
            cands.append((s + _overlap(u["desc"], qtoks), "use_case", u))

    # 4) FACTS (only when the query looks quantitative)
    if any(w in qtoks for w in ("how", "many", "much", "number", "stat", "benchmark", "rate", "lift",
                                "percent", "latency", "budget")) or any(
            k in m for k in ("how many", "how much", "what percent", "benchmark")):
        for fa in kb.FACTS:
            s = _overlap(fa["fact"], qtoks)
            if s >= 1.0:
                cands.append((s + 1.0, "fact", fa))

    if not cands:
        return None
    cands.sort(key=lambda c: c[0], reverse=True)
    score, kind, payload = cands[0]
    if score < 5.0:
        return None
    return {"kind": kind, "score": score, "payload": payload}


# ---------------------------------------------------------------------------
# Answer composition (tone-aware, grounded, confident but explainable)
# ---------------------------------------------------------------------------
_OPENERS = {
    "witty": ["Great question, this is home turf. ", "Happy to, this one I know cold. ", ""],
    "professional": ["", "Certainly. ", ""],
    "genz": ["okay this is lowkey my favorite topic. ", "bet, real quick: ", ""],
}
_GROUND = {
    "witty": [f"\n\n(Grounded in {SOURCE}, not vibes.)", f"\n\nStraight from {SOURCE}.", ""],
    "professional": [f"\n\nSource: {SOURCE}.", ""],
    "genz": [f"\n\nsourced from {SOURCE} btw, not made up.", ""],
}


def compose(hit: dict, message: str, tone: str) -> dict:
    kind, payload = hit["kind"], hit["payload"]
    seed = message + tone

    if kind == "framework":
        body = payload["answer"]
        title = payload["title"]
    elif kind == "glossary":
        g = payload
        head = f"**{g['term']}**"
        if g.get("expansion") and g["expansion"].lower() != g["term"].lower():
            head += f" ({g['expansion']})"
        body = f"{head}: {g['definition']}"
        if g.get("relevance"):
            body += " " + g["relevance"]
        title = g["term"]
    elif kind == "use_case":
        u = payload
        body = f"{u['name']}: {u['desc']}"
        extra = []
        if u.get("pattern"):
            extra.append(f"the pattern is {u['pattern'].lower()}")
        if u.get("verticals"):
            extra.append(f"it applies to {u['verticals']}")
        if extra:
            body += " In Aria, " + ", and ".join(extra) + "."
        title = u["name"]
    elif kind == "fact":
        fa = payload
        body = f"{fa['fact']}: **{fa['value']}**."
        if fa.get("note"):
            body += f" {fa['note']}."
        title = fa["fact"]
    else:
        return None

    opener = _pick(seed, _OPENERS.get(tone, _OPENERS["witty"]))
    ground = _pick(seed + "g", _GROUND.get(tone, _GROUND["witty"]))
    answer = opener + body + ground
    return {"answer": answer, "title": title, "matched": True, "tone": tone,
            "grounded": True, "source": SOURCE}
