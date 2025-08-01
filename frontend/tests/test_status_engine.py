import pytest
from frontend import status_engine

def test_get_status_optimal():
    param = list(status_engine.config["parameters"].keys())[0]
    min_val = status_engine.config["parameters"][param]["optimal_range"]["min"]
    result = status_engine.get_status(min_val, param)
    assert result == "optimal"

def test_get_status_critical():
    param = list(status_engine.config["parameters"].keys())[0]
    min_val = status_engine.config["parameters"][param]["optimal_range"]["min"]
    result = status_engine.get_status(min_val - 100, param)
    assert result == "critical"

def test_fetch_weather_data_returns_dict(monkeypatch):
    def fake_get(*args, **kwargs):
        class FakeResponse:
            def raise_for_status(self): pass
            def json(self): return {"main": {"temp": 20}, "weather": [{"description": "clear"}]}
        return FakeResponse()

    monkeypatch.setattr("requests.get", fake_get)
    data = status_engine.fetch_weather_data("dummy")
    assert isinstance(data, dict)
    assert "main" in data
