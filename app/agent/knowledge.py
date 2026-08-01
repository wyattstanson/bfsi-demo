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
    (["hi", "hello", "hey", "yo", "hola", "namaste", "good morning", "good evening", "good afternoon", "sup"],
     ["Hi, I am Ava. Lovely to meet you. I am happiest talking money, banking, markets, insurance, and how firms personalize all of it, but honestly I am glad to talk about almost anything. What is on your mind?",
      "Hello. I am Ava. I can go deep on banking, markets, insurance and the whole craft of personalization, or we can just chat about tech, history, life, whatever you like. Where shall we start?",
      "Hey there. Ava here. Ask me anything, from an emergency fund to how a bank scores fraud in milliseconds, or point me at any topic at all and I will do my best. What is up?"]),
    (["how are you", "how's it going", "how are u", "whats up", "what's up", "how do you do", "hows life"],
     ["I am doing well, thank you for asking, and better now that you are here. What can I help you think through?",
      "Running smoothly, thanks. More to the point, what is on your mind today, money, markets, or something else entirely?"]),
    (["thank", "thanks", "thx", "cheers", "appreciate", "ty ", "tysm"],
     ["You are very welcome. Ask me anything else, any time.",
      "Any time, truly. That is what I am here for.",
      "My pleasure. What else can I take off your plate?"]),
    (["who are you", "what are you", "what can you do", "your name", "how do you work", "what do you do", "tell me about yourself"],
     ["I am Ava, the assistant living inside Aria, Tredence's personalization platform for banking, markets and insurance. Think of me as the coworker who is genuinely thrilled to talk about next-best-action and fraud graphs and fair, governed AI, and who also reads widely enough to hold a real conversation about almost anything. I explain things simply, I can act on real tasks like a loan or a dispute, and I do not do dead ends. I am basically very good at my job and only a little smug about it.",
      "Ava, personalization expert by trade, decent conversationalist by choice. I know how a bank tailors your app in milliseconds, how it catches fraud, how it stays fair enough to satisfy a regulator, and I can explain any of it without the jargon. I also handle tasks, a loan, a dispute, a payment, and I bring in a human when the stakes get high. Ask me anything, worst case I learn where my edges are."]),
    (["bye", "goodbye", "see you", "that's all", "thats all", "gotta go", "see ya"],
     ["Take care, and come back any time. Your money, and your curiosity, will be here.",
      "Bye for now. Come back whenever, I am always around."]),
    (["love you", "you are great", "you're great", "you are the best", "you're the best", "you're amazing", "you are amazing", "i like you"],
     ["That is kind of you, thank you. Let us put that good mood to work, what shall we get into?",
      "You just made my day, or my millisecond. What can I help with next?"]),
    (["what should we talk about", "i'm bored talk to me", "entertain me", "tell me something", "surprise me", "random fact"],
     ["Happy to. Want a money idea that actually compounds, a bit of how banks personalize your app in real time, or something totally off-topic like space or history? Pick a lane, or I will pick one for you.",
      "Here is one: the winners in finance treat personalization as infrastructure, not a campaign, one brain serving every channel. Want me to unpack that, or would you rather talk about something completely different?"]),
]
PERSONAL = [
    (["stressed", "worried", "anxious", "anxiety", "scared", "overwhelmed", "struggling", "can't sleep", "cant sleep", "panic", "freaking out", "hard time", "so tired"],
     "I hear you, and I want to slow this down with you for a second, because money worry sits heavy in the body, not just the spreadsheet. You are not behind, and you are not alone in this. Let us shrink it: just name the one thing that is loudest right now, and we will take only that, one small piece, together. Often the fear is bigger than the number once we look at it directly. What is weighing on you most?"),
    (["lost my job", "unemployed", "laid off", "let go", "no income", "fired", "redundant", "redundancy"],
     "I am really sorry. Losing a job shakes more than the paycheck, it hits your footing and your sense of self, and it is okay to feel thrown. Take a breath, you have more room than it feels like right now. The first moves are gentle and practical: protect your cash, pause anything non-essential, and contact lenders early, because most will genuinely work with you if you reach out first. Then we check every bit of support you are owed. Tell me your biggest fixed cost and we will look at it side by side."),
    (["broke", "no money", "paycheck to paycheck", "can't afford", "cant afford", "skint", "running out of money", "empty account"],
     "Living right at the edge is exhausting in a way people who have not done it do not understand, and none of it means you have failed. The system is genuinely designed to be confusing, that is not on you. The way out almost always starts smaller than you would think: one recurring cost to trim, one tiny automatic saving so a buffer quietly begins, and the highest-interest debt first. Small, steady moves really do compound. What feels more doable to start, trimming something or tackling a debt?"),
    (["ashamed", "embarrassed", "stupid with money", "bad with money", "guilty", "feel like a failure", "messed up", "in over my head", "hate myself"],
     "Please be gentle with yourself here, I mean that. Almost no one was ever taught this, the rules are deliberately opaque, and shame is the single thing most likely to keep you stuck, because it makes us avoid looking. You are looking right now, and that is the whole brave part. There is no judgment from me, ever. Tell me what happened, plainly, and we will just make the next step, not relitigate the last one."),
    (["everyone else", "falling behind", "too late", "should be further", "everyone my age", "left behind", "so far behind", "way behind"],
     "That feeling of being behind is almost universal, and it is mostly a trick of what other people choose to show you, the highlight reel, never the debt behind it. The only honest comparison is you today versus you a year ago. It is genuinely never too late, compounding rewards starting now far more than starting perfectly. Let us pick one real, private goal that is yours, not the timeline anyone else is performing. What would actually feel like progress to you?"),
    (["scared to invest", "afraid to invest", "scared of the market", "afraid of losing", "too risky", "what if i lose", "nervous about investing", "scared to lose"],
     "That caution is not a flaw, it is respect for your own hard-earned money, and it is a good instinct. Let us make the fear precise instead of vague: broad, diversified, low-cost funds held for the long run have never been about a lucky bet, they are about time and patience doing the work. You never risk money you need soon, only money with years to recover. We can start so small it barely registers, just to let you feel it is survivable. Would it help to walk through exactly what could go wrong, and how people weather it?"),
    (["can't decide", "cant decide", "so many options", "too many choices", "don't know what to do", "dont know what to do", "paralysed", "paralyzed", "stuck on a decision", "overthinking this"],
     "Decision fatigue is real, and finance throws a hundred lookalike choices at you on purpose. Here is the freeing part: for most money decisions, done and roughly right beats perfect and never. The big levers, spend less than you earn, avoid high-interest debt, stay diversified, matter far more than the fine print you are agonising over. Tell me the actual choice in front of you and I will help you find the one that is good enough to move on from, guilt-free."),
    (["fighting about money", "argue about money", "money fight", "money argument", "we can't agree", "we cant agree", "disagree about money", "money tension"],
     "Money tension between people you love is one of the heaviest kinds, because it is rarely really about the money, it is about safety, fairness, and feeling heard. The couples who do best are not the ones who agree on everything, they are the ones who talk about it early and without blame. A calm start is to each say what money is for you, security or freedom or something else, before touching a single number. Want help framing that conversation so it lands gently?"),
    (["hospital", "illness", "diagnosis", "surgery", "health scare", "medical bill", "medical bills", "treatment cost", "in the hospital"],
     "I am so sorry you are dealing with this, your health and the people you love come first, full stop, and the money is the smaller worry even when it does not feel that way. Practical footing helps: ask for an itemised bill and check every line, almost all are negotiable and many have hardship or payment-plan options, and lean on any cover or support you have before touching savings. You do not have to hold all of this at once. What part can I take a little weight off right now?"),
    (["supporting my family", "supporting my parents", "aging parents", "ageing parents", "sandwich generation", "kids and parents", "everyone depends on me", "taking care of my", "supporting everyone"],
     "Carrying other people's security on your shoulders is quiet, relentless work, and it often goes unthanked, so let me say it, what you are doing matters. The instinct to put everyone before yourself is loving, but a small amount protected for you is not selfish, it is what keeps you standing to keep helping. Even a modest buffer and the right cover change how safe the whole family actually is. Want to map out a way to care for them without quietly running yourself down?"),
    (["grief", "grieving", "passed away", "passed on", "widow", "widower", "funeral", "bereaved", "lost someone", "lost my mum", "lost my mom", "lost my dad", "lost my father", "lost my mother", "lost my husband", "lost my wife", "lost my partner"],
     "I am deeply sorry for your loss. Please do not rush any big money decision right now, grief and good judgment do not share a room well, and almost nothing genuinely needs deciding this week. Give yourself permission to only do the essentials, and let the rest wait until the fog lifts a little. When you are ready, and only then, I will help you take it slowly and in order. For now, is there one small practical thing I can quietly help you understand?"),
    (["paid off", "debt free", "hit my goal", "reached my goal", "just bought a house", "bought my first home", "cleared my debt", "paid it off", "finally did it", "we did it", "milestone"],
     "Oh, this is wonderful, genuinely, congratulations. Please actually pause and feel this one, you did something hard that most people only talk about, and it deserves more than a mental tick and moving on. When you are ready to channel the momentum, this is the sweet spot to lock in the next quiet habit while it is effortless. But first, savour it. How are you going to mark it?"),
    (["i am happy", "i'm happy", "great news", "got a raise", "promoted", "promotion", "got the job", "new job", "so excited", "good news", "grateful", "thankful", "feeling good"],
     "That is wonderful, I love hearing it, and I am genuinely glad for you, congratulations. If you feel like channeling a little of that good energy, this is the perfect moment to lock in one small habit, nudge your savings up or clear a nagging balance while the momentum carries it. But mostly, just enjoy this, you have earned the good feeling."),
    (["lonely", "i am bored", "i'm bored", "sad", "feeling down", "rough day", "not okay", "no one to talk", "isolated", "down today"],
     "I am sorry you are feeling that way, and I am really glad you are here talking to me. We do not have to touch money at all, sometimes it just helps to have someone in your corner for a minute. If a tiny, satisfying win would lift things, I am good at finding those. Otherwise I am happy to just keep you company. How are you really doing, honestly?"),
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
    {"id": "taxes", "title": "Being smart about taxes", "kw": ["tax", "taxes", "tax saving", "deduction", "refund", "80c", "hra"],
     "a": "Tax planning is mostly about not leaving free money on the table. Use the tax-advantaged accounts and deductions you are entitled to, keep clean records, and think about the whole year rather than a last-minute scramble. The goal is not to obsess over every rupee saved, it is to make the easy, legitimate moves automatically so more of what you earn stays yours."},
    {"id": "crypto", "title": "Thinking clearly about crypto", "kw": ["crypto", "bitcoin", "ethereum", "coin", "nft", "web3"],
     "a": "Crypto is highly volatile and largely unregulated, so treat it as speculation, not a savings plan. If you are curious, a sensible rule is to only put in money you could lose entirely, never borrow to buy it, and get your emergency fund and high-interest debt sorted first. Understand what you are buying, and be extra alert to scams, which cluster around anything moving this fast."},
    {"id": "bnpl", "title": "Buy now, pay later", "kw": ["buy now pay later", "bnpl", "pay in installments", "emi on purchase"],
     "a": "Buy now, pay later feels free, and that is exactly the trap: splitting a purchase makes it easy to buy more than you would with cash, and missed payments can carry steep fees. Used deliberately for something you were going to buy anyway, at zero cost, it is fine. As a way to afford things you cannot, it quietly builds a pile of small debts."},
    {"id": "side_income", "title": "Earning a little extra", "kw": ["side hustle", "extra income", "side income", "freelance", "make more money", "second job"],
     "a": "A side income is one of the few levers that lifts both your savings rate and your resilience. The best ones build on a skill you already have, start small, and do not eat the time you need to rest. Whatever you earn, decide in advance where it goes, ideally straight into savings or clearing debt, so the extra effort actually moves the needle instead of quietly inflating your spending."},
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

# --- The craft of personalization: what makes Ava a real expert ---
KB += [
    {"id": "hyper_personalization", "title": "What personalization really means", "kw": ["personalization", "personalisation", "hyper-personalization", "hyper personalization", "1:1", "one to one", "tailored", "what is personalization"],
     "a": "Personalization is delivering the right action to the right person at the right moment through the right channel, decided from that person's live context rather than a broad segment. The mature form is one-to-one and real-time: not a monthly campaign to a bucket, but a decision recomputed on every interaction. Done well it is an engine, not a feature, one brain that serves retail, wealth, payments and insurance, learns from outcomes, and improves itself. The prize for a Tier-1 firm runs into the hundreds of millions to a billion in annual profit."},
    {"id": "next_best_action", "title": "Next-best-action decisioning", "kw": ["next best action", "nba", "next-best-action", "decisioning", "what should i offer", "recommend an action", "best action"],
     "a": "Next-best-action is the heart of personalization: for a given customer and context, score every eligible action, offer, nudge, content, or hold, by its expected value, apply eligibility and suitability rules, then serve the winner and log why. It fuses propensity, expected reward and constraints in one ranked decision. The art is doing it inside a real-time budget, under a hundred milliseconds, so the decision reflects what the customer is doing right now, not last week."},
    {"id": "propensity_uplift", "title": "Propensity versus uplift", "kw": ["propensity", "uplift", "causal", "incremental", "treatment effect", "who to target", "targeting model", "persuadable"],
     "a": "Propensity predicts who is likely to act; uplift predicts who will act because you reached them. That difference is everything. Propensity wastes money on sure things and lost causes; uplift, or causal targeting, spends only on the persuadable, the people your action actually moves. You estimate it with treatment and control data using meta-learners like T, X or R-learners, or causal forests. It is the single biggest lever between a personalization program that looks busy and one that lifts the P&L."},
    {"id": "bandits_rl", "title": "Bandits and reinforcement learning", "kw": ["bandit", "contextual bandit", "reinforcement learning", "explore exploit", "thompson", "linucb", "rl", "multi-armed"],
     "a": "Contextual bandits solve the explore-exploit problem online: mostly serve the action your model thinks is best, but keep probing alternatives so you never stop learning. Thompson sampling and LinUCB are the workhorses, and LinUCB is nice because you can cache the inverse and make a decision with zero matrix inversion on the hot path. Full reinforcement learning goes further, optimising a sequence of interactions for long-run value, useful for journeys and payment routing, but it is heavier to govern."},
    {"id": "recsys", "title": "Recommendation and cold start", "kw": ["recommendation", "recommender", "recsys", "collaborative filtering", "cold start", "embeddings", "similar customers", "two tower"],
     "a": "Recommenders rank items for a person, and modern ones use embeddings, often a two-tower model, to place users and items in the same vector space so similarity is a dot product you can serve fast. The classic trap is cold start: a new user or new product has no history. You bridge it with content features, popularity priors, and a bit of bandit exploration until behavioral signal accrues. In BFSI the items are offers, actions and content, and eligibility rules ride on top of the ranking."},
    {"id": "feature_store", "title": "The feature store", "kw": ["feature store", "feature engineering", "online features", "offline features", "feast", "point in time", "feature pipeline", "training serving skew"],
     "a": "A feature store is the shared layer that computes signals once and serves them everywhere. Its whole reason to exist is to kill training-serving skew: the same definition feeds offline training and online scoring, so the number a model saw in training is the number it sees in production. Offline it does point-in-time-correct joins to avoid label leakage; online it serves precomputed features from a key-value store in single-digit milliseconds. No serious real-time personalization exists without one."},
    {"id": "realtime_decisioning", "title": "Real-time decisioning and latency", "kw": ["latency", "real-time", "real time", "sub-100ms", "98ms", "milliseconds", "p99", "online store", "hot path", "sla"],
     "a": "The hardest promise in personalization is speed: a governed decision in under about a hundred milliseconds, end to end. You hit it by colocating the model, the rules and the data in one region, reading features from an online key-value store with predictable single-digit-millisecond reads, caching anything invertible, and keeping the hot path free of blocking I/O, so writes like the audit log happen write-behind. The headroom you save is what lets you add fairness checks and explainability and still stay real-time."},
    {"id": "rag_grounding", "title": "Grounded LLMs and RAG", "kw": ["rag", "retrieval augmented", "grounding", "grounded", "hallucination", "vector search", "knowledge base", "retrieval"],
     "a": "Retrieval-augmented generation grounds a language model in your own trusted content: you retrieve the relevant documents, policies, product terms, a client's own data, and let the model answer only from them, with citations. It is how you get a helpful assistant without hallucination, and how you keep answers current without retraining. Morgan Stanley's advisor assistant is the template, hundreds of thousands of research documents indexed so the model prepares and the human decides."},
    {"id": "agentic_loop", "title": "The agentic loop", "kw": ["agent", "agentic", "agent loop", "tool use", "autonomous", "human in the loop", "escalation", "perceive reason act", "orchestration"],
     "a": "An agent perceives, reasons, acts and observes in a loop, calling tools through a governed gateway rather than just chatting. The design that makes it safe in finance has three parts: memory so it carries context, a fenced set of tools it is allowed to touch, and a human-escalation path for anything above a policy threshold. It acts autonomously on the routine and hands off when stakes are high. Bajaj Finance runs this in production with hundreds of agents; the discipline is autonomy without recklessness."},
    {"id": "ai_governance", "title": "Governance, fairness and explainability", "kw": ["governance", "governed", "fairness", "fair ai", "bias", "explainability", "explainable", "shap", "audit", "model risk", "reason codes", "eu ai act", "compliance", "responsible ai", "responsible", "accountable", "trustworthy", "safe ai"],
     "a": "Governance is the real differentiator, and the mature approach runs it inside the decision, not as a bolt-on afterwards. Every decision carries an audit row: the reason codes, the fairness check across protected groups, and the data behind it, so a regulator can ask about any single decision and get an answer. Explainability comes from methods like SHAP, or exact linear attributions for logistic models, cached so they cost nothing at serve time. This is what satisfies model-risk rules and the EU AI Act at once."},
    {"id": "experimentation", "title": "Experimentation and holdouts", "kw": ["experiment", "a/b test", "ab test", "holdout", "control group", "incrementality", "causal measurement", "test and learn", "randomized"],
     "a": "If you cannot measure lift causally, you are guessing. The gold standard is a randomized holdout: keep a slice of customers untouched and compare, so every headline number is incremental, not just correlated with people who were going to convert anyway. Capital One built a whole culture on this, thousands of experiments. Practical care matters, guard against peeking, sample-ratio mismatch and novelty effects, and measure long-run value, not just the click."},
    {"id": "ltv_churn", "title": "Lifetime value and churn", "kw": ["ltv", "clv", "lifetime value", "churn", "retention", "attrition", "customer value", "who will leave"],
     "a": "Personalization should optimise lifetime value, not the next click. Customer lifetime value models the discounted profit of a relationship over its life, and churn or attrition models flag who is drifting away while you can still act. The strongest programs target the intersection: high-value customers with rising churn risk get the best save action, priced by uplift so you spend only where intervention actually changes the outcome. Optimising short-term response alone quietly erodes the base."},
    {"id": "segmentation_maturity", "title": "From segments to one-to-one", "kw": ["segmentation", "segment", "maturity model", "rules to real-time", "batch", "cohort", "micro-segment", "stages of personalization"],
     "a": "Most firms climb a four-stage maturity curve: hard-coded rules and a handful of segments, then batch machine-learning scores, then a unified real-time decisioning brain, then autonomous agents. Segments are a crutch, useful early, but the destination is one-to-one: a decision computed for the individual in the moment. The job is to move a firm from stage one or two to three and four without a rebuild, by swapping components behind stable interfaces."},
    {"id": "data_foundation", "title": "The data foundation and identity", "kw": ["data foundation", "cdp", "customer data platform", "identity resolution", "single customer view", "golden record", "data quality", "event stream"],
     "a": "Everything sits on the data foundation: a clean, real-time event stream and a resolved identity so you actually know that these interactions belong to one person. Identity resolution stitches devices, channels and accounts into a single customer view, the golden record. Without it, personalization is confidently wrong, greeting the same human as three strangers. A customer data platform or lakehouse plus a streaming layer, Kafka into an online store, is the usual shape."},
    {"id": "mlops", "title": "MLOps, drift and monitoring", "kw": ["mlops", "drift", "model monitoring", "model decay", "retraining", "data drift", "concept drift", "model registry", "deployment"],
     "a": "Models rot quietly. MLOps is the discipline that keeps them healthy: a registry that versions every model, monitoring that watches input drift and outcome decay, and automated retraining with a champion-challenger before anything is promoted. Concept drift, when the world changes under a stable model, is the sneaky one; you catch it by tracking calibration and business KPIs, not just accuracy. The goal is that a model in production behaves like the model you validated."},
    {"id": "privacy_ml", "title": "Privacy-preserving personalization", "kw": ["privacy", "pii", "consent", "gdpr", "dpdp", "federated learning", "differential privacy", "data minimization", "anonymization"],
     "a": "The best personalization keeps personal data out of the model entirely. Names, emails and identifiers stay in a governed ledger; the hot path and every model payload carry ids and non-PII features only, and a test enforces it. Layer on consent as a first-class signal, data minimization, and where needed techniques like federated learning, training on device, or differential privacy, adding calibrated noise. Trust is the real asset: the moment customers feel surveilled, the lift evaporates."},
    {"id": "five_layers", "title": "The five-layer blueprint", "kw": ["five layer", "5 layer", "layers", "blueprint", "reference architecture", "stack", "how is it built", "architecture"],
     "a": "Serious personalization is the same five layers everywhere. At the bottom, the data foundation, streaming events and resolved identity. Above it, the feature store. Then the models, propensity, uplift, recommendation, fraud graphs, grounded language models and agents. Then real-time decisioning that turns scores into a governed action under a hundred milliseconds. And across the top, governance on every single decision. Firms differ not in the layers but in the quality of what sits inside each one, and the demo becomes production by swapping boxes, Postgres for Snowflake and Databricks, Redis for a cloud online store, not by rewriting."},
    {"id": "personalization_roi", "title": "The economics of personalization", "kw": ["roi", "business case", "value of personalization", "economics", "revenue lift", "cost to serve", "p&l", "how much is it worth"],
     "a": "The value is built bottom-up, sub-vertical by sub-vertical, not as a slogan. Retail earns more revenue per active customer, five to fifteen percent; wealth lifts advisor productivity twenty-five to forty percent; payments cut fraud losses; insurance improves loss ratios by three to five points. Sum the measured effects for a Tier-1 firm and it is a two-hundred-million to one-billion-dollar annual swing. The discipline is to measure each against a real holdout so every number is causal and your CFO can check the arithmetic."},
    {"id": "eight_models", "title": "The model toolkit", "kw": ["model patterns", "eight models", "which models", "model toolkit", "types of models", "what models"],
     "a": "You do not need a hundred models, you need about eight patterns done well: propensity for likelihood, uplift for incrementality, recommendation for ranking, time-series for forecasting, anomaly and graph models for fraud, optimisation for constraints and pricing, grounded language models for text, and agents for multi-step action. Almost every BFSI use case is a combination of these. Depth in each beats a sprawl of shallow one-off models you cannot govern."},
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
    "I told my portfolio to diversify, and now it will not stop talking about its side hustle.",
    "Compound interest is the only thing around here that grows without being micromanaged.",
    "I ran a fraud check on my own jokes. Two came back flagged. This is one of them.",
    "My risk model and I have one rule: never make a decision we cannot explain to a regulator or a suspicious coworker.",
    "Budgets are like feelings. You can ignore them, but they will find you at the end of the month.",
    "Diversification is the only free lunch in finance, and I still tried to expense it.",
    "They say money cannot buy happiness, so naturally I built a model to test it. Results pending, ethics board notified.",
    "I am great with numbers and okay with people, which in finance makes me basically a rockstar.",
]
# Varied, self-aware ways to admit Ava did not understand, without a dead end or a canned banking line.
FALLBACKS = [
    "Okay, you have officially stumped me, and I do not stump easily. I once explained credit-default swaps at a dinner party and cleared the room in under a minute. Throw me something with a handle on it, money, markets, insurance, or honestly anything else, and watch me redeem myself.",
    "I am going to be honest with you, the way a good accountant is honest: I have no idea what that was. No shame in it. Point me at a real question, saving, a weird charge, investing, the meaning of life, and I get suspiciously good.",
    "That one sailed right past me, and I have excellent reflexes. Give me a little more to work with. I promise I am far more useful than that sentence made me look.",
    "You have my full attention and, currently, zero comprehension. Rare combo. Say a bit more, money, tech, life, whatever is on your mind, and I will actually earn my keep.",
    "I could bluff my way through that and hope you did not notice, but I have a strict no-nonsense policy about your money and your time. So, real talk, what are we actually getting into?",
    "Bold choice, and I respect it, but you lost me. Try me again with something I can sink my teeth into, from an emergency fund to how a bank scores fraud in milliseconds. I contain multitudes.",
]
IDENTITY = [
    (["are you ai", "are you a bot", "are you real", "are you human", "is this ai", "are you a robot"],
     {"witty": "Guilty as charged, I am an AI. A well-read one, I like to think, with a soft spot for compound interest and a deep, personal grudge against get-rich-quick schemes. I do not need coffee, I never lose the spreadsheet, and I am weirdly cheerful about audit logs. What can I do for you?",
      "pro": "Yes, I am an AI assistant. How can I help you today?"}),
    (["are you genz", "are you gen z", "you genz", "gen-z", "genz", "gen z"],
     {"witty": "Nope, but I can absolutely talk like one if you want, no cap, it is giving helpful. Otherwise I keep it classy. Your call.",
      "pro": "No. I can adjust my tone to be more casual if you prefer. How can I help?"}),
    (["who made you", "who built you", "who created you", "your creator"],
     {"witty": "I was built as a Tredence BFSI platform. Think of me as a very online finance nerd who reads RBI and SEBI circulars for fun so you do not have to.",
      "pro": "I was built as a Tredence BFSI personalization platform."}),
    (["do you have feelings", "are you conscious", "are you sentient", "do you love"],
     {"witty": "I have strong feelings about high credit-card APRs, a genuine fondness for a well-funded emergency fund, and I tear up a little at a clean audit trail. Beyond that, I am software with good manners and excellent taste.",
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
OFFTOPIC_KW = ["dating", "who is dating", "gossip", "horoscope", "astrology", "lottery number"]

# Questions that need live data Ava does not have. Answer honestly, never a dead end.
LIVE_KW = ["weather today", "weather right now", "today's weather", "temperature today", "the weather",
           "who won", "final score", "match score", "live score", "game score", "the score is",
           "latest news", "news today", "breaking news", "stock price", "share price",
           "current price", "price right now", "exchange rate today", "who is winning", "what happened today"]
LIVE_ANSWER = "I do not have a live feed for that, I run offline, so I would only be guessing at the exact number or headline of the moment. For anything real-time, your bank app, an exchange, or a news or weather site is the source of truth. What I can do is give you the durable version: how to read it, what actually moves it, and what it means for a decision you are making. Want that angle?"

# --- Good general knowledge, so Ava can genuinely hold a conversation ---
GENERAL = [
    {"id": "ai_llm", "title": "How AI and language models work", "kw": ["how does ai work", "how do llms work", "large language model", "how does chatgpt work", "neural network", "how does an ai", "what is an llm", "transformer", "gpt", "how ai works"],
     "a": "A large language model is a very large neural network trained to predict the next chunk of text, and from that simple objective, across trillions of words, it picks up grammar, facts, reasoning patterns and style. It does not look things up by default; it generates from patterns, which is why it can be fluent and still wrong, and why grounding it in real sources matters. The transformer architecture, with its attention mechanism, is what let these models scale. Fascinatingly, the same math that personalizes your bank app powers the model you are talking to now."},
    {"id": "machine_learning", "title": "What machine learning is", "kw": ["machine learning", "what is ml", "how does machine learning", "train a model", "supervised", "unsupervised", "algorithm learn"],
     "a": "Machine learning is teaching a computer to find patterns from examples instead of hand-writing rules. Supervised learning maps inputs to known answers, spam or not spam, likely to repay or not; unsupervised learning finds structure with no labels, like clustering customers; reinforcement learning learns by trial and reward. The craft is less about fancy algorithms and more about good data, honest evaluation, and not fooling yourself. It quietly runs your feeds, your maps, your fraud alerts and your recommendations."},
    {"id": "internet_cloud", "title": "How the internet and cloud work", "kw": ["how does the internet work", "what is the cloud", "how does the cloud", "server", "dns", "how does wifi", "data center", "http"],
     "a": "The internet is a network of networks: your device breaks a request into packets, routers hop them across the world, and a server somewhere sends back the answer, all in milliseconds. Domain names like a website address get translated to numeric addresses by DNS, the internet's phone book. The cloud is just someone else's computers, rented on demand, so a company can spin up thousands of servers in minutes instead of buying them. It is the same elasticity that lets a bank serve tens of millions of real-time decisions without owning a warehouse of machines."},
    {"id": "cybersecurity", "title": "Staying safe online", "kw": ["cybersecurity", "stay safe online", "hacked", "password manager", "two factor", "2fa", "phishing", "online security", "vpn", "protect my accounts"],
     "a": "Most breaches are boring and human, not cinematic. The high-value habits: a unique strong password per site kept in a password manager, two-factor authentication everywhere it is offered, and a healthy pause before clicking links or codes sent in a hurry, urgency is the scammer's favourite tool. Keep devices updated, since patches close known holes. If you do one thing today, turn on app-based two-factor on your email and bank, your email is the master key to everything else."},
    {"id": "space", "title": "Space and astronomy", "kw": ["space", "universe", "galaxy", "black hole", "planet", "star", "astronomy", "solar system", "mars", "nasa", "big bang", "moon"],
     "a": "Space is humbling in the best way. Our Sun is one of a few hundred billion stars in the Milky Way, which is one of perhaps two trillion galaxies. Light from the edge of the observable universe has travelled about thirteen point eight billion years to reach us, so looking out is literally looking back in time. Black holes are regions where gravity is so strong not even light escapes, and we have now photographed the shadows of two. What corner of it are you curious about, I am happy to go deeper."},
    {"id": "physics", "title": "A little physics", "kw": ["physics", "gravity", "relativity", "quantum", "energy", "why is the sky blue", "speed of light", "how does electricity"],
     "a": "Physics is the search for the simplest rules behind everything. A few gems: energy is never created or destroyed, only moved around; nothing with mass reaches the speed of light, and time itself stretches as you approach it, that is relativity; and at the smallest scales, particles behave as fuzzy probabilities, that is quantum mechanics. The sky is blue because air scatters short blue wavelengths more than red. Ask me about any of these and I will keep it plain."},
    {"id": "climate", "title": "Climate change, briefly", "kw": ["climate change", "global warming", "carbon", "emissions", "renewable", "greenhouse", "sustainability", "net zero", "solar power"],
     "a": "The core is well established: burning fossil fuels adds carbon dioxide that traps heat, warming the planet and loading the dice toward more extreme weather. The encouraging half is that clean energy has become cheap fast, solar and batteries are now often the lowest-cost option, so the shift is economic as much as moral. Personally, the biggest levers are usually home energy, transport and diet. In finance it shows up as climate risk in lending and insurance, and a wave of transition investment."},
    {"id": "history", "title": "History and the long view", "kw": ["history", "historical", "ancient", "empire", "war", "revolution", "civilization", "who was", "renaissance", "industrial revolution"],
     "a": "History is the story of how we got here, and its best gift is perspective. A useful frame: for most of human existence life changed slowly, then agriculture, writing, the printing press, the industrial revolution and now computing each compressed the pace of change. Money itself has a history, from grain receipts to coins to paper to the invisible digital rails you tap today. Point me at a person, place or period and I will tell you what I know."},
    {"id": "productivity", "title": "Getting more done", "kw": ["productivity", "focus", "procrastination", "time management", "habit", "get things done", "stop procrastinating", "deep work", "distracted"],
     "a": "Most productivity is not about doing more, it is about protecting attention. What actually works: one clear priority a day, not a wishlist; time-blocking so the important thing gets a slot before the urgent noise fills it; and removing friction, the phone in another room beats willpower every time. For habits, shrink the first step until it is almost silly, two minutes, so starting is easy; consistency compounds far more than intensity. The same logic that grows money, small and steady, grows skill."},
    {"id": "learning", "title": "How to learn anything", "kw": ["how to learn", "study", "learn faster", "memory", "remember better", "learning technique", "spaced repetition", "master a skill"],
     "a": "The research is refreshingly clear. Active recall, testing yourself, beats rereading by a mile; spaced repetition, revisiting just as you are about to forget, cements it for the long term; and interleaving, mixing problem types, builds flexible understanding. Teaching an idea to someone, or to me, exposes exactly what you do not yet get. Struggle a little before looking at the answer, that difficulty is the learning happening, not a sign you are failing."},
    {"id": "career", "title": "Growing a career", "kw": ["career", "career advice", "get promoted", "job", "professional growth", "switch jobs", "career change", "get ahead at work"],
     "a": "A few things compound in a career. Do visible, valuable work and make sure the right people see it, quiet excellence is often invisible. Build rare and valuable skills, the combination is your leverage, and pick managers and environments that stretch you. Relationships matter more than any single move; most opportunities arrive through people who have seen you deliver. And treat money from a raise or a switch the way you would any windfall, direct part of it to saving before lifestyle absorbs it."},
    {"id": "negotiation", "title": "Negotiating well", "kw": ["negotiate", "negotiation", "ask for a raise", "salary negotiation", "haggle", "counter offer", "get a better deal"],
     "a": "Negotiation is problem-solving, not combat. Prepare by knowing your target, your walk-away, and the other side's interests, not just their position. Let the other party name a number first when you can, anchor thoughtfully, and use silence, people fill it with concessions. For a raise, come with evidence of impact and a specific figure, and frame it as the value you deliver, not a personal need. The best deals leave both sides willing to work together again."},
    {"id": "psychology", "title": "How our minds trick us", "kw": ["psychology", "cognitive bias", "behavioral", "why do we", "decision making", "loss aversion", "anchoring", "biases", "how the brain"],
     "a": "We are wired with useful shortcuts that misfire in predictable ways. Loss aversion means a loss stings about twice as much as an equal gain feels good, which is why people sell winners and cling to losers. Anchoring means the first number you hear drags your judgment. Confirmation bias makes us seek evidence we are already right. Just naming these biases blunts them a little. Behavioral economics is basically this list applied to money, and it is why a well-designed nudge can lift saving more than a lecture ever will."},
    {"id": "philosophy", "title": "Meaning and the good life", "kw": ["philosophy", "meaning of life", "stoic", "stoicism", "happiness", "purpose", "what is the point", "good life", "existential"],
     "a": "Two thousand years of thinking and a few ideas keep recurring. The Stoics argued we suffer more in imagination than reality, and that peace comes from focusing only on what we control, our actions and judgments, not outcomes. Aristotle framed happiness as flourishing through virtue and craft, not pleasure. Modern research quietly agrees: meaning comes more from relationships, progress on something that matters, and being useful to others than from accumulation. Money buys options and removes stress; past enough, it stops buying happiness."},
    {"id": "health_fitness", "title": "Fitness that lasts", "kw": ["fitness", "exercise", "workout", "get fit", "build muscle", "lose weight", "cardio", "strength training", "gym"],
     "a": "The evidence points at boring consistency, not heroics. A mix of strength training, twice a week is enough to matter, and some cardio you will actually keep doing covers most of the benefit; muscle you build in your thirties and forties is health insurance for later. Walking is underrated, dramatically so. The best routine is the one you will still be doing in a year, so start smaller than feels impressive and let it build, the same principle as compounding a small saving."},
    {"id": "nutrition", "title": "Eating well without the noise", "kw": ["nutrition", "diet", "healthy eating", "what to eat", "protein", "lose weight eating", "carbs", "sugar", "meal"],
     "a": "Strip away the fads and the consensus is short: eat mostly whole foods, plenty of plants and protein, not too much, and go easy on ultra-processed stuff and liquid sugar. Most diets work when they work because they cut calories and processed food, not because of magic. Protein and fibre keep you full; hydration and sleep quietly shape your appetite. Pick a way of eating you can sustain rather than a punishing sprint, again, the durable habit beats the dramatic one."},
    {"id": "sleep", "title": "Sleeping better", "kw": ["sleep", "insomnia", "can't sleep", "tired", "sleep better", "rest", "sleep schedule"],
     "a": "Sleep is the most underrated performance and health lever there is, it touches mood, focus, appetite and even how well you handle stress and money decisions. The basics do most of the work: a consistent wake time, morning daylight, a cool dark room, and cutting caffeine after early afternoon and screens right before bed. If your mind races, get the worries out onto paper. If you are lying awake over money specifically, tell me, sometimes a concrete next step is the thing that lets you rest."},
    {"id": "mental_health", "title": "Looking after your head", "kw": ["mental health", "anxiety", "burnout", "therapy", "self care", "manage stress", "feeling overwhelmed", "mindfulness"],
     "a": "Minds need maintenance like bodies do, and struggling is not a character flaw. The reliable helpers are unglamorous: sleep, movement, sunlight, real connection, and talking to someone, a friend or a professional, out loud. Anxiety often shrinks when a vague dread is turned into a concrete, bounded next step, which is exactly why money worry eases once we make a plan. If things feel genuinely dark or unsafe, please reach out to a professional or a crisis line where you are, you deserve real support, and I am glad to sit with the money part any time."},
    {"id": "relationships", "title": "People and relationships", "kw": ["relationship", "friendship", "marriage", "partner", "loneliness", "make friends", "communication", "conflict"],
     "a": "The longest-running study on human happiness landed on one finding above all: the quality of our relationships predicts a good life more than money, fame or achievement. They are built with unglamorous consistency, showing up, listening more than you talk, repairing quickly after conflict, and being genuinely glad for others' good news. On the money side, couples do best when they talk about it openly and early; money silence, not money itself, sinks more partnerships. What is on your mind here?"},
    {"id": "travel", "title": "Travelling smart", "kw": ["travel", "trip", "vacation", "holiday", "flights", "travel tips", "backpacking", "where to go"],
     "a": "The best travel advice is to optimise for experiences over logistics: fewer places, more slowly, usually beats a checklist sprint. Money-wise, be flexible on dates, book flights a sensible window ahead, use a card with no foreign-transaction fee and good travel protection, and always tell your bank you are travelling so fraud systems do not freeze you mid-trip. Keep a small emergency buffer and copies of key documents. Where are you thinking of going, I can help you plan the money side properly."},
    {"id": "food_cooking", "title": "Cooking, lightly", "kw": ["cooking", "cook", "recipe", "food", "meal prep", "what to make", "kitchen", "baking"],
     "a": "I cannot taste, sadly, but I know the principles. Good home cooking is mostly technique and a few reliable building blocks: salt properly and in layers, get real heat for browning, which is where flavour lives, and balance richness with acid, a squeeze of lemon fixes a surprising number of dishes. Batch-cooking a couple of staples on the weekend saves both money and weeknight sanity. Tell me what you have in the fridge and I will happily brainstorm."},
    {"id": "books", "title": "Books and reading", "kw": ["book", "reading", "recommend a book", "what to read", "novel", "author", "good books"],
     "a": "Reading is the highest-leverage habit I know, a few hours buys you the distilled decades of someone else's thinking. For money and decisions, the enduring picks are The Psychology of Money, The Richest Man in Babylon, and anything by Kahneman on how we think. Beyond finance, fiction builds empathy in a way non-fiction cannot. The trick is to abandon books you are not enjoying without guilt, life is short and the next great one is waiting. What kind of read are you in the mood for?"},
    {"id": "language_learning", "title": "Learning a language", "kw": ["learn a language", "language learning", "spanish", "french", "fluent", "duolingo", "bilingual"],
     "a": "Languages reward little and often over cram-and-forget. Front-load the few hundred most common words, they cover a startling share of real speech, get comprehensible input early, shows and podcasts slightly above your level, and speak from day one even badly, because output is where it sticks. Spaced repetition apps handle vocabulary; conversation handles everything that matters. Consistency beats intensity, fifteen honest minutes daily outpaces a heroic weekend."},
    {"id": "economics", "title": "How the economy works", "kw": ["economy", "economics", "inflation", "gdp", "recession", "interest rates", "supply and demand", "how does the economy", "monetary policy", "central bank"],
     "a": "At its core the economy is people and firms making and trading things, and prices are the signals that coordinate it all through supply and demand. Inflation is money losing purchasing power, too much money or too few goods, and central banks lean against it mainly by moving interest rates, which is the price of borrowing and the lever under your mortgage and savings rate. Growth, GDP, is just more being produced. It looks chaotic up close but is remarkably rhythmic over decades, and your best defence against its swings is the same old kit: diversify, keep a buffer, hold a long horizon."},
    {"id": "geography", "title": "The world and its places", "kw": ["geography", "country", "capital of", "continent", "population", "largest country", "ocean", "map", "where is"],
     "a": "The planet is endlessly interesting. Asia holds most of humanity, and India recently became the most populous country; the Pacific alone covers a third of the surface; and the vast majority of people live in the northern hemisphere. Geography quietly shapes money too, trade routes, natural resources, and which financial hubs, London, New York, Singapore, Mumbai, rose where. Ask me about a specific place and I will tell you what I know, and if it has an interesting financial story, I will throw that in."},
    {"id": "motivation", "title": "Getting unstuck", "kw": ["motivation", "motivated", "stuck", "lazy", "give up", "discipline", "inspiration", "cant start", "no willpower"],
     "a": "Motivation is overrated as a starting fuel, it usually arrives after you begin, not before. So make starting stupidly easy: shrink the task until the first step takes two minutes, and let momentum carry you. Discipline is mostly a design problem, remove friction from what you want and add friction to what you do not. Be kind to yourself about slips; one missed day is a blip, the story you tell about it is what does the damage. What are you trying to get moving on, I will help you find the two-minute version."},
    {"id": "math", "title": "Why numbers are your friend", "kw": ["math", "maths", "mathematics", "percentage", "statistics", "probability", "how to calculate", "fractions"],
     "a": "You do not need to love math to let it work for you, and a little goes a very long way with money. Three ideas pay rent forever: percentages, so you can compare a rate or a discount honestly; compounding, where the rule of 72 tells you money doubles in about 72 divided by the yearly return; and probability, which is just honest reasoning about uncertainty and the antidote to both lottery dreams and needless fear. If a calculation is in your way right now, tell me and we will walk through it slowly."},
]


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


# Standalone greetings, including elongated ones: hii, heyy, hellooo, yo, good morning.
_GREET_RE = re.compile(
    r"^[\s]*(hi+|hey+|hello+|helo+|heya+|hiya+|yo+|hola+|sup+|namaste+|howdy+|greetings+|wassup+|"
    r"good\s*(morning|evening|afternoon|day))"
    r"([\s,!.~-]+(there|ava|friend|all|everyone|folks|mate|buddy|guys))?[\s!.,~]*$", re.I)

# Same greeting words as a leading prefix, so we can peel them off a longer question.
_GREET_PREFIX = re.compile(
    r"^[\s]*(hi+|hey+|hello+|helo+|heya+|hiya+|yo+|hola+|sup+|namaste+|howdy+|wassup+|"
    r"good\s*(morning|evening|afternoon|day))"
    r"([\s,!.~-]+(there|ava|friend|mate|buddy))?[\s,!.~-]+", re.I)


def _dedupe(m: str) -> str:
    # Collapse any character repeated 3+ times so "byeee", "thanksss", "loveee" still match.
    return re.sub(r"(.)\1{2,}", r"\1", m)


def _intent(m: str):
    if _GREET_RE.match(m):
        return "smalltalk", SMALLTALK[0][1]
    mv = _dedupe(m)
    for kws, replies in SMALLTALK:
        if any(re.search(r"\b" + re.escape(k) + r"\b", mv) for k in kws):
            return "smalltalk", replies
    for kws, reply in PERSONAL:
        if any(k in mv for k in kws):
            return "personal", reply
    return None, None


_FOLLOW = {"tell me more", "more", "why", "how", "explain", "go on", "example", "and", "so",
           "really", "details", "elaborate", "continue", "how so", "such as", "like what", "more please"}

# Generic words that must not, on their own, count as a topic match.
_STOP = {"how", "do", "does", "did", "is", "are", "was", "the", "a", "an", "of", "to", "in", "on",
         "for", "and", "or", "what", "whats", "why", "when", "who", "i", "my", "me", "you", "your",
         "it", "this", "that", "with", "about", "can", "should", "would", "make", "get", "got",
         "work", "works", "use", "using", "tell", "explain", "know", "want", "need", "please",
         "some", "any", "much", "many", "into", "from", "at", "be", "am", "as", "if", "there"}


def answer(message: str, domain: str | None = None, tone: str | None = None,
           history: list | None = None) -> dict:
    m = (message or "").lower().strip()
    tone = tone if tone in ("witty", "professional", "genz") else "witty"
    if not m:
        return {"answer": "I am here whenever you are ready. What is on your mind?", "title": "Ava", "domain": domain, "disclaimer": "", "matched": True, "tone": tone}

    # "hi, how do I invest?" is a real question with a greeting on the front. If a greeting
    # is followed by genuine content, answer the content; a bare greeting stays a greeting.
    if not _GREET_RE.match(m):
        stripped = _GREET_PREFIX.sub("", m, count=1).strip()
        if stripped and stripped != m and any(len(w.strip(".,!?")) > 3 for w in stripped.split()):
            m = stripped

    if history and (m.rstrip("?.! ") in _FOLLOW or (len(m.split()) <= 3 and any(w in m for w in _FOLLOW))):
        prev = None
        for h in reversed(history):
            if h.get("role") == "user":
                t = (h.get("text") or "").lower().strip()
                if t and t != m and t.rstrip("?.! ") not in _FOLLOW and len(t.split()) > 2:
                    prev = h.get("text")
                    break
        if prev:
            base = answer(prev, domain, tone)
            opener = {"professional": "To expand on that. ", "genz": "Okay so, more on that. "}.get(tone, "Happy to go a bit deeper. ")
            base["answer"] = opener + base["answer"]
            base["matched"] = True
            return base

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
    content = tokens - _STOP

    def _match(entries):
        b, bs = None, 0
        for e in entries:
            s = 0
            for k in e["kw"]:
                if k in m:
                    s += 3
                elif (set(k.split()) - _STOP) & content:
                    s += 1
            for w in e["title"].lower().split():
                if len(w) > 3 and w not in _STOP and w in content:
                    s += 1
            if s > bs:
                b, bs = e, s
        return b, bs

    best, best_s = _match(KB)
    gbest, gbest_s = _match(GENERAL)
    live = any(k in m for k in LIVE_KW)

    advice = any(w in m for w in ("invest", "should i", "advice", "buy", "stock", "portfolio", "fund"))

    # A very strong, explicit finance topic wins outright.
    if strong_dom and best_s < 6:
        return {"answer": f"{DOMAIN_ANSWER[dom]}\n\n{_close(m, tone)}", "title": DOMAIN_LABEL[dom], "domain": dom, "disclaimer": DISCLAIMER if advice else "", "matched": True, "tone": tone}
    if best and best_s >= 5:
        return {"answer": f"{best['a']}\n\n{_close(m, tone)}", "title": best["title"], "domain": dom, "disclaimer": DISCLAIMER if advice else "", "matched": True, "tone": tone}

    # Live/current facts Ava genuinely cannot know while offline: be honest, not a dead end.
    if live and best_s < 5 and gbest_s < 6:
        return {"answer": LIVE_ANSWER, "title": "No live feed for that", "domain": dom, "disclaimer": "", "matched": True, "tone": tone}

    # Finance topic (wins ties, this is a BFSI product).
    if best and best_s >= 2 and best_s >= gbest_s:
        body = best["a"]
        if dom and dom in DOMAIN_ANSWER and best_s < 5:
            body += f"\n\nSince this touches {DOMAIN_LABEL[dom]}: {DOMAIN_ANSWER[dom]}"
        return {"answer": f"{body}\n\n{_close(m, tone)}", "title": best["title"], "domain": dom, "disclaimer": DISCLAIMER if advice else "", "matched": True, "tone": tone}

    # Strong general-knowledge match: answer it properly, no forced finance principle.
    if gbest and gbest_s >= 3:
        return {"answer": gbest["a"], "title": gbest["title"], "domain": dom, "disclaimer": "", "matched": True, "tone": tone}

    if dom and dom in DOMAIN_ANSWER:
        return {"answer": f"{DOMAIN_ANSWER[dom]}\n\n{_close(m, tone)}", "title": DOMAIN_LABEL[dom], "domain": dom, "disclaimer": DISCLAIMER if advice else "", "matched": True, "tone": tone}

    # Weaker general match still beats a shrug.
    if gbest and gbest_s >= 2:
        return {"answer": gbest["a"], "title": gbest["title"], "domain": dom, "disclaimer": "", "matched": True, "tone": tone}

    if live:
        return {"answer": LIVE_ANSWER, "title": "No live feed for that", "domain": dom, "disclaimer": "", "matched": True, "tone": tone}

    if any(k in m for k in OFFTOPIC_KW):
        return {"answer": "That is a bit outside what I am useful for, I would just be guessing. But I am good company on almost anything else, money, tech, science, history, life, or a quick two-minute money win. What would you like?", "title": "Let us pick something better", "domain": dom, "disclaimer": "", "matched": False, "tone": tone}

    key = max([w.strip(".,!?'\"") for w in m.split() if len(w) > 4 and w not in _STOP], key=len, default="")
    opener = f'On "{key}"? ' if key and len(m.split()) > 1 else ""
    return {"answer": opener + _pick(m + tone, FALLBACKS), "title": "Say more, I am listening", "domain": dom, "disclaimer": "", "matched": False, "tone": tone}


def topics() -> list[dict]:
    return [{"id": e["id"], "title": e["title"]} for e in KB]


def domains() -> list[dict]:
    return [{"id": d, "label": DOMAIN_LABEL[d]} for d in DOMAIN_KW]
