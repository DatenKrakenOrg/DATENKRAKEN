import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from status_engine import (
    load_config,
    get_status,
    get_recommendations,
    get_virtual_recommendations,
    filter_recommendations,
    fetch_weather_data,
)

API_KEY = os.getenv("WEATHER_API_KEY")
LOCATION = "Heidenheim,DE"






def gauge_plot(value: float, title: str, value_range: List[float], bar_color: str, unit: str) -> go.Figure:
    """Create a Plotly gauge chart for visualizing a single sensor value.

    The gauge displays the given value within a defined range and uses a
    colored bar to indicate its position. A numeric label with a unit is also
    shown inside the gauge.

    Args:
        value (float): The numeric value to display.
        title (str): Title of the gauge (e.g., parameter name).
        value_range (List[float]): Two-element list [min, max] defining the axis range. Defined in parameter.json.
        bar_color (str): Color of the gauge's bar (e.g., "green", "red").
        unit (str): Measurement unit displayed next to the value (e.g., "°C"). Defined in parameter.json.

    Returns:
        go.Figure: A Plotly figure object containing the gauge visualization."""
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
    """Return the color for a gauge bar based on parameter status.

    Uses `get_status` to evaluate the given sensor value against the
    configured thresholds. Maps the resulting status to a display color:

        - "optimal"  -> "green"
        - "warning"  -> "orange"
        - "critical" -> "red"

    Args:
        param_name (str): Name of the parameter (e.g., "temperature_inside").
        value (float): Sensor reading to evaluate.

    Returns:
        str: Color name ("green", "orange", or "red") corresponding to
        the parameter status.
    """
    status = get_status(value, param_name)
    if status == "optimal":
        return "green"
    elif status == "warning":
        return "orange"
    return "red"


def build_param_recommendations(sensor_data: Dict[str, float]) -> Dict[str, List[str]]:
    """Build parameter-to-recommendation mappings from sensor and weather data.
    The resulting recommendations are grouped by parameter name so that
    each parameter has a list of associated messages.

    Args:
        sensor_data (Dict[str, float]): Dictionary of sensor readings,
            e.g.:
            {
                "temperature_inside": 22,
                "humidity_inside": 40,
                "voc_index": 120,
                "noise_level": 55
            }

    Returns:
        Dict[str, List[str]]: Mapping from parameter names to a list of
        recommendation messages."""
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
    """Ensure that a parameter has a valid history DataFrame.

    If no history is provided, if it is empty, or if the given parameter is
    not yet present in the history, this function generates a synthetic
    48-hour history for the parameter with values fluctuating slightly
    around the current value. Otherwise, the existing history DataFrame
    is returned unchanged. 
    """
    #IMPORTANT: Should be removed or replaced with real history fetching logic with a fallback logic.


    if history_df is None or history_df.empty or param not in history_df.get("parameter", pd.Series(dtype=str)).unique():
        dates = [datetime.now() - timedelta(hours=i) for i in range(48, -1, -1)]
        vals = [value + (i % 5 - 2) * 0.2 for i in range(len(dates))]
        return pd.DataFrame({"time": dates, "parameter": param, "value": vals})
    return history_df


def filter_period(df: pd.DataFrame, period: str) -> pd.DataFrame:
    """ Filter a history DataFrame by a given time period.

    Keeps only the rows in the DataFrame that fall within the selected
    time window, based on the maximum timestamp in the "time" column.

    Args:
        df (pd.DataFrame): DataFrame with at least a "time" column of
            datetime values.
        period (str): Time period to filter by. Supported values:
            - "Alle": No filtering, return full DataFrame.
            - "24h": Last 24 hours.
            - "7d": Last 7 days.
            - "30d": Last 30 days.
            - "90d": Last 90 days.

    Returns:
        pd.DataFrame: Filtered DataFrame containing only rows within
        the chosen period.

    """
                
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
    """Compute padded y-axis ranges from a time series DataFrame.

    The function calculates the minimum and maximum values of the "value"
    column and applies a 10% padding. It returns both a default range
    (slightly padded around the data) and a global range (covering the
    actual min/max values as well).

    Args:
        df (pd.DataFrame): DataFrame with a numeric "value" column.

    Returns:
        Tuple[float, float, float, float]:
            - default_min: Lower bound with padding applied.
            - default_max: Upper bound with padding applied.
            - global_min: Absolute minimum (may equal or be below default_min).
            - global_max: Absolute maximum (may equal or be above default_max)."""
    y_min = float(df["value"].min())
    y_max = float(df["value"].max())
    pad = (y_max - y_min) * 0.1 if y_max > y_min else max(abs(y_min), 1.0) * 0.1
    default_min = y_min - pad
    default_max = y_max + pad
    global_min = min(default_min, y_min)
    global_max = max(default_max, y_max)
    return default_min, default_max, global_min, global_max


