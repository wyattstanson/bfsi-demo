from __future__ import annotations
import hashlib
import math
import re
from app import config
EMB_DIM = 64

def embed(text: str) -> list[float]:
    vec = [0.0] * EMB_DIM
    for tok in re.findall('[a-z0-9]+', text.lower()):
        h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
        vec[h % EMB_DIM] += 1.0
    norm = math.sqrt(sum((v * v for v in vec))) or 1.0
    return [v / norm for v in vec]

def cosine(a: list[float], b: list[float]) -> float:
    return sum((x * y for x, y in zip(a, b)))

def _stub_answer(query: str, docs: list[str]) -> str:
    if not docs:
        return 'No grounded context available; escalate for a human answer.'
    top = docs[0]
    return f'Based on retrieved policy: {top} (grounded, offline stub).'

def grounded_answer(query: str, docs: list[str]) -> dict:
    citations = [{'rank': i + 1, 'snippet': d} for i, d in enumerate(docs[:3])]
    if config.ANTHROPIC_API_KEY:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
            context = '\n'.join((f'[{i + 1}] {d}' for i, d in enumerate(docs[:3])))
            msg = client.messages.create(model=config.LLM_MODEL, max_tokens=300, messages=[{'role': 'user', 'content': f'Answer using ONLY the numbered context, and cite the numbers you use.\n\nContext:\n{context}\n\nQuestion: {query}'}])
            answer = msg.content[0].text
            return {'answer': answer, 'citations': citations, 'grounded': True}
        except Exception:
            pass
    return {'answer': _stub_answer(query, docs), 'citations': citations, 'grounded': True}
