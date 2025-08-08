import pytest
from frontend import functions
import plotly.graph_objects as go
import json
import os

def test_load_config_creates_dict():
    config = functions.load_config("parameter.json")
    assert isinstance(config, dict)
    assert "parameters" in config  # Expected key in the JSON config

def test_gauge_plot_returns_figure():
    fig = functions.gauge_plot(
        value=25,
        title="Test",
        value_range=[0, 50],
        bar_color="green",
        unit="°C"
    )
    assert isinstance(fig, go.Figure)

def test_get_bar_color_optimal(monkeypatch):
    monkeypatch.setattr("frontend.functions.get_status", lambda v, p: "optimal")
    color = functions.get_bar_color("temp", 20)
    assert color == "green"

def test_get_bar_color_warning(monkeypatch):
    monkeypatch.setattr("frontend.functions.get_status", lambda v, p: "warning")
    color = functions.get_bar_color("temp", 20)
    assert color == "orange"

def test_get_bar_color_critical(monkeypatch):
    monkeypatch.setattr("frontend.functions.get_status", lambda v, p: "critical")
    color = functions.get_bar_color("temp", 20)
    assert color == "red"
