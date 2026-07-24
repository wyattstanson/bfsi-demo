from __future__ import annotations

import hashlib
import re

DISCLAIMER = "This is general financial education, not personalized investment advice. For decisions about your money, please speak with a licensed advisor."

PRINCIPLES = [
    "Spend less than you earn, and invest the difference for the long run. That gap, compounded patiently, is where wealth quietly comes from.",
    "The first rule is to avoid permanent loss. Protect your downside and you will still be standing when opportunity shows up.",
    "Time in the market beats timing the market. Compounding rewards patience far more than cleverness.",
    "Diversify so no single mistake can sink you. You do not have to be right often if you are never ruined.",
    "Understand what you own. If you cannot explain it simply, it does not belong in your plan yet.",
    "High-interest debt is a guaranteed negative return. Clearing it is the safest high-yield move most people ever make.",
    "Be fearful when others are greedy and patient when others panic. Temperament, not IQ, decides outcomes.",
    "Price is what you pay, value is what you get. Focus on value and let price take care of itself over time.",
]


def _pick(seed: str, arr):
    return arr[int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(arr)]


DOMAIN_KW = {
    "retail": ["retail bank", "checking", "savings account", "debit card", "everyday bank", "mobile bank", "current account", "overdraft"],
    "corporate": ["corporate bank", "treasury", "cash management", "business account", "sme ", "payroll", "working capital", "trade finance"],
    "wealth": ["wealth", "portfolio", "financial advisor", "high net worth", "private bank", "financial plan", "estate", "advisory"],
    "asset_mgmt": ["asset management", "mutual fund", "etf", "fund manager", "index fund", "direct indexing", "separately managed"],
    "payments": ["payment", "card ", "upi", "transaction", "merchant", "wallet", "remittance", "point of sale", "pos "],
    "capital_markets": ["capital markets", "trading", "equities", "derivatives", "rfq", "research", "institutional", "brokerage", "prime broker"],
    "nbfc": ["nbfc", "microfinance", "consumer loan", "gold loan", "two wheeler", "emi card", "collections", "account aggregator"],
    "personal_ins": ["life insurance", "health insurance", "term life", "wellness", "telematics", "vitality", "mediclaim"],
    "general_ins": ["auto insurance", "home insurance", "motor insurance", "property", "claim", "p&c", "flood", "catastrophe"],
    "commercial_ins": ["commercial insurance", "cyber insurance", "business insurance", "liability", "underwriting", "broker submission", "parametric"],
}
DOMAIN_LABEL = {
    "retail": "Retail Banking", "corporate": "Corporate Banking", "wealth": "Wealth",
    "asset_mgmt": "Asset Management", "payments": "Payments", "capital_markets": "Capital Markets",
    "nbfc": "NBFC", "personal_ins": "Personal Insurance", "general_ins": "General Insurance",
    "commercial_ins": "Commercial Insurance",
}
DOMAIN_ANSWER = {
    "retail": "In retail banking, personalization shows up as real-time next-best-action on every tap: a fair rate, a timely nudge, fraud caught in milliseconds, and grounded self-service. The winning firms combine uplift models and contextual bandits under 100ms with a genuinely helpful assistant, the pattern BofA Erica set with billions of interactions.",
    "corporate": "In corporate banking the relationship is the product. The edge is a relationship-manager co-pilot that drafts client briefs in minutes and surfaces cross-sell with talking points, plus a treasury workstation that personalizes cash, payment routing, and hedging insight. Most clients want tailored solutions and feel their bank does not yet understand them, which is exactly the gap AI closes.",
    "wealth": "In wealth, personalization means an advisor co-pilot that drafts portfolio commentary and life-event outreach sixty to one hundred and twenty days early, plus tax-aware, goal-based portfolios. This is the Aladdin Auto-Commentary template: the human keeps the relationship, the AI does the preparation, and productivity rises twenty-five to forty percent.",
    "asset_mgmt": "In asset management the product itself becomes the personalization vehicle: direct indexing and separately managed accounts let each client hold a custom basket with tax-loss harvesting and ESG screens, rather than a one-size fund. Distribution is a layer removed from the investor, so the tailoring happens in construction, not messaging.",
    "payments": "In payments the frontier is agentic commerce and sub-fifty-millisecond fraud. Card-linked offers personalize spend, graph models score fraud in real time on instant rails, and tokenized agent credentials let trusted AI agents transact within a budget and scope. Personalization here is measured in milliseconds and basis points.",
    "capital_markets": "In capital markets, personalization is research and pricing: tailored research feeds and trade ideas that win wallet share, per-client RFQ pricing that reflects elasticity, and domain-tuned language models over filings and transcripts. Execution quality wins primary-dealer status; relevance wins the reader.",
    "nbfc": "In the NBFC world, especially India, the edge is speed and reach: account-aggregator data rails enable a sub-five-minute cash-flow underwriting decision, and fleets of narrow autonomous agents close loans, run vernacular collections, and cross-sell end to end. Bajaj FINAI is the reference, with hundreds of agents in production.",
    "personal_ins": "In personal insurance, continuous data turns pricing into a feedback loop: wellness and telematics reward healthier, safer behavior with lower premiums, and connected-home sensors prevent losses before they happen. The customer sees fairer pricing that reflects how they actually live, not a broad demographic bucket.",
    "general_ins": "In general insurance the wins are geospatial property risk scored per address and straight-through claims where image AI assesses damage in seconds. The outcome is a three to five point loss-ratio improvement and claims satisfaction that customers actually notice, the space where Lemonade pays simple claims in about three seconds.",
    "commercial_ins": "In commercial insurance, AI triages broker submissions, matches appetite, and prices cyber risk from live security posture, letting a small team do the work of a larger one. Parametric products pay out instantly on a measured trigger. Personalization here is underwriting precision at portfolio scale.",
}

