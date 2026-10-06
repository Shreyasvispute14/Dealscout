"""Criterion: Login and protected shopping insights.

Valid demo credentials sign in successfully and unlock /api/analytics;
unauthenticated requests to analytics are rejected.
"""

import httpx
import pytest

from .conftest import API_URL

CREDENTIALS = {"email": "preview@dealscout.local", "password": "dealscout123"}


def test_login_succeeds_and_unlocks_analytics():
    with httpx.Client(base_url=API_URL, timeout=30.0) as c:
        login_resp = c.post("/auth/login", json=CREDENTIALS)
        assert login_resp.status_code == 200, login_resp.text
        body = login_resp.json()
        assert body["user"]["email"] == CREDENTIALS["email"]

        # trigger a search so analytics has at least one row tied to this session's run
        search_resp = c.get("/products/search", params={"q": "tscheck insights probe", "category": "All", "mode": "demo"})
        assert search_resp.status_code == 200

        analytics_resp = c.get("/analytics")
        assert analytics_resp.status_code == 200, analytics_resp.text
        summary = analytics_resp.json()
        assert "total_searches" in summary
        assert "unique_queries" in summary
        assert "recent_searches" in summary
        assert "source_counts" in summary
        assert summary["total_searches"] >= 1


def test_analytics_rejects_unauthenticated_request(client):
    resp = client.get("/analytics")
    assert resp.status_code == 401, resp.text


def test_login_rejects_wrong_password(client):
    resp = client.post("/auth/login", json={"email": "preview@dealscout.local", "password": "wrongpass"})
    assert resp.status_code == 401, resp.text
