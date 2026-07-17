from __future__ import annotations
import json
import random
import threading
import time
from app.layer1_data import db
EVENT_TYPES = ['session_start', 'large_transfer_attempt', 'product_page_view', 'support_ticket_opened', 'card_declined']

def make_event(party_id: str) -> dict:
    et = random.choice(EVENT_TYPES)
    return {'party_id': party_id, 'event_type': et, 'amount': round(random.lognormvariate(4, 1.2), 2) if 'transfer' in et else 0.0, 'channel': random.choice(['app', 'web', 'call_center']), 'ts': time.time()}

def publish(event: dict) -> None:
    store = db.get_online_store()
    key = f"payments__party__last_event__live:{event['party_id']}"
    store.hset(key, event)
    store.rpush('stream:events', json.dumps(event))

def stream(party_ids: list[str], rate_hz: float=200.0, stop: threading.Event | None=None):
    interval = 1.0 / rate_hz
    while not (stop and stop.is_set()):
        publish(make_event(random.choice(party_ids)))
        time.sleep(interval)
if __name__ == '__main__':
    ids = [r[0] for r in db.fetchall('SELECT party_id FROM party LIMIT 100')]
    for _ in range(20):
        e = make_event(random.choice(ids))
        publish(e)
        print(e)
