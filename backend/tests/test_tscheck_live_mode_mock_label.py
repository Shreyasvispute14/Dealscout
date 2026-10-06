"""Criterion: Truthful live-mode fallback.

With no SERPAPI_KEY configured, live-mode search results must be clearly
flagged as mocked/preview and never claimed as real live data.
"""


def test_live_mode_marks_results_as_mocked_preview(client):
    resp = client.get("/products/search", params={"q": "MacBook Air", "category": "All", "mode": "live"})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["mode"] == "live"
    assert data["live_provider_available"] is False
    assert "MOCKED" in data["notice"]
    assert len(data["results"]) >= 1
    for item in data["results"]:
        assert item["is_live"] is False
        assert item["is_mocked"] is True
