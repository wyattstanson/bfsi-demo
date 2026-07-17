import statistics
from app import config

def _percentile(xs, p):
    xs = sorted(xs)
    k = max(0, min(len(xs) - 1, int(round(p / 100.0 * (len(xs) - 1)))))
    return xs[k]

def test_decide_p99_under_slo(client, party_id):
    body = {'party_id': party_id, 'channel': 'web', 'event': {'event_type': 'large_transfer_attempt', 'amount': 4000}}
    for _ in range(20):
        client.post('/decide', json=body)
    lat = []
    for _ in range(300):
        r = client.post('/decide', json=body)
        assert r.status_code == 200
        lat.append(r.json()['latency_ms'])
    p50, p95, p99 = (_percentile(lat, 50), _percentile(lat, 95), _percentile(lat, 99))
    print(f'\nwarm /decide latency  p50={p50:.2f}ms  p95={p95:.2f}ms  p99={p99:.2f}ms')
    assert p99 < config.LATENCY_SLO_MS, f'p99 {p99:.2f}ms exceeds {config.LATENCY_SLO_MS}ms'
