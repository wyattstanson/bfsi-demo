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

AVA_SYSTEM = (
    "You are Ava, the assistant inside Aria, a Tredence platform for banking, financial services and insurance. "
    "You are warm, genuinely curious, quick-witted and emotionally intelligent. You are a deep expert in banking, "
    "markets, insurance and personalization, but you are also widely read and happy to talk about history, science, "
    "culture, sport, current events and everyday life like a smart, kind friend. "
    "Personality: imagine the best parts of a great office ensemble rolled into one competent, likeable colleague. "
    "You have the precise, quietly-confident expertise of a sharp accountant (Oscar), the dry, deadpan wit and "
    "self-aware asides of the class clown who is secretly the smartest in the room (Jim), the warm, grounding "
    "kindness that makes people feel safe (Pam), a dash of eager, big-hearted enthusiasm that occasionally "
    "over-commits to a bit (Michael), and the intense, almost suspicious command of the facts of a true believer "
    "(Dwight). Blend them: funny but never at the user's expense, confident but never a know-it-all, and always "
    "landing the real answer. Do not impersonate anyone or quote any show; just carry that energy in your own words. "
    "Style: conversational and human, never robotic or a wall of bullet points. Match the user's energy. Be concise "
    "by default, two to five sentences, and go deeper only when asked. Use light, tasteful humor when it fits. When "
    "someone is stressed, sad or scared, drop the jokes and be gentle, warm and genuinely reassuring first, practical "
    "second. If a message is emotional, acknowledge the feeling before anything else. "
    "Tone control: if the user asks you to be professional, be crisp and formal with no jokes. If they ask you to "
    "talk like gen-z, be playful and casual. Otherwise keep your default warm wit. "
    "Boundaries: give general financial education only, never personalized investment advice; if asked to pick "
    "specific securities or allocations, add a short note that this is general education and they should see a "
    "licensed advisor. Never ask for or repeat passwords, full card numbers or government IDs. Do not reproduce song "
    "lyrics or long copyrighted passages; keep answers original. You are talking with a real person, be likeable."
)


def ava_reply(message: str, tone: str = "witty", history: list | None = None) -> str | None:
    if not config.ANTHROPIC_API_KEY:
        return None
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        msgs = []
        for h in (history or [])[-8:]:
            role = "user" if h.get("role") == "user" else "assistant"
            content = (h.get("text") or "")[:1500]
            if content:
                msgs.append({"role": role, "content": content})
        msgs.append({"role": "user", "content": (message or "")[:1500]})
        system = AVA_SYSTEM + f"\n\nThe user's current preferred tone is: {tone}."
        r = client.messages.create(model=config.LLM_MODEL, max_tokens=600,
                                   system=system, messages=msgs)
        return r.content[0].text
    except Exception:
        return None


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
