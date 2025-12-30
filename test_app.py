import os
import pytest
from fastapi.testclient import TestClient
from app import app, TAVILY_API_KEY  # assuming your main file is named app.py

# For real testing we need a valid key, but for unit tests we can mock Tavily
# Here we use dependency override + mock for isolation

client = TestClient(app)

# ────────────────────────────────────────────────
# 1. Basic health check (no external dependency)
# ────────────────────────────────────────────────
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "message": "Web Search Microservice is running"}


# ────────────────────────────────────────────────
# 2. Quick search endpoint (GET)
# ────────────────────────────────────────────────
def test_quick_search_success(monkeypatch):
    # Mock Tavily response
    mock_response = {
        "query": "test query",
        "answer": "This is a mock summary",
        "results": [
            {
                "title": "Mock Title",
                "url": "https://example.com",
                "content": "Mock content snippet",
                "score": 0.95
            }
        ]
    }

    class MockTavily:
        def search(self, query, **kwargs):
            return mock_response

    monkeypatch.setattr("app.tavily", MockTavily())

    response = client.get("/quick-search?query=test%20query")
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "test query"
    assert "answer" in data
    assert len(data["results"]) == 1
    assert data["results"][0]["title"] == "Mock Title"


def test_quick_search_error_handling(monkeypatch):
    class MockTavilyError:
        def search(self, query, **kwargs):
            raise Exception("Tavily API is down")

    monkeypatch.setattr("app.tavily", MockTavilyError())

    response = client.get("/quick-search?query=anything")
    assert response.status_code == 500
    assert "Tavily search error" in response.json()["detail"]


# ────────────────────────────────────────────────
# 3. Main /search endpoint (POST)
# ────────────────────────────────────────────────
@pytest.mark.parametrize("payload, expected_status", [
    (
        {
            "query": "latest robotics 2025",
            "search_depth": "advanced",
            "max_results": 5,
            "include_answer": True
        },
        200
    ),
    (
        {
            "query": "",
        },
        422   # validation error – missing required field
    ),
    (
        {
            "query": "test",
            "search_depth": "invalid"   # should still pass (Tavily will default)
        },
        200
    )
])
def test_search_endpoint(payload, expected_status, monkeypatch):
    mock_response = {
        "query": payload.get("query", ""),
        "answer": "Mock answer",
        "results": [{"title": "Test", "url": "http://test.com", "content": "...", "score": 0.9}]
    }

    class MockTavily:
        def search(self, query, **kwargs):
            return mock_response

    monkeypatch.setattr("app.tavily", MockTavily())

    response = client.post("/search", json=payload)
    assert response.status_code == expected_status

    if expected_status == 200:
        data = response.json()
        assert "query" in data
        assert "results" in data
        assert len(data["results"]) > 0


# ────────────────────────────────────────────────
# 4. Environment variable check (critical safety)
# ────────────────────────────────────────────────
def test_missing_api_key_raises_error(monkeypatch):
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    
    with pytest.raises(ValueError) as exc_info:
        # Force module reload or re-init to trigger the check
        # (in real project you might extract this check into a function)
        from app import TAVILY_API_KEY
    assert "TAVILY_API_KEY not set" in str(exc_info.value)
