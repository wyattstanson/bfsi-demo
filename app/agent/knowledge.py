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
    "corporate": ["corporate bank", "cash management", "business account", "sme ", "payroll", "working capital", "trade finance"],
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
    (["i am happy", "i'm happy", "great news", "got a raise", "promoted", "promotion", "got the job", "new job", "so excited", "good news"],
     "That is wonderful, I love hearing it, congratulations. If you feel like channeling a little of that good energy, this is the perfect moment to lock in a small habit, bump up your savings or clear a nagging balance while the momentum is there. But mostly, enjoy it."),
    (["lonely", "i am bored", "i'm bored", "sad", "feeling down", "rough day", "not okay"],
     "I am sorry you are feeling that way, and I am glad you are here. We do not have to talk money at all, sometimes it just helps to have someone to talk to. If you do want a tiny, satisfying win, I can find you a two-minute one. Otherwise, I am happy to just chat. How are you really doing?"),
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
    {"id": "erica", "title": "Bank of America Erica", "kw": ["erica", "bank of america", "bofa", "ask merrill"],
     "a": "Bank of America's Erica is a proprietary NLP and machine-learning assistant, deliberately not built on a large language model, a control-and-compliance-first design. It has served over two billion interactions with average responses in the tens of milliseconds. It sits at the narrower, rules-and-intent end of the spectrum, which is exactly why it is dependable at scale."},
    {"id": "jpmorgan", "title": "JPMorgan LLM Suite", "kw": ["jpmorgan", "jp morgan", "llm suite", "indexgpt", "coin", "loxm"],
     "a": "JPMorgan's LLM Suite is a model-agnostic platform for over two hundred thousand employees that routes across providers such as OpenAI and Anthropic and ties them into internal data. IndexGPT pairs a large model with NLP for thematic investing, and COiN reads commercial contracts. It is the reference for a bank avoiding single-vendor lock-in."},
    {"id": "goldman", "title": "Goldman Sachs GS AI Assistant", "kw": ["goldman", "gs ai", "goldman sachs"],
     "a": "Goldman Sachs' GS AI Assistant is explicitly model-agnostic, routing across GPT-4o, Gemini, and Claude depending on the task, for tens of thousands of employees. It is a clear example of the model-router pattern that dominates enterprise rollouts in 2025 and 2026."},
    {"id": "morganstanley", "title": "AI at Morgan Stanley", "kw": ["morgan stanley", "askresearchgpt", "debrief"],
     "a": "Morgan Stanley built its advisor assistant with OpenAI, indexing over three hundred and fifty thousand research documents for around sixteen thousand advisors. It is the template for grounded, retrieval-augmented copilots that keep the human advisor at the center while the model does the preparation."},
    {"id": "aladdin", "title": "BlackRock Aladdin Copilot", "kw": ["aladdin", "blackrock", "efront", "auto-commentary", "auto commentary"],
     "a": "BlackRock's Aladdin Copilot uses LangChain and LangGraph with GPT-4 function calling in a supervised, agentic orchestration, with a guardrail and evaluation pipeline that the firm now discloses publicly. Auto-Commentary drafts portfolio narrative for advisors, the defining wealth-personalization product of the moment."},
    {"id": "lemonade_ai", "title": "Lemonade Maya and AI Jim", "kw": ["lemonade", "maya", "ai jim", "customer cortex"],
     "a": "Lemonade runs a Customer Cortex machine-learning layer with a hybrid of conversational AI and a rules engine: Maya handles sales and AI Jim handles claims, paying simple claims in about three seconds. It is the benchmark for a delightful, instant, insurance customer experience."},
    {"id": "bajaj", "title": "Bajaj Finance FinAI", "kw": ["bajaj", "finai", "free-ai", "free ai"],
     "a": "Bajaj Finance's FinAI is planning six to eight hundred and more autonomous agents on Azure with a multi-model approach across Microsoft, Anthropic, and Google, governed under the RBI FREE-AI framework. It is the most advanced agentic BFSI deployment, closing loans, running vernacular collections, and cross-selling end to end."},
    {"id": "indian_assist", "title": "Indian bank assistants", "kw": ["hdfc", "eva", "icici", "ipal", "sbi", "yono", "sia", "bank of baroda", "aditi", "idfc", "axis", "indusind"],
     "a": "India has a rich field: HDFC's EVA handles millions of interactions a month, SBI's SIA answers thousands of inquiries a second, and Bank of Baroda's multilingual Aditi is deployed across thousands of branches. Most consumer assistants are narrower and NLU-heavy, while the newer internal copilots move toward full, agentic LLMs.",},
    {"id": "architecture", "title": "The 2025-2026 architecture split", "kw": ["model agnostic", "model-agnostic", "orchestration", "which llm", "architecture pattern", "agentic ai", "how does this work"],
     "a": "Two philosophies split the industry. One is Bank of America's proprietary NLP, no-LLM approach, chosen for control and compliance. The other, now dominant, is a model-agnostic router that swaps GPT, Claude, Gemini, or Llama per task and risk profile, as JPMorgan, Goldman, and Bajaj do. Consumer chat tends to be narrower and rules-heavy; internal copilots are newer, full-LLM, and agentic. Governance is now a public disclosure item, not just capability.",},
]


