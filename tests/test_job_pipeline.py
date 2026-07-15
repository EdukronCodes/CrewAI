from app.services.job_pipeline import run_job_search


def test_run_job_search_returns_matches(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    result = run_job_search("Python Engineer", "Remote", "mid", "Python, FastAPI, AWS")
    assert "summary" in result
    assert isinstance(result["matches"], list)
    assert result["matches"]
