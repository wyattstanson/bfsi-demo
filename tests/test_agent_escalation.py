import json
from app.layer1_data import db

def _final_event(sse_text: str) -> dict:
    final = None
    for line in sse_text.splitlines():
        if line.startswith('data: '):
            ev = json.loads(line[6:])
            if ev.get('type') == 'final':
                final = ev
    assert final is not None, 'no final SSE event received'
    return final

def test_high_value_dispute_escalates(client, party_id):
    before = (db.fetchone('SELECT COUNT(*) FROM human_queue') or [0])[0]
    r = client.post('/agent', json={'party_id': party_id, 'goal': 'dispute an unauthorized charge of 15000'})
    final = _final_event(r.text)
    assert final['escalated'] is True
    assert final['confidence'] < 0.6
    after = (db.fetchone('SELECT COUNT(*) FROM human_queue') or [0])[0]
    assert after == before + 1, 'escalation must enqueue a human-review row'

def test_simple_info_goal_completes(client, party_id):
    r = client.post('/agent', json={'party_id': party_id, 'goal': 'give me a financial tip'})
    final = _final_event(r.text)
    assert final['escalated'] is False
    assert final['answer']
