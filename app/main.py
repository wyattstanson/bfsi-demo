from __future__ import annotations
import hashlib
import hmac
import json
import random
import re
import threading
import time
from collections import deque
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, field_validator
from app import bootstrap, config
from app.agent import agent
from app.layer1_data import cdc_stub, db
from app.layer2_features import feature_store
from app.layer4_decisioning.decisioning import get_engine
from app.layer5_governance import audit, fairness, governance
_STATIC = Path(__file__).parent / 'static'
_events: deque = deque(maxlen=60)
_recent: deque = deque(maxlen=40)
_stop = threading.Event()
_party_ids: list[str] = []

def _stream_loop():
    while not _stop.is_set():
        if _party_ids:
            ev = cdc_stub.make_event(random.choice(_party_ids))
            ev['ts_label'] = time.strftime('%H:%M:%S')
            _events.appendleft(ev)
        time.sleep(0.7)

@asynccontextmanager
async def lifespan(app: FastAPI):
    bootstrap.ensure()
    get_engine()
    global _party_ids
    _party_ids = [r[0] for r in db.fetchall('SELECT party_id FROM party LIMIT 800')]
    t = threading.Thread(target=_stream_loop, daemon=True)
    t.start()
    yield
    _stop.set()
app = FastAPI(title='BFSI personalization platform', lifespan=lifespan)

_CSP = ("default-src 'self'; script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; "
        "base-uri 'none'; frame-ancestors 'none'; object-src 'none'; form-action 'self'")


@app.middleware('http')
async def security_headers(request: Request, call_next):
    resp = await call_next(request)
    resp.headers['Content-Security-Policy'] = _CSP
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    resp.headers['X-Frame-Options'] = 'DENY'
    resp.headers['Referrer-Policy'] = 'no-referrer'
    resp.headers['Permissions-Policy'] = 'geolocation=(), camera=(), microphone=(self)'
    return resp


_ID_RE = re.compile(r'^[A-Za-z0-9_-]{1,40}$')


class DecideRequest(BaseModel):
    party_id: str
    event: dict | None = None
    channel: str = 'app'

    @field_validator('party_id')
    @classmethod
    def _pid(cls, v):
        if not _ID_RE.match(v):
            raise ValueError('invalid party_id')
        return v


class AgentRequest(BaseModel):
    party_id: str
    goal: str

    @field_validator('party_id')
    @classmethod
    def _pid(cls, v):
        if not _ID_RE.match(v):
            raise ValueError('invalid party_id')
        return v

    @field_validator('goal')
    @classmethod
    def _goal(cls, v):
        return v[:280]

class DevAuth(BaseModel):
    passcode: str

@app.get('/')
def index():
    return FileResponse(_STATIC / 'index.html')

@app.get('/meta')
def meta():
    return {'domains': config.DOMAINS, 'domain_labels': config.DOMAIN_LABELS, 'regions': config.REGIONS, 'currency_symbol': config.CURRENCY_SYMBOL, 'journey_stages': config.JOURNEY_STAGES, 'slo_ms': config.LATENCY_SLO_MS, 'references': {'erica_ms': 44, 'aladdin_aum': '$23T', 'lemonade_claim_s': 3, 'bajaj_agents': '800+', 'flow_steps': 10}}

@app.post('/dev-auth')
def dev_auth(req: DevAuth):
    ok = hmac.compare_digest(req.passcode.encode(), config.DEV_PASSCODE.encode())
    return {'ok': ok}

@app.post('/decide')
def decide(req: DecideRequest):
    engine = get_engine()
    t0 = time.perf_counter()
    decision = engine.decide(req.party_id, req.event)
    assessment = governance.assess(engine, decision)
    latency_ms = (time.perf_counter() - t0) * 1000.0
    record = governance.build_record(decision, assessment, req.channel, latency_ms)
    audit.write(record)
    winner = decision['winner']
    attrs = decision['attrs']
    _recent.appendleft({'party_id': req.party_id, 'action': winner['action_id'], 'ev': winner['expected_value'], 'latency_ms': round(latency_ms, 2), 'fairness': record['fairness_flag'], 'region': attrs.get('region', ''), 'ts_label': time.strftime('%H:%M:%S')})
    return {'decision_id': record['decision_id'], 'action': winner['action_id'], 'action_detail': winner['action'], 'score': winner['expected_value'], 'reason_codes': record['reason_codes'], 'fairness_flag': record['fairness_flag'], 'latency_ms': round(latency_ms, 3), 'slo_ms': config.LATENCY_SLO_MS, 'within_slo': latency_ms < config.LATENCY_SLO_MS, 'model_scores': {k: round(v, 4) for k, v in decision['model_scores'].items()}, 'model_versions': decision['model_versions'], 'attrs': {k: attrs.get(k) for k in ('domain', 'journey_stage', 'region', 'currency', 'risk_band')}, 'ranked': [{'action_id': r['action_id'], 'expected_value': r['expected_value'], 'signal': r['signal'], 'signal_value': r['signal_value']} for r in decision['ranked']], 'rejected': decision['rejected']}

