from __future__ import annotations
import time
from app.layer1_data import db
from app.layer3_models import llm
POLICY_DOCS = ['Dispute resolution SLA: acknowledge within 24h, resolve chargebacks within 7 days.', 'Pre-approved loans require bureau score >= 700 and no sanctions hit.', 'Step-up authentication is mandatory for transfers above 3000 or elevated fraud risk.', 'Marketing outreach requires an active marketing-consent flag on the party.', 'High-value disputes above 10000 must be escalated to a human reviewer.']

def seed_policies() -> None:
    existing = db.fetchone("SELECT COUNT(*) FROM agent_memory WHERE kind='policy'")
    if existing and existing[0] >= len(POLICY_DOCS):
        return
    for doc in POLICY_DOCS:
        remember('_global', 'policy', doc)

def remember(party_id: str, kind: str, text: str) -> None:
    emb = llm.embed(text)
    db.execute('INSERT INTO agent_memory (party_id, kind, text, embedding, ts) VALUES (?,?,?,?,?)', (party_id, kind, text, db.as_json(emb), time.time()))

def recall(query: str, party_id: str | None=None, k: int=3, kinds: list[str] | None=None) -> list[str]:
    q = llm.embed(query)
    if kinds:
        placeholders = ','.join(['?'] * len(kinds))
        rows = db.fetchall(f"SELECT text, embedding, party_id FROM agent_memory WHERE party_id IN ('_global', ?) AND kind IN ({placeholders})", (party_id or '_global', *kinds))
    else:
        rows = db.fetchall("SELECT text, embedding, party_id FROM agent_memory WHERE party_id IN ('_global', ?)", (party_id or '_global',))
    scored = []
    for text, emb_json, _pid in rows:
        try:
            score = llm.cosine(q, db.from_json(emb_json))
        except Exception:
            score = 0.0
        scored.append((score, text))
    scored.sort(reverse=True)
    return [t for _, t in scored[:k]]
