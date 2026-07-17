import os
os.environ.setdefault('SEED_PARTIES', '400')
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope='session')
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope='session')
def party_id(client):
    return client.get('/personas?limit=1').json()[0]['party_id']