@app.post('/agent')
def run_agent(req: AgentRequest):

    def gen():
        for ev in agent.run_stream(req.party_id, req.goal):
            yield f'data: {json.dumps(ev)}\n\n'
    return StreamingResponse(gen(), media_type='text/event-stream')

_SEGMENTS = {
    'retail': ['Priority Banking', 'Everyday Checking', 'Salary Account', 'Youth Saver'],
    'corporate': ['Treasury Client', 'Trade Finance', 'Cash Management', 'Payroll Client'],
    'wealth': ['Private Wealth', 'HNW Portfolio', 'Managed Advisory', 'Goals Portfolio'],
    'asset_mgmt': ['Direct Indexing SMA', 'Model Portfolio', 'Index Mandate', 'ESG Sleeve'],
    'payments': ['Platinum Card', 'Rewards Card', 'Business Card', 'Travel Card'],
    'capital_markets': ['Institutional Desk', 'Prime Brokerage', 'Research Access', 'Execution Client'],
    'nbfc': ['Consumer Loan', 'EMI Card', 'Two-Wheeler Loan', 'Gold Loan'],
    'personal_ins': ['Term Life', 'Health Cover', 'Motor Policy', 'Wellness Plan'],
    'general_ins': ['Home Cover', 'Travel Policy', 'Motor Fleet', 'Pet Cover'],
    'commercial_ins': ['Cyber Policy', 'Property Cover', 'Liability Policy', 'Marine Cargo'],
}


def _display(pid: str, domain: str, region: str) -> str:
    h = int(hashlib.md5(pid.encode()).hexdigest(), 16)
    segs = _SEGMENTS.get(domain, ['Client'])
    seg = segs[h % len(segs)]
    return f"{seg} · {region} · ••{h % 10000:04d}"


@app.get('/personas')
def personas(limit: int=12, domain: str='', region: str=''):
    where, params = ([], [])
    if domain:
        where.append('domain = ?')
        params.append(domain)
    if region:
        where.append('region = ?')
        params.append(region)
    clause = ' WHERE ' + ' AND '.join(where) if where else ''
    params.append(limit)
    rows = db.fetchall(f'SELECT party_id, domain, journey_stage, region, currency, risk_band, tenure_months FROM party{clause} LIMIT ?', tuple(params))
    return [{'party_id': p, 'domain': d, 'domain_label': config.DOMAIN_LABELS.get(d, d), 'display': _display(p, d, rg), 'journey_stage': s, 'region': rg, 'currency': cur, 'risk_band': rb, 'tenure_months': tn} for p, d, s, rg, cur, rb, tn in rows]

@app.get('/party/{party_id}')
def party_snapshot(party_id: str):
    attrs = feature_store.get_online_attrs(party_id)
    feats = feature_store.get_online_features(party_id)
    if not attrs:
        return {'error': 'not found'}
    attrs['domain_label'] = config.DOMAIN_LABELS.get(attrs.get('domain', ''), attrs.get('domain', ''))
    return {'party_id': party_id, 'attrs': attrs, 'features': feats}

@app.get('/audit/{decision_id}')
def get_audit(decision_id: str):
    return audit.get(decision_id) or {'error': 'not found'}

@app.get('/governance')
def governance_snapshot():
    fair = fairness.snapshot()
    rates = [g['rate'] for g in fair.values() if g['total'] >= 20]
    air = round(min(rates) / max(rates), 3) if len(rates) >= 2 and max(rates) > 0 else None
    return {'drift': governance.drift_snapshot(), 'fairness': fair, 'air': air,
            'audit_rows': audit.count(),
            'human_queue': (db.fetchone('SELECT COUNT(*) FROM human_queue') or [0])[0]}


