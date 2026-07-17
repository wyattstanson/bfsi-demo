from app.agent import agent, tools
from app.layer1_data import db
from app.layer3_models import llm

def test_guardrail_rejects_pii():
    tools.assert_no_pii({'party_id': 'P1', 'profile': {'risk_band': 'low'}})
    for bad in ({'name': 'Jane Doe'}, {'nested': [{'ssn': 'x'}]}, {'email': 'a@b.c'}):
        try:
            tools.assert_no_pii(bad)
            assert False, f'should have rejected {bad}'
        except ValueError:
            pass

def test_profile_tool_returns_no_pii(party_id):
    profile = tools.call('get_customer_profile', party_id=party_id)
    assert set(profile) & {'name', 'email', 'ssn'} == set()
    assert profile['party_id'] == party_id

def test_llm_payload_contains_no_pii(client, party_id, monkeypatch):
    name, email, ssn = db.fetchone('SELECT name, email, ssn FROM party WHERE party_id = ?', (party_id,))
    captured = {}

    def spy(query, docs):
        captured['query'] = query
        captured['docs'] = docs
        return {'answer': 'ok', 'citations': [{'rank': 1, 'snippet': docs[0] if docs else ''}], 'grounded': True}
    monkeypatch.setattr(llm, 'grounded_answer', spy)
    agent.run(party_id, 'give me a financial tip')
    blob = (captured.get('query', '') + ' ' + ' '.join(captured.get('docs', []))).lower()
    for pii in (name, email, ssn):
        assert pii.lower() not in blob, f"PII '{pii}' leaked into the model payload"
