"""Criterion: Product search and best-deal comparison.

Searching MacBook Air returns offers with a best-deal id present in the
results, along with seller, rating, delivery, and discount fields.
"""

import pytest


def test_macbook_air_search_returns_offers_and_best_deal(client):
    resp = client.get("/products/search", params={"q": "MacBook Air", "category": "All", "mode": "demo"})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["query"] == "MacBook Air"
    assert len(data["results"]) >= 1, "expected MacBook Air offers in sample catalog"
    best_id = data["best_deal_id"]
    assert best_id is not None
    ids = [item["id"] for item in data["results"]]
    assert best_id in ids
    best_offer = next(item for item in data["results"] if item["id"] == best_id)
    # best offer must be the lowest price among results
    assert best_offer["price"] == min(item["price"] for item in data["results"])
    for item in data["results"]:
        assert "seller" in item and item["seller"]
        assert "rating" in item
        assert "delivery" in item
        assert "source" in item and item["source"]


def test_search_rejects_too_short_query(client):
    resp = client.get("/products/search", params={"q": "M", "category": "All", "mode": "demo"})
    assert resp.status_code == 422, resp.text
