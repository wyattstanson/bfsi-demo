from app.layer5_governance import audit

def test_one_audit_row_per_decision(client, party_id):
    before = client.get('/governance').json()['audit_rows']
    r = client.post('/decide', json={'party_id': party_id, 'channel': 'app', 'event': {'event_type': 'session_start'}})
    assert r.status_code == 200
    d = r.json()
    after = client.get('/governance').json()['audit_rows']
    assert after == before + 1, 'each decision must write exactly one audit row'
    row = client.get(f"/audit/{d['decision_id']}").json()
    assert set(row.keys()) == set(audit.FIELDS)
    assert len(audit.FIELDS) == 16
    assert row['action_id'] == d['action']
    assert row['decision_id'] == d['decision_id']
    assert row['fairness_flag'] == d['fairness_flag']
    assert row['features_snapshot'] and row['model_versions']
