"""Test fixtures: a warmed TestClient over the full app.

Uses a small persona set so bootstrap is fast; reuses any existing local data.
"""
import os

os.environ.setdefault("SEED_PARTIES", "400")

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:  # triggers startup bootstrap once
        yield c


@pytest.fixture(scope="session")
def party_id(client):
    return client.get("/personas?limit=1").json()[0]["party_id"]
