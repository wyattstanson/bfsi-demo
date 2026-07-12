"""Layer 3 — Models: a grounded (retrieval-augmented) LLM helper.

Retrieves over vector memory and returns text *with citations*.  If an
ANTHROPIC_API_KEY is present it calls a hosted Claude model; otherwise it uses a
deterministic offline stub so the demo always runs and tests are reproducible.

Embeddings here are a deterministic hashing embedding — good enough to exercise
the vector-retrieval path on one laptop.

# PROD: swap the stub for Bedrock / a hosted Claude endpoint, and the hashing
#       embedding for a real embedding model with pgvector similarity search.
"""
from __future__ import annotations

import hashlib
import math
import re

from app import config

EMB_DIM = 64


def embed(text: str) -> list[float]:
    """Deterministic bag-of-tokens hashing embedding (unit-normalized)."""
    vec = [0.0] * EMB_DIM
    for tok in re.findall(r"[a-z0-9]+", text.lower()):
        h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
        vec[h % EMB_DIM] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _stub_answer(query: str, docs: list[str]) -> str:
    if not docs:
        return "No grounded context available; escalate for a human answer."
    top = docs[0]
    return f"Based on retrieved policy: {top} (grounded, offline stub)."


def grounded_answer(query: str, docs: list[str]) -> dict:
    """Return an answer plus the citations it was grounded on.

    `docs` are already-retrieved snippets (retrieval happens in memory.py over
    pgvector). This keeps the model payload free of PII — only ids + snippets.
    """
    citations = [{"rank": i + 1, "snippet": d} for i, d in enumerate(docs[:3])]

    if config.ANTHROPIC_API_KEY:
        try:  # pragma: no cover - only when a key is configured
            import anthropic

            client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
            context = "\n".join(f"[{i+1}] {d}" for i, d in enumerate(docs[:3]))
            msg = client.messages.create(
                model=config.LLM_MODEL,
                max_tokens=300,
                messages=[
                    {
                        "role": "user",
                        "content": (
                            "Answer using ONLY the numbered context, and cite "
                            f"the numbers you use.\n\nContext:\n{context}\n\n"
                            f"Question: {query}"
                        ),
                    }
                ],
            )
            answer = msg.content[0].text
            return {"answer": answer, "citations": citations, "grounded": True}
        except Exception:
            pass  # fall through to the offline stub

    return {"answer": _stub_answer(query, docs), "citations": citations, "grounded": True}