SMALLTALK = [
    (["hi", "hello", "hey", "yo", "hola", "namaste", "good morning", "good evening", "good afternoon"],
     ["Hi, I am Ava, your financial guide. Lovely to meet you. What is on your mind today, saving, borrowing, investing, a payment, or something about your account?",
      "Hello. I am Ava. I can talk money in plain English, from budgeting and credit to investing and insurance, or handle a loan, a dispute, or a payment. Where shall we start?"]),
    (["how are you", "how's it going", "how are u", "whats up", "what's up"],
     ["I am doing well, thank you for asking. More importantly, how can I help with your money today?"]),
    (["thank", "thanks", "thx", "cheers", "appreciate"],
     ["You are very welcome. Ask me anything else, any time."]),
    (["who are you", "what are you", "what can you do", "your name", "how do you work", "what do you do"],
     ["I am Ava, a financial guide. I answer questions across every part of banking, markets, and insurance, I explain things simply, and I can act on real tasks like a loan, a dispute, or a payment, bringing in a human when the stakes are high. I never leave you with a dead end."]),
    (["bye", "goodbye", "see you", "that's all", "thats all"],
     ["Take care, and come back any time. Your money will be here, hopefully a little better organised."]),
    (["love you", "you are great", "you're great", "you are the best"],
     ["That is kind of you. Let us put that good mood to work, is there a money question I can take off your plate?"]),
]
PERSONAL = [
    (["stressed", "worried", "anxious", "scared", "overwhelmed", "struggling", "can't sleep", "cant sleep", "depressed", "hard time"],
     "I hear you, money worry is heavy, and you are not alone in it. Let us make it smaller and concrete. A calm first step is to list what is coming in, what must go out, and what can wait, then protect a small cash buffer before anything else. Tell me the one thing weighing on you most and we will take it a piece at a time."),
    (["lost my job", "unemployed", "laid off", "no income", "fired"],
     "I am sorry, that is genuinely hard. The priorities right now are simple: protect cash, cut non-essential spending, contact lenders early because most will work with you, and check any benefits or emergency support you are entitled to. Keep the emergency fund for essentials only. If you tell me your biggest fixed cost, I can help you think it through."),
    (["broke", "no money", "paycheck to paycheck", "can't afford", "cant afford"],
     "Living close to the edge is exhausting, and it is more common than people admit. The way out usually starts small: find one recurring cost to cut, automate even a tiny weekly saving so a buffer starts to build, and clear the highest-interest debt first. Small, steady moves compound. What would help most, trimming spending or dealing with a debt?"),
]