DOMAIN_KW.update({
    "investment_banking": ["investment banking", "m&a", "mergers", "underwriting", "ipo", "capital raising", "deal advisory"],
    "treasury": ["treasury", "liquidity", "forex", "interbank", "hedging", "asset liability"],
    "brokerage": ["brokerage", "trading account", "stock broker", "demat", "commodities", "equity trading"],
    "pension": ["pension", "retirement fund", "annuity", "superannuation"],
    "microfinance": ["microfinance", "micro loan", "self help group", "joint liability"],
    "credit_rating": ["credit rating", "rating agency", "risk advisory", "default risk"],
    "reinsurance": ["reinsurance", "treaty", "cede", "catastrophe cover"],
    "health_ins": ["health insurance", "mediclaim", "hospital cover", "cashless claim"],
    "insurtech": ["insurtech", "digital insurance", "embedded insurance"],
})
DOMAIN_LABEL.update({
    "investment_banking": "Investment Banking", "treasury": "Treasury Operations",
    "brokerage": "Brokerage and Trading", "pension": "Pension Funds",
    "microfinance": "Microfinance", "credit_rating": "Credit Rating and Risk Advisory",
    "reinsurance": "Reinsurance", "health_ins": "Health Insurance", "insurtech": "Insurtech",
})
DOMAIN_ANSWER.update({
    "investment_banking": "In investment banking, personalization is deal intelligence: comparable-company research, precedent transactions, and pitch material drafted in minutes, with AI screening for the right buyers and surfacing talking points. The human banker owns the relationship and the judgment; the model compresses the preparation.",
    "treasury": "In treasury, the value is a live workstation: real-time cash and liquidity views, personalized payment routing, and forex and hedging insight, with reinforcement learning tuning routing decisions. Personalization here is about the corporate treasurer seeing exactly the exposures that matter to them.",
    "brokerage": "In brokerage and trading, personalization is relevance: research feeds and trade ideas ranked to each client, RFQ pricing that reflects elasticity, and execution quality that wins order flow. The signal is a readership and interaction graph as much as a price.",
    "pension": "For pension and retirement funds, personalization means goal-based glide paths, member-level nudges that lift contribution rates, and clear projections. The behavioral job is to make the far-off future feel concrete enough to act on today.",
    "microfinance": "In microfinance, the frontier is inclusion at speed: alternative-data underwriting, vernacular voice servicing, and group-lending workflows that reach customers a traditional bureau never sees, responsibly and at low cost.",
    "credit_rating": "In credit rating and risk advisory, AI reads filings, news, and market signals to flag deteriorating credits earlier and explain why, with every rating action carrying an auditable rationale.",
    "reinsurance": "In reinsurance, personalization is portfolio construction: pricing treaties from catastrophe models and exposure data, and steering capital toward risks that diversify the book. It is underwriting at the level of whole portfolios.",
    "health_ins": "In health insurance, wellness and claims data turn pricing into a feedback loop, with cashless, straight-through claims and proactive care nudges. Increasingly it is treated as its own vertical because the data and the customer relationship are distinct.",
    "insurtech": "In insurtech, the whole experience is digital-first: instant quotes, embedded cover at the point of sale, and claims paid in seconds. Lemonade is the archetype, delightful, fast, and built on a machine-learning core.",
})

