from __future__ import annotations

import hashlib

DISCLAIMER = "This is general financial education, not personalized investment advice. For decisions about your money, speak with a licensed advisor."

PRINCIPLES = [
    "Spend less than you earn, and invest the difference for the long run. That gap, compounded patiently, is where wealth quietly comes from.",
    "The first rule is to avoid permanent loss. Protect your downside, keep an emergency cushion, and you will still be standing when opportunity shows up.",
    "Time in the market beats timing the market. Compounding rewards patience far more than cleverness.",
    "Buy quality and hold it. Frequent trading mostly enriches the people charging the fees.",
    "Diversify so no single mistake can sink you. You do not have to be right often if you are never ruined.",
    "Understand what you own. If you cannot explain it simply, it does not belong in your plan yet.",
    "High-interest debt is a guaranteed negative return. Clearing it is the safest high-yield investment most people will ever make.",
    "Be fearful when others are greedy and patient when others panic. Temperament, not IQ, decides outcomes.",
    "Pay yourself first. Automate savings before you can spend the money, and willpower stops being the bottleneck.",
    "Price is what you pay, value is what you get. Focus on value and let price take care of itself over time.",
]


def _principle(seed: str) -> str:
    i = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(PRINCIPLES)
    return PRINCIPLES[i]


KB = [
    {"id": "emergency_fund", "title": "Building an emergency fund", "kw": ["emergency", "rainy day", "buffer", "cushion", "savings safety", "unexpected"],
     "a": "An emergency fund is the foundation everything else rests on. Aim for three to six months of essential expenses held in a plain, instant-access savings account, separate from your spending money. Build it before you invest, because it is what stops a surprise car repair or a lost paycheck from turning into high-interest debt. Automate a small weekly transfer so it grows without you thinking about it, and only touch it for genuine emergencies."},
    {"id": "budget", "title": "Budgeting that actually sticks", "kw": ["budget", "spending plan", "track expenses", "50 30 20", "manage money", "overspend"],
     "a": "A budget is simply telling your money where to go before it disappears. A durable starting point is the 50/30/20 shape: roughly half your take-home for needs, a third for wants, and a fifth for saving and clearing debt. The trick is to make saving automatic and to review one number a week, not to log every coffee. Most people overspend on subscriptions and delivery, so a five-minute monthly audit of recurring charges usually finds real money."},
    {"id": "credit_score", "title": "How your credit score works", "kw": ["credit score", "bureau", "cibil", "fico", "improve credit", "creditworthy"],
     "a": "Your credit score is a lender's shorthand for how reliably you repay. The two levers that matter most are paying every bill on time and keeping your credit utilisation low, ideally under thirty percent of your limit. Length of history and a healthy mix of credit help at the margin. You do not need to carry a balance to build score; paying in full each month is ideal. Check your report yearly and dispute anything that looks wrong."},
    {"id": "compounding", "title": "The power of compounding", "kw": ["compound", "compounding", "interest on interest", "grow money", "long term"],
     "a": "Compounding is interest earning interest, and it is the closest thing to magic in finance. Money invested early has decades to snowball, which is why starting small at twenty-five beats starting large at forty. A useful shortcut is the rule of 72: divide 72 by your annual return to estimate the years it takes to double. At seven percent, money doubles about every ten years. The lesson is simple: start now, stay invested, and let time do the heavy lifting."},
    {"id": "investing_basics", "title": "Getting started with investing", "kw": ["invest", "investing", "stocks", "index fund", "etf", "market", "portfolio", "mutual fund"],
     "a": "For most people, low-cost, broadly diversified index funds are the sensible core. They spread your money across hundreds of companies, keep fees low, and remove the guesswork of picking winners. Invest a fixed amount on a regular schedule so you buy through ups and downs, and give it years, not weeks. Match how much risk you take to how soon you need the money: cash for near-term goals, a diversified mix for the long ones."},
    {"id": "diversification", "title": "Why diversification matters", "kw": ["diversify", "diversification", "spread risk", "concentration", "asset allocation"],
     "a": "Diversification means not letting any single company, sector, or currency decide your future. By holding many uncorrelated assets, a bad outcome anywhere becomes survivable everywhere. It will not make you rich overnight, and that is the point: it keeps you in the game long enough for compounding to work. The simplest version is a broad global index fund plus some bonds or cash sized to your comfort with swings."},
    {"id": "retirement", "title": "Planning for retirement", "kw": ["retirement", "retire", "pension", "401k", "nps", "ppf", "future"],
     "a": "Retirement planning is really about buying your future self freedom. Contribute enough to capture any employer match first, because that is an instant return you will not find anywhere else. Then automate steady contributions into tax-advantaged, diversified funds and increase them a little each time your income rises. The two biggest drivers of the outcome are how early you start and how consistent you are, not how clever your fund picks are."},
    {"id": "debt_payoff", "title": "Paying down debt", "kw": ["debt", "loan payoff", "credit card debt", "emi", "interest", "avalanche", "snowball"],
     "a": "Not all debt is equal. Clear high-interest debt, especially credit cards, as fast as you can, because avoiding a twenty percent interest charge is a guaranteed twenty percent return. Two proven methods work: the avalanche pays highest-rate balances first to save the most money, while the snowball clears the smallest balances first for motivating quick wins. Keep making minimums on everything, then throw every spare rupee or dollar at the target balance."},
    {"id": "fraud_safety", "title": "Protecting yourself from fraud", "kw": ["fraud", "scam", "phishing", "unauthorized", "stolen", "safe", "security", "otp"],
     "a": "Most fraud starts with urgency and a request to move money or share a code. A real bank will never ask for your full password, PIN, or a one-time code over a call or message. Turn on transaction alerts, use a unique password and app-based two-factor authentication, and pause whenever something feels rushed. If you spot a charge you do not recognise, report it immediately; the sooner you flag it, the more protection you have."},
    {"id": "dispute", "title": "Disputing a charge you do not recognise", "kw": ["dispute", "chargeback", "unauthorized charge", "wrong charge", "refund", "not recognise"],
     "a": "If a charge looks wrong, act quickly. First confirm it is not a forgotten subscription or a merchant name you do not recognise. If it is genuinely unauthorised, report it to your bank so they can freeze the card and open a dispute; card networks give you the right to challenge fraudulent and incorrect charges. Keep any receipts or messages, note the date you reported it, and you are generally protected while the investigation runs."},
    {"id": "loan", "title": "Borrowing sensibly", "kw": ["loan", "borrow", "mortgage", "pre-approved", "credit offer", "apr", "interest rate"],
     "a": "Borrow for things that build value or are genuine needs, and treat the interest rate and total cost, not the monthly payment, as the real price. Before you sign, compare the annual rate across lenders, check for fees, and make sure the repayment fits comfortably inside your budget with room to spare. A pre-approved offer is a starting point, not an obligation; it is worth shopping around and reading the terms in full."},
    {"id": "insurance", "title": "How much insurance you need", "kw": ["insurance", "cover", "term life", "health cover", "premium", "protect family"],
     "a": "Insurance exists to protect against losses you could not absorb yourself, not to cover small, affordable ones. Prioritise health cover and, if people depend on your income, term life insurance, which is cheap because it is pure protection with no investment attached. Buy enough to cover your dependents' needs and outstanding debts, and revisit it after big life events like a marriage, a child, or a new home."},
    {"id": "saving_goals", "title": "Saving for a specific goal", "kw": ["save for", "goal", "house", "car", "wedding", "down payment", "vacation"],
     "a": "Give every goal a name, a number, and a date, then work backwards to a monthly amount. Keep short-term goals, anything you need within three years, in safe cash-like savings so a market dip cannot derail your timeline; let longer goals ride in diversified investments. Automating the transfer on payday is what turns a vague wish into a funded plan, because the money is set aside before you can spend it."},
    {"id": "cashflow", "title": "Understanding your cash flow", "kw": ["cash flow", "income", "money in money out", "paycheck", "salary", "where money goes"],
     "a": "Cash flow is the honest picture of money coming in versus going out. Track it for one month and you will usually find a few silent leaks and one or two categories worth trimming. The goal is a consistent positive gap between income and spending, which you then direct toward savings and investments. Modern banks can categorise this for you automatically, so use those insights rather than counting by hand."},
    {"id": "market_view", "title": "Reading the market without panic", "kw": ["market view", "stock market", "volatility", "crash", "recession", "downturn", "should i sell"],
     "a": "Markets rise over the long run but lurch in the short run, and the headlines are loudest exactly when it is least useful to react. Downturns are a normal cost of the higher returns equities offer over time. If your money is invested for a goal years away, the wisest move during a fall is usually to keep contributing on schedule and avoid selling in fear. Match your risk to your timeline, and volatility becomes noise rather than danger."},
]