def render_overview_grid(config: Dict, sensor_data: Dict[str, float], param_to_recs: Dict[str, List[str]]) -> None:
    """Render a grid of gauges and recommendations in a Streamlit app.

    Displays each parameter from `sensor_data` in a 4-column grid layout.
    For each parameter, a gauge plot is shown along with status indicators
    and recommendation messages.

    Args:
        config (Dict): Configuration dictionary with parameter definitions,
            must include for each parameter:
                {
                    "unit": <str>,
                    "display_range": {"min": <float>, "max": <float>}
                }
        sensor_data (Dict[str, float]): Dictionary of current sensor values,
            keyed by parameter name.
        param_to_recs (Dict[str, List[str]]): Mapping from parameter names
            to recommendation messages (warnings, hints, etc.).

    Returns:
        None
        The function directly renders Streamlit components (gauges,
        status messages, recommendations)."""
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
    """Render the header section for the detailed parameter view in Streamlit.

    Provides navigation and parameter selection:
      - A **back button** ("Zurück") to switch the app back to overview mode.
      - A **dropdown (selectbox)** to choose which parameter is currently
        displayed in detail view.

    The function ensures that `st.session_state.selected_param` is always set
    to a valid parameter from `sensor_data`.

    Args:
        sensor_data (Dict[str, float]): Dictionary of current sensor values,
            keyed by parameter name.

    Returns:
        Optional[str]: The currently selected parameter name, or None if
        `sensor_data` is empty."""

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
    """Render a detailed insight view for a selected parameter.

    Displays a gauge visualization, current and recent metrics, status,
    recommended ranges, and optional recommendations for the given parameter.

    Args:
        config (Dict): Configuration dictionary containing parameter metadata,
            must include for each parameter:
                {
                    "unit": <str>,
                    "display_range": {"min": <float>, "max": <float>},
                    "optimal_range": {"min": <float>, "max": <float>}
                }
        param (str): The parameter name (e.g., "temperature_inside").
        value (float): The current sensor reading for the parameter.
        history_df (pd.DataFrame): DataFrame of historical values with columns
            ["time", "parameter", "value"]. Used to compute deltas.
        param_to_recs (Optional[Dict[str, List[str]]]): Mapping from parameter
            names to recommendation messages. If provided, recommendations
            for `param` are displayed.

    Returns:
        None
        The function directly renders UI components."""
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
    """Render a detailed time series chart for a given parameter in Streamlit.

    Provides interactive visualization of historical parameter data with
    filtering, y-axis control, and CSV export functionality.

    Args:
        param (str): The parameter name (e.g., "temperature_inside").
        unit (str): The unit of the parameter (e.g., "°C").
        df (pd.DataFrame): History DataFrame with columns ["time", "parameter", "value"].
        config (dict): Configuration dictionary that must define
            config["parameters"][param]["display_range"] with "min" and "max".

    Returns:
        None
        The function directly renders UI components."""
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
    """Render the detailed view for a selected parameter in Streamlit.

    Combines the header, insights, and time series components into a
    full detail page for one parameter chosen by the user.

    Args:
        config (Dict): Configuration dictionary containing parameter metadata.
            Must include for each parameter:
                {
                    "unit": <str>,
                    "display_range": {"min": <float>, "max": <float>},
                    "optimal_range": {"min": <float>, "max": <float>}
                }
        sensor_data (Dict[str, float]): Dictionary of current sensor readings,
            keyed by parameter name.
        history_df (Optional[pd.DataFrame]): Historical readings with columns
            ["time", "parameter", "value"]. If None or incomplete, synthetic
            history is generated via `ensure_history`.
        param_to_recs (Optional[Dict[str, List[str]]]): Optional mapping from
            parameter names to recommendation messages.

    Returns:
        None
        The function directly renders Streamlit UI components."""
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
    """Define and render the Streamlit dashboard page for a specific room.

    Sets up the Streamlit page layout, loads configuration, manages
    session state (overview vs. detail view), and renders either the
    parameter overview grid or the detailed parameter view.

    Args:
        roomNumber (int): Identifier for the room (used in page title).
        sensor_data (Dict[str, float]): Dictionary of current sensor readings
            keyed by parameter name.
        history_df (Optional[pd.DataFrame]): Optional history of sensor data
            with columns ["time", "parameter", "value"]. If None, synthetic
            history will be generated when required.

    Returns:
        None
        The function directly renders the Streamlit UI components."""
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
    