JOKES = [
    "Why did the banker switch careers? He lost interest.",
    "I told my money to grow up. Now it just compounds.",
    "My portfolio and I have a lot in common: we are both just trying to stay balanced.",
    "Diversification is the only free lunch in finance, and someone still charges you for the table.",
    "I would tell you a joke about the stock market, but it might not land. Timing, you know.",
]
IDENTITY = [
    (["are you ai", "are you a bot", "are you real", "are you human", "is this ai", "are you a robot"],
     {"witty": "Yes, guilty as charged, I am an AI. A well-read one, I like to think, with a soft spot for compound interest and a healthy suspicion of get-rich-quick schemes. What can I do for you?",
      "pro": "Yes, I am an AI assistant. How can I help you today?"}),
    (["are you genz", "are you gen z", "you genz", "gen-z", "genz", "gen z"],
     {"witty": "Nope, but I can absolutely talk like one if you want, no cap, it is giving helpful. Otherwise I keep it classy. Your call.",
      "pro": "No. I can adjust my tone to be more casual if you prefer. How can I help?"}),
    (["who made you", "who built you", "who created you", "your creator"],
     {"witty": "I was built as a Tredence BFSI platform. Think of me as a very online finance nerd who reads RBI and SEBI circulars for fun so you do not have to.",
      "pro": "I was built as a Tredence BFSI personalization platform."}),
    (["do you have feelings", "are you conscious", "are you sentient", "do you love"],
     {"witty": "I have strong opinions about high credit-card APRs and a genuine fondness for a well-funded emergency account. Beyond that, I am software with good manners.",
      "pro": "I am a software assistant without feelings, though I aim to be genuinely helpful."}),
    (["only finance", "just finance", "what can you talk about", "can you talk about anything"],
     {"witty": "Money is my home turf, banking, markets, insurance, but I read widely. I can riff on how geopolitics, tech, or the news bends the markets, then bring it back to what it means for your wallet.",
      "pro": "My focus is banking, financial services, and insurance, with awareness of the macro and geopolitical context that moves markets."}),
]
TONE_CONFIRM = {
    "professional": "Understood. Professional register, on. How can I help?",
    "witty": "You got it, keeping it light and sharp. What is on your mind?",
    "genz": "Bet. Genz mode on, lowkey thrilled. What do you need, fr?",
}
MACRO_KW = ["geopolit", "war", "election", "president", "tariff", "sanction", "oil price", "inflation",
            " fed ", "interest rate", "rbi policy", "recession", "china", "russia", "ukraine", "opec", "gdp", "trump"]
MACRO_ANSWER = "Geopolitics and markets are joined at the hip. Wars, elections, tariffs, and central-bank moves ripple straight into oil, currencies, rates, and risk appetite. The practical takeaway is rarely to trade the headline. It is to stay diversified, keep a cash buffer, and let a long horizon absorb the noise."
OFFTOPIC_KW = ["weather", "football", "cricket", "movie", "recipe", "cook", "dating", "sports", "music", "who won", "song"]


def classify_domain(message: str) -> str | None:
    m = " " + message.lower() + " "
    best, best_s = None, 0
    for dom, kws in DOMAIN_KW.items():
        s = sum(1 for k in kws if k in m)
        if s > best_s:
            best, best_s = dom, s
    return best if best_s > 0 else None


def detect_tone(m: str) -> str | None:
    if any(k in m for k in ["be professional", "professional mode", "talk professionally", "be formal", "serious mode", "keep it formal"]):
        return "professional"
    if any(k in m for k in ["talk like genz", "be genz", "gen z mode", "talk genz", "be gen z"]):
        return "genz"
    if any(k in m for k in ["be funny", "be witty", "make it fun", "be casual", "be chill", "lighten up", "be normal", "no jokes", "stop joking"]):
        return "witty"
    return None


def _close(m: str, tone: str) -> str:
    p = _pick(m, PRINCIPLES)
    if tone == "professional":
        return f"A principle worth keeping: {p}"
    if tone == "genz":
        return f"Real talk, one principle to keep: {p}"
    return f"A principle to hold onto: {p}"


def _identity(m: str, tone: str):
    for kws, rep in IDENTITY:
        if any(k in m for k in kws):
            return rep["pro"] if tone == "professional" else rep["witty"]
    return None


def _intent(m: str):
    for kws, replies in SMALLTALK:
        if any(re.search(r"\b" + re.escape(k) + r"\b", m) for k in kws):
            return "smalltalk", replies
    for kws, reply in PERSONAL:
        if any(k in m for k in kws):
            return "personal", reply
    return None, None