KB = [
    {"id": "emergency_fund", "title": "Building an emergency fund", "kw": ["emergency", "rainy day", "buffer", "cushion", "unexpected", "safety net"],
     "a": "An emergency fund is the foundation everything else rests on. Aim for three to six months of essential expenses in a plain, instant-access savings account, kept separate from spending money. Build it before you invest, because it is what stops a surprise from turning into high-interest debt. Automate a small weekly transfer so it grows without you thinking about it."},
    {"id": "budget", "title": "Budgeting that sticks", "kw": ["budget", "spending plan", "track expenses", "50 30 20", "manage money", "overspend"],
     "a": "A budget is telling your money where to go before it disappears. A durable shape is 50/30/20: roughly half your take-home for needs, a third for wants, a fifth for saving and debt. The trick is to automate the saving and review one number a week, not to log every coffee. A five-minute monthly check of subscriptions usually finds real money."},
    {"id": "credit_score", "title": "How your credit score works", "kw": ["credit score", "cibil", "fico", "improve credit", "creditworthy", "credit report"],
     "a": "Your credit score is a lender's shorthand for how reliably you repay. The two biggest levers are paying every bill on time and keeping your credit utilisation low, ideally under thirty percent of your limit. You do not need to carry a balance; paying in full each month is ideal. Check your report yearly and dispute anything wrong."},
    {"id": "compounding", "title": "The power of compounding", "kw": ["compound", "interest on interest", "grow money", "long term growth", "snowball"],
     "a": "Compounding is interest earning interest, and it rewards starting early. A useful shortcut is the rule of 72: divide 72 by your annual return to estimate the years it takes to double. At seven percent, money doubles roughly every ten years. Start now, stay invested, and let time do the heavy lifting."},
    {"id": "investing_basics", "title": "Getting started with investing", "kw": ["invest", "stocks", "index fund", "etf", "mutual fund", "start investing", "sip"],
     "a": "For most people, low-cost, broadly diversified index funds are a sensible core. They spread money across hundreds of companies, keep fees low, and remove the guesswork of picking winners. Invest a fixed amount on a regular schedule so you buy through ups and downs, and match your risk to your timeline: cash for near-term goals, a diversified mix for the long ones."},
    {"id": "diversification", "title": "Why diversification matters", "kw": ["diversify", "spread risk", "concentration", "asset allocation", "all my money in"],
     "a": "Diversification means not letting any single company, sector, or currency decide your future. Holding many uncorrelated assets makes a bad outcome anywhere survivable everywhere. It keeps you in the game long enough for compounding to work. The simplest version is a broad global index fund plus some bonds or cash sized to your comfort with swings."},
    {"id": "retirement", "title": "Planning for retirement", "kw": ["retirement", "retire", "pension", "401k", "nps", "ppf", "old age"],
     "a": "Retirement planning is buying your future self freedom. Capture any employer match first, because it is an instant return. Then automate steady contributions into tax-advantaged, diversified funds and raise them a little each time your income rises. How early you start and how consistent you are matter more than clever fund picks."},
    {"id": "debt", "title": "Paying down debt", "kw": ["debt", "credit card debt", "emi", "loan payoff", "avalanche", "snowball", "interest"],
     "a": "Clear high-interest debt, especially credit cards, as fast as you can, because avoiding a twenty percent charge is a guaranteed twenty percent return. Two methods work: the avalanche pays the highest-rate balance first to save the most, while the snowball clears the smallest first for quick wins. Keep minimums on everything, then attack the target."},
    {"id": "fraud", "title": "Protecting yourself from fraud", "kw": ["fraud", "scam", "phishing", "unauthorized", "stolen", "otp", "safe", "hacked"],
     "a": "Most fraud starts with urgency and a request to move money or share a code. A real bank never asks for your full password, PIN, or a one-time code. Turn on transaction alerts, use app-based two-factor authentication, and pause whenever something feels rushed. If you see a charge you do not recognise, report it immediately."},
    {"id": "insurance", "title": "How much insurance you need", "kw": ["insurance", "cover", "term life", "health cover", "premium", "protect family"],
     "a": "Insurance exists to protect against losses you could not absorb yourself, not small affordable ones. Prioritise health cover and, if people depend on your income, term life, which is cheap because it is pure protection. Buy enough to cover your dependents' needs and debts, and revisit after big life events like a marriage, a child, or a home."},
    {"id": "loan", "title": "Borrowing sensibly", "kw": ["loan", "borrow", "mortgage", "pre-approved", "apr", "interest rate", "credit offer"],
     "a": "Borrow for things that build value or are genuine needs, and treat the rate and total cost, not the monthly payment, as the real price. Compare the annual rate across lenders, check fees, and make sure the repayment fits comfortably in your budget. A pre-approved offer is a starting point, not an obligation; shop around and read the terms."},
    {"id": "goal", "title": "Saving for a goal", "kw": ["save for", "goal", "house", "car", "wedding", "down payment", "vacation", "big purchase"],
     "a": "Give every goal a name, a number, and a date, then work backwards to a monthly amount. Keep anything you need within three years in safe cash-like savings so a market dip cannot derail you; let longer goals ride in diversified investments. Automating the transfer on payday turns a wish into a funded plan."},
    {"id": "market", "title": "Reading the market without panic", "kw": ["market crash", "volatility", "recession", "downturn", "should i sell", "market dip", "stocks falling"],
     "a": "Markets rise over the long run but lurch in the short run, and headlines are loudest when reacting is least useful. Downturns are the normal cost of higher long-term returns. If your money is invested for a distant goal, the wise move in a fall is usually to keep contributing and avoid selling in fear."},
]


