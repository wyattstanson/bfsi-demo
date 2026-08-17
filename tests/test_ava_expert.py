"""Ava's grounded expert brain: corpus integrity, retrieval quality, and the
guarantee that she never hard-blocks or loses her human warmth."""

from app.agent import bfsi_kb, expert
from app.agent.knowledge import answer


def test_corpus_loaded():
    assert len(bfsi_kb.GLOSSARY) >= 150
    assert len(bfsi_kb.FACTS) >= 35
    assert len(bfsi_kb.USE_CASES) >= 25
    # every glossary entry is usable: has a definition and at least one alias
    for g in bfsi_kb.GLOSSARY:
        assert g["definition"] and g["aliases"]


def test_technical_questions_are_grounded():
    grounded_terms = [
        "what is SHAP?", "explain uplift modeling", "what is GraphSAGE?",
        "what is a feature store?", "what is the EU AI Act?", "what is SR 11-7?",
        "what is BofA Erica?", "what is direct indexing?", "what is a contextual bandit?",
    ]
    for q in grounded_terms:
        r = answer(q)
        assert r["matched"], q
        assert r.get("grounded"), f"expected a grounded expert answer for: {q}"


def test_flagship_answers_carry_the_real_numbers():
    # Ava must quote the paper's benchmark, not vibe it.
    assert "0.817" in answer("why demographics-free?")["answer"]
    assert "1.35x" in answer("uplift vs propensity")["answer"]
    assert "0.996" in answer("what is the disparate impact result?")["answer"]
    assert "35.5" in answer("what is the latency budget?")["answer"]
    assert "sixteen" in answer("what is the audit log?")["answer"].lower()


def test_five_layers_and_eight_patterns_list():
    five = answer("what are the five layers?")["answer"].lower()
    for layer in ("data foundation", "feature store", "decisioning", "governance"):
        assert layer in five
    patterns = answer("what are the eight patterns?")["answer"].lower()
    for p in ("uplift", "graph", "bandit", "agentic"):
        assert p in patterns


def test_conversation_and_emotion_are_not_hijacked():
    # The expert brain must never steal warm, human moments.
    assert answer("what is the meaning of life?")["title"] == "Meaning and the good life"
    assert answer("I just lost my job and I am scared")["title"] == "A steadier footing"
    assert not answer("hi")["answer"].startswith("**")
    assert answer("how do I budget?")["title"] == "Budgeting that sticks"


def test_ava_never_hard_blocks():
    # Any input returns a non-empty answer; even gibberish gets a graceful reply.
    for q in ["", "asdkjfh qweoiu", "!!!", "tell me about black holes", "what is xgboost"]:
        r = answer(q)
        assert isinstance(r["answer"], str) and r["answer"].strip()


def test_tone_variants_stay_accurate():
    for tone in ("witty", "professional", "genz"):
        r = answer("what is SHAP?", tone=tone)
        assert r["matched"] and "Shapley".lower() in r["answer"].lower()


def test_retrieve_below_threshold_returns_none():
    # A purely conversational message should not trip the expert retriever.
    assert expert.retrieve("hey how are you doing today") is None