_CLOUD = [
    {'layer': 'L1 Data', 'aws': 'Kinesis, MSK', 'databricks': 'Delta Lake', 'snowflake': 'Warehouse'},
    {'layer': 'L2 Features', 'aws': 'ElastiCache, DynamoDB', 'databricks': 'Feature Store', 'snowflake': 'Feature Views'},
    {'layer': 'L3 Models', 'aws': 'SageMaker', 'databricks': 'Model Serving', 'snowflake': 'Snowpark ML'},
    {'layer': 'L4 Decisioning', 'aws': 'EKS, Lambda', 'databricks': 'Jobs', 'snowflake': 'Streamlit in SF'},
    {'layer': 'L5 Governance', 'aws': 'CloudTrail', 'databricks': 'Unity Catalog', 'snowflake': 'Access History'},
]


@app.get('/topology')
def topology():
    return {'providers': ['AWS', 'Databricks', 'Snowflake'], 'mapping': _CLOUD,
            'streaming': 'Kafka / MSK + Flink', 'orchestration': 'LangGraph on EKS',
            'capacity': 'stateless decisioning, horizontally autoscaled'}


@app.get('/db')
def db_view():
    def cnt(t):
        return (db.fetchone(f'SELECT COUNT(*) FROM {t}') or [0])[0]
    recent = db.fetchall(
        'SELECT decision_id, action_id, channel, latency_ms, fairness_flag, ts '
        'FROM audit_log ORDER BY ts DESC LIMIT 12')
    return {
        'tables': [
            {'name': 'party', 'rows': cnt('party')},
            {'name': 'txn', 'rows': cnt('txn')},
            {'name': 'feature_offline', 'rows': cnt('feature_offline')},
            {'name': 'audit_log', 'rows': cnt('audit_log')},
            {'name': 'agent_memory', 'rows': cnt('agent_memory')},
            {'name': 'human_queue', 'rows': cnt('human_queue')},
        ],
        'audit_tail': [
            {'decision_id': d[:14], 'action_id': a, 'channel': ch,
             'latency_ms': round(lm, 2), 'fairness_flag': ff,
             'ts_label': time.strftime('%H:%M:%S', time.localtime(ts))}
            for d, a, ch, lm, ff, ts in recent
        ],
    }

@app.get('/stats')
def stats():
    lat = [r[0] for r in db.fetchall('SELECT latency_ms FROM audit_log ORDER BY ts DESC LIMIT 2000')]
    lat_sorted = sorted(lat)

    def pct(p):
        if not lat_sorted:
            return 0.0
        k = max(0, min(len(lat_sorted) - 1, int(round(p / 100 * (len(lat_sorted) - 1)))))
        return round(lat_sorted[k], 2)
    by_action = db.fetchall('SELECT action_id, COUNT(*) FROM audit_log GROUP BY action_id ORDER BY 2 DESC')
    by_use = db.fetchall('SELECT use_case, COUNT(*) FROM audit_log GROUP BY use_case ORDER BY 2 DESC')
    by_region = db.fetchall('SELECT p.region, COUNT(*) FROM audit_log a JOIN party p ON a.party_id = p.party_id GROUP BY p.region ORDER BY 2 DESC')
    ev = db.fetchone('SELECT COALESCE(SUM(score),0), COALESCE(AVG(score),0) FROM audit_log')
    return {'decisions': audit.count(), 'parties': (db.fetchone('SELECT COUNT(*) FROM party') or [0])[0], 'latency': {'avg': round(sum(lat) / len(lat), 2) if lat else 0.0, 'p50': pct(50), 'p95': pct(95), 'p99': pct(99)}, 'value_captured': round(ev[0], 0), 'avg_value': round(ev[1], 2), 'by_action': [{'action': a, 'count': c} for a, c in by_action], 'by_use_case': [{'use_case': u, 'count': c} for u, c in by_use], 'by_region': [{'region': rg, 'count': c} for rg, c in by_region]}

@app.get('/stream')
def stream():
    return {'events': list(_events)[:24], 'decisions': list(_recent)[:24]}

@app.get('/health')
def health():
    return {'status': 'ok', 'backends': db.backends(), 'parties': (db.fetchone('SELECT COUNT(*) FROM party') or [0])[0], 'audit_rows': audit.count(), 'agent_engine': 'langgraph' if agent._HAS_LANGGRAPH else 'hand-rolled'}
