import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from status_engine import (
    get_status,
    get_recommendations,
    get_virtual_recommendations,
    filter_recommendations,
    fetch_weather_data,
)

API_KEY = os.getenv("WEATHER_API_KEY")
LOCATION = "Heidenheim,DE"


@st.cache_data(show_spinner=False)
def load_config(config_file: str = "parameter.json") -> Dict:
    # Loads parameter configuration from JSON with caching.
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, config_file)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def gauge_plot(value: float, title: str, value_range: List[float], bar_color: str, unit: str) -> go.Figure:
    # Creates a compact Plotly gauge for a single metric.
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"suffix": f" {unit}"},
            title={"text": title},
            gauge={
                "axis": {"range": value_range, "tickcolor": "gray"},
                "bgcolor": "lightgray",
                "bar": {"color": bar_color, "thickness": 1},
                "steps": [{"range": value_range, "color": "lightgray"}],
            },
        )
    )
    fig.update_layout(width=250, height=250, margin=dict(l=20, r=20, t=50, b=20))
    return fig


def get_bar_color(param_name: str, value: float) -> str:
    # Maps a status to a gauge bar color.
    status = get_status(value, param_name)
    if status == "optimal":
        return "green"
    elif status == "warning":
        return "orange"
    return "red"


def build_param_recommendations(sensor_data: Dict[str, float]) -> Dict[str, List[str]]:
    # Collects and groups recommendations per parameter.
    recs = get_recommendations(sensor_data)
    virtual_recs = get_virtual_recommendations(API_KEY, LOCATION)
    recs.extend(virtual_recs)
    weather_data = fetch_weather_data(API_KEY, LOCATION)
    filtered = filter_recommendations(sensor_data, weather_data, recs)
    param_to_recs: Dict[str, List[str]] = {k: [] for k in sensor_data.keys()}
    for r in filtered:
        param_to_recs[r["parameter"]].append(r["message"])
    return param_to_recs


def ensure_history(sensor_data: Dict[str, float], history_df: Optional[pd.DataFrame], param: str, value: float) -> pd.DataFrame:
    # Ensures a non-empty history dataframe for the given parameter by simulating when missing.
    if history_df is None or history_df.empty or param not in history_df.get("parameter", pd.Series(dtype=str)).unique():
        dates = [datetime.now() - timedelta(hours=i) for i in range(48, -1, -1)]
        vals = [value + (i % 5 - 2) * 0.2 for i in range(len(dates))]
        return pd.DataFrame({"time": dates, "parameter": param, "value": vals})
    return history_df


def filter_period(df: pd.DataFrame, period: str) -> pd.DataFrame:
    # Filters the dataframe by a chosen period window.
    if period == "Alle" or df.empty:
        return df
    now = df["time"].max()
    delta_map = {
        "24h": timedelta(hours=24),
        "7d": timedelta(days=7),
        "30d": timedelta(days=30),
        "90d": timedelta(days=90),
    }
    return df[df["time"] >= now - delta_map[period]]


def compute_y_range(df: pd.DataFrame) -> Tuple[float, float, float, float]:
    # Computes default and global y-axis ranges with padding.
    y_min = float(df["value"].min())
    y_max = float(df["value"].max())
    pad = (y_max - y_min) * 0.1 if y_max > y_min else max(abs(y_min), 1.0) * 0.1
    default_min = y_min - pad
    default_max = y_max + pad
    global_min = min(default_min, y_min)
    global_max = max(default_max, y_max)
    return default_min, default_max, global_min, global_max


def render_overview_grid(config: Dict, sensor_data: Dict[str, float], param_to_recs: Dict[str, List[str]]) -> None:
    # Renders the 4-column overview grid with gauges and messages.
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    cols = [col1, col2, col3, col4]
    for idx, (param, value) in enumerate(sensor_data.items()):
        col = cols[idx % 4]
        with col:
            with st.container(border=True):
                title = param.replace("_", " ").capitalize()
                unit = config["parameters"][param]["unit"]
                status = get_status(value, param)
                display_range = config["parameters"][param]["display_range"]
                value_range = [display_range["min"], display_range["max"]]
                bar_color = get_bar_color(param, value)
                fig = gauge_plot(value, title, value_range, bar_color, unit)
                st.plotly_chart(fig, use_container_width=False)
                if param_to_recs.get(param):
                    for msg in param_to_recs[param]:
                        (st.error if "!" in msg else st.warning)(msg)
                else:
                    if status == "critical":
                        st.error("Wert ist kritisch!")
                    elif status == "warning":
                        st.warning("Wert im Toleranzbereich!")
                    else:
                        st.success("Wert im optimalen Bereich")


def render_detail_header(sensor_data: Dict[str, float]) -> Optional[str]:
    # Renders the back button and parameter selector and returns the selected parameter.
    all_params = list(sensor_data.keys())
    if "selected_param" not in st.session_state or st.session_state.selected_param not in all_params:
        st.session_state.selected_param = all_params[0] if all_params else None
    left, right = st.columns([1, 3])
    with left:
        st.write("")
        if st.button("Zurück"):
            st.session_state.view_mode = "overview"
            st.rerun()
    with right:
        if all_params:
            chosen = st.selectbox(
                "Parameter auswählen",
                options=all_params,
                index=all_params.index(st.session_state.selected_param) if st.session_state.selected_param in all_params else 0,
            )
            if chosen != st.session_state.selected_param:
                st.session_state.selected_param = chosen
    return st.session_state.selected_param