_ACTION_HINTS = ("loan", "pre-approved", "preapproved", "dispute", "chargeback", "unauthorized",
                 "unauthorised", "transfer", "pay ", "send money", "block card")


def is_action(message: str) -> bool:
    m = message.lower()
    return any(h in m for h in _ACTION_HINTS)


def _score(entry: dict, tokens: set[str], m: str) -> int:
    s = 0
    for k in entry["kw"]:
        if k in m:
            s += 3
        elif set(k.split()) & tokens:
            s += 1
    for w in entry["title"].lower().split():
        if w in tokens:
            s += 1
    return s


def answer(message: str) -> dict:
    m = (message or "").lower().strip()
    tokens = set(w.strip(".,!?") for w in m.split())
    best, best_s = None, 0
    for e in KB:
        s = _score(e, tokens, m)
        if s > best_s:
            best, best_s = e, s
    if best and best_s >= 2:
        body = best["a"]
        advice = "invest" in m or "should i" in m or "advice" in m or "buy" in m or "market" in m
        text = f"{body}\n\nA principle to hold onto: {_principle(m)}"
        return {"answer": text, "title": best["title"],
                "disclaimer": DISCLAIMER if advice else "", "matched": True}
    return {
        "answer": f"Here is how I would think about that. {_principle(m)} If you tell me a little more, for example whether this is about saving, borrowing, investing, a suspicious charge, or planning for a goal, I can be far more specific.",
        "title": "A place to start", "disclaimer": DISCLAIMER, "matched": False,
    }


def topics() -> list[dict]:
    return [{"id": e["id"], "title": e["title"]} for e in KB]