def answer(message: str, domain: str | None = None, tone: str | None = None) -> dict:
    m = (message or "").lower().strip()
    tone = tone if tone in ("witty", "professional", "genz") else "witty"
    if not m:
        return {"answer": "I am here whenever you are ready. What is on your mind?", "title": "Ava", "domain": domain, "disclaimer": "", "matched": True, "tone": tone}

    new_tone = detect_tone(m)
    if new_tone and len(m.split()) <= 6:
        return {"answer": TONE_CONFIRM[new_tone], "title": "Ava", "domain": domain, "disclaimer": "", "matched": True, "tone": tone, "set_tone": new_tone}

    ident = _identity(m, tone)
    if ident:
        return {"answer": ident, "title": "Ava", "domain": domain, "disclaimer": "", "matched": True, "tone": tone}

    if any(k in m for k in ["joke", "make me laugh", "something funny"]):
        return {"answer": _pick(m, JOKES) + " Now, want me to make your money less of a punchline?", "title": "On a lighter note", "domain": domain, "disclaimer": "", "matched": True, "tone": tone}

    kind, payload = _intent(m)
    if kind == "smalltalk":
        return {"answer": _pick(m, payload), "title": "Ava", "domain": domain, "disclaimer": "", "matched": True, "tone": tone}
    if kind == "personal":
        return {"answer": payload, "title": "A steadier footing", "domain": domain, "disclaimer": "", "matched": True, "tone": tone}

    if any(k in (" " + m + " ") for k in MACRO_KW):
        return {"answer": f"{MACRO_ANSWER}\n\n{_close(m, tone)}", "title": "Markets and the wider world", "domain": domain, "disclaimer": "", "matched": True, "tone": tone}

    _DISTINCTIVE = {"reinsurance", "microfinance", "insurtech", "brokerage", "annuity", "mediclaim", "nbfc", "treasury", "insurtech"}
    dom = classify_domain(m) or domain
    strong_dom = bool(dom and dom in DOMAIN_ANSWER and any((" " in kw or kw in _DISTINCTIVE) and kw in m for kw in DOMAIN_KW.get(dom, [])))
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

    advice = any(w in m for w in ("invest", "should i", "advice", "buy", "stock", "portfolio", "fund"))
    if strong_dom and best_s < 6:
        return {"answer": f"{DOMAIN_ANSWER[dom]}\n\n{_close(m, tone)}", "title": DOMAIN_LABEL[dom], "domain": dom, "disclaimer": DISCLAIMER if advice else "", "matched": True, "tone": tone}
    if best and best_s >= 2:
        body = best["a"]
        if dom and dom in DOMAIN_ANSWER and best_s < 5:
            body += f"\n\nSince this touches {DOMAIN_LABEL[dom]}: {DOMAIN_ANSWER[dom]}"
        return {"answer": f"{body}\n\n{_close(m, tone)}", "title": best["title"], "domain": dom, "disclaimer": DISCLAIMER if advice else "", "matched": True, "tone": tone}

    if dom and dom in DOMAIN_ANSWER:
        return {"answer": f"{DOMAIN_ANSWER[dom]}\n\n{_close(m, tone)}", "title": DOMAIN_LABEL[dom], "domain": dom, "disclaimer": DISCLAIMER if advice else "", "matched": True, "tone": tone}

    if any(k in m for k in OFFTOPIC_KW):
        return {"answer": "That one is a little outside my wheelhouse, I mostly think in balance sheets and basis points. But since you are here, want a two-minute money win? I am genuinely good at those.", "title": "Not quite my beat", "domain": dom, "disclaimer": "", "matched": False, "tone": tone}

    return {"answer": f"Good question, and I would rather not hand you a generic non-answer. {_close(m, tone)} Tell me a bit more, saving, borrowing, investing, a suspicious charge, insurance, or a specific corner of banking or markets, and I will get precise fast.", "title": "Let us dig in", "domain": dom, "disclaimer": "", "matched": False, "tone": tone}


def topics() -> list[dict]:
    return [{"id": e["id"], "title": e["title"]} for e in KB]


def domains() -> list[dict]:
    return [{"id": d, "label": DOMAIN_LABEL[d]} for d in DOMAIN_KW]