def render_detail_insights(config: Dict, param: str, value: float, history_df: pd.DataFrame, param_to_recs: Optional[Dict[str, List[str]]]) -> None:
    # Renders the left-aligned gauge and right-hand insights panel.
    unit = config["parameters"][param]["unit"]
    d_range = config["parameters"][param]["display_range"]
    o_range = config["parameters"][param]["optimal_range"]
    value_range = [d_range["min"], d_range["max"]]
    optimal_range = [o_range["min"], o_range["max"]]
    bar_color = get_bar_color(param, value)
    status = get_status(value, param)
    title = param.replace("_", " ").capitalize()
    col_gauge, col_info = st.columns([1, 1], vertical_alignment="center")
    with col_gauge:
        fig_g = gauge_plot(value=value, title=" ", value_range=value_range, bar_color=bar_color, unit=unit)
        fig_g.update_layout(margin=dict(l=0, r=0, t=50, b=0))
        st.plotly_chart(fig_g, use_container_width=True)
    with col_info:
        st.subheader(f"{title} • Insights")
        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("Aktueller Wert", f"{value:.2f} {unit}")
        delta_txt = "–"
        h = history_df[history_df["parameter"] == param].sort_values("time")
        if len(h) >= 2:
            delta_val = value - h["value"].iloc[-2]
            arrow = "↑" if delta_val > 0 else ("↓" if delta_val < 0 else "→")
            delta_txt = f"{delta_val:+.2f} {unit} {arrow}"
        with k2:
            st.metric("Δ seit letzter Messung", delta_txt)
        with k3:
            st.metric("Status", status.capitalize())
        st.write(" ")
        st.caption(f"Empfohlener Bereich: {optimal_range[0]}–{optimal_range[1]} {unit}")
        if param_to_recs and param_to_recs.get(param):
            with st.expander("Empfehlungen & Hinweise"):
                for m in param_to_recs[param]:
                    (st.error if "!" in m else st.warning)(m)


def render_detail_timeseries(param: str, unit: str, df: pd.DataFrame, config: dict) -> None:
    st.divider()
    left, right = st.columns([1, 1])
    with left:
        st.subheader(f"Verlauf • {param.replace('_', ' ').capitalize()}")
    with right:
        period = st.selectbox("Zeitraum", ["24h", "7d", "30d", "90d", "Alle"], index=1)

    dff = df[df["parameter"] == param].copy().sort_values("time")
    dff = filter_period(dff, period)

    d_range = config["parameters"][param]["display_range"]
    disp_min = float(d_range["min"])
    disp_max = float(d_range["max"])
    if disp_min >= disp_max:
        eps = max(abs(disp_min) * 1e-3, 1e-6)
        disp_min, disp_max = disp_min - eps, disp_max + eps

    y_min_sel, y_max_sel = st.slider(
        "Anzeigebereich (min/max)",
        min_value=float(round(disp_min, 2)),
        max_value=float(round(disp_max, 2)),
        value=(float(round(disp_min, 2)), float(round(disp_max, 2))),
        step=0.01,
        help="Lege den sichtbaren Wertebereich der y-Achse fest.",
    )

    fig_line = px.line(
        dff, x="time", y="value",
        labels={"time": "Zeit", "value": f"Wert ({unit})"}
    )
    fig_line.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        hovermode="x unified",
        xaxis=dict(
            rangeslider=dict(visible=True),
            rangeselector=dict(buttons=[
                dict(count=24, label="24h", step="hour", stepmode="backward"),
                dict(count=7, label="7d", step="day", stepmode="backward"),
                dict(count=30, label="30d", step="day", stepmode="backward"),
                dict(step="all", label="Alle"),
            ]),
        ),
    )
    fig_line.update_yaxes(range=[y_min_sel, y_max_sel])
    st.plotly_chart(fig_line, use_container_width=True)

    csv = dff[["time", "value"]].rename(columns={"time": "Zeit", "value": f"Wert ({unit})"}).to_csv(index=False).encode("utf-8")
    st.download_button("CSV herunterladen", data=csv, file_name=f"{param}_verlauf.csv", mime="text/csv")


def detail_view(config: Dict, sensor_data: Dict[str, float], history_df: Optional[pd.DataFrame] = None, param_to_recs: Optional[Dict[str, List[str]]] = None) -> None:
    # Drives the detail view by selecting a parameter, rendering insights, and plotting the time series.
    selected = render_detail_header(sensor_data)
    if selected is None:
        st.info("Keine Parameter vorhanden.")
        return
    value = float(sensor_data[selected])
    history_df = ensure_history(sensor_data, history_df, selected, value)
    render_detail_insights(config, selected, value, history_df, param_to_recs)
    unit = config["parameters"][selected]["unit"]
    render_detail_timeseries(selected, unit, history_df, config)


def define_page(roomNumber: int, sensor_data: Dict[str, float], history_df: Optional[pd.DataFrame] = None) -> None:
    # Orchestrates page layout: overview grid, a single bottom "Detailed view" button, and the detail page.
    st.set_page_config(page_title=f"Raum {roomNumber} Dashboard", layout="wide")
    st.title("Raumüberwachung Dashboard")
    config = load_config()
    
    if "view_mode" not in st.session_state:
        st.session_state.view_mode = "overview"
    if "selected_param" not in st.session_state:
        st.session_state.selected_param = None
    
    param_to_recs = build_param_recommendations(sensor_data)
    
    if st.session_state.view_mode == "detail":
        detail_view(config=config, sensor_data=sensor_data, history_df=history_df, param_to_recs=param_to_recs)
        return
    if st.button("Detailed view"):
        if st.session_state.selected_param is None and len(sensor_data) > 0:
            st.session_state.selected_param = list(sensor_data.keys())[0]
        st.session_state.view_mode = "detail"
        st.rerun()
    render_overview_grid(config, sensor_data, param_to_recs)
    st.divider()
    