def classify_domain(message: str) -> str | None:
    m = " " + message.lower() + " "
    best, best_s = None, 0
    for dom, kws in DOMAIN_KW.items():
        s = sum(1 for k in kws if k in m)
        if s > best_s:
            best, best_s = dom, s
    return best if best_s > 0 else None


def _intent(m: str):
    for kws, replies in SMALLTALK:
        if any(re.search(r"\b" + re.escape(k) + r"\b", m) for k in kws):
            return "smalltalk", replies
    for kws, reply in PERSONAL:
        if any(k in m for k in kws):
            return "personal", reply
    return None, None


def answer(message: str, domain: str | None = None) -> dict:
    m = (message or "").lower().strip()
    if not m:
        return {"answer": "I am here whenever you are ready. What would you like to talk about?", "title": "Ava", "domain": domain, "disclaimer": "", "matched": True}

    kind, payload = _intent(m)
    if kind == "smalltalk":
        return {"answer": _pick(m, payload), "title": "Ava", "domain": domain, "disclaimer": "", "matched": True}
    if kind == "personal":
        return {"answer": payload, "title": "A steadier footing", "domain": domain, "disclaimer": "", "matched": True}

    dom = classify_domain(m) or domain
    tokens = set(w.strip(".,!?") for w in m.split())
    best, best_s = None, 0
    for e in KB:
        s = 0
        for k in e["kw"]:
            if k in m:
                s += 3
            elif set(k.split()) & tokens:
                s += 1
        for w in e["title"].lower().split():
            if w in tokens:
                s += 1
        if s > best_s:
            best, best_s = e, s

    advice = any(w in m for w in ("invest", "should i", "advice", "buy", "market", "stock", "portfolio", "fund"))
    if best and best_s >= 2:
        body = best["a"]
        if dom and dom in DOMAIN_ANSWER and best_s < 5:
            body += f"\n\nSince this touches {DOMAIN_LABEL[dom]}: {DOMAIN_ANSWER[dom]}"
        text = f"{body}\n\nA principle to hold onto: {_pick(m, PRINCIPLES)}"
        return {"answer": text, "title": best["title"], "domain": dom, "disclaimer": DISCLAIMER if advice else "", "matched": True}

    if dom and dom in DOMAIN_ANSWER:
        text = f"{DOMAIN_ANSWER[dom]}\n\nA principle to hold onto: {_pick(m, PRINCIPLES)}"
        return {"answer": text, "title": DOMAIN_LABEL[dom], "domain": dom, "disclaimer": DISCLAIMER if advice else "", "matched": True}

    return {
        "answer": f"Good question, and I do not want to give you a generic non-answer. Here is a principle to anchor on: {_pick(m, PRINCIPLES)} If you tell me a little more, for example whether this is about saving, borrowing, investing, a suspicious charge, insurance, or a specific part of banking or markets, I will get specific fast.",
        "title": "Let us dig in", "domain": dom, "disclaimer": DISCLAIMER, "matched": False,
    }


def topics() -> list[dict]:
    return [{"id": e["id"], "title": e["title"]} for e in KB]


def domains() -> list[dict]:
    return [{"id": d, "label": DOMAIN_LABEL[d]} for d in DOMAIN_KW]
