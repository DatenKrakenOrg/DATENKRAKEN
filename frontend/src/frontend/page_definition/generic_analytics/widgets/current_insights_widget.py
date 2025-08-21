import streamlit as st
import plotly.graph_objects as go
from typing import Tuple, Dict, List

from .utils import sensor_data_language_dict, SensorStatus, fetch_weather_data

def gauge_plot(value: float, title: str, value_range: Tuple[float], bar_color: str, unit: str) -> go.Figure:
    """Create a Plotly gauge chart for visualizing a single sensor value.

    The gauge displays the given value within a defined range and uses a
    colored bar to indicate its position. A numeric label with a unit is also
    shown inside the gauge.

    Args:
        value (float): The numeric value to display.
        title (str): Title of the gauge (e.g., parameter name).
        value_range (Tuple[float]): Two-element list [min, max] defining the axis range. Defined in parameter.json.
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
    fig.update_layout(width=250, height=250, margin=dict(l=20, r=28, t=50, b=20))
    return fig

def render_gauge_column(value: float, title: str, value_range: Tuple[float], bar_color: str, unit: str):
    """Renders the gauge meter widget. Typically located on the right side of the current_insights widget.

    Args:
        value (float): Value that gauge meter should show.
        title (str): Heading of the gauge meter and widget.
        value_range (Tuple[float]): Allowed value range of sensor. Used as axis for the gauge meter.
        bar_color (str): Color of the gauge meter bar. Typically specified by its status (f.e. critical => red)
        unit (str): Unit of the sensors measurement
    """
    st.subheader(f"{title} - Tachometer")
    st.plotly_chart(
            gauge_plot(value, title, value_range, bar_color, unit)
        )

def render_recommendation_column(sensor_selection: str, value: float, sensor_status: SensorStatus, sensor_unit: str, optimal_range: Dict[str, int], recommendation_tolerance: float):
    """Renders the recommendation widget. Typically located on the right side of the current_insights widget

    Args:
        sensor_selection (str): Sensor selection value extracted by the parents st.selectbox. Must match frontend.page_definition.widgets.utils.sensor_data_language_dict
        value (float): Sensor value that the widget should depend on
        sensor_status (SensorStatus): Interpreted SensorStatus
        sensor_unit (str): Unit of the sensors measurement
        optimal_range (Dict[str, int]): Optimal range in which no action recommendation to the user is needed. Keys: ("min", "max") 
        recommendation_tolerance (float): Tolerance specifying a offset in which the optimal ranges min and max is added on before a recommendation is made
    """
    st.subheader(f"{sensor_selection} • Empfehlungen")
    sensor_specifier = sensor_data_language_dict[sensor_selection]
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Aktueller Wert", f"{value} {sensor_unit}")
    with col2:
        st.metric("Status", sensor_status.value[1])
    st.caption(f"Empfohlener Bereich: {optimal_range["min"]}–{optimal_range["max"]} {sensor_unit}")
    for text in _get_recommendation_texts(sensor_specifier, value, optimal_range, recommendation_tolerance):
        st.caption(text)

def _get_recommendation_texts(sensor_specifier: str, value: float, optimal_range: Dict[str, int], recommendation_tolerance: float) -> List[str]:
    """Evaluates a recommendation text based on a sensor_specifier and its value

    Args:
        sensor_specifier (str): Sensor specifier as described by sensor_data
        value (float): Sensor value a recommendation should be evaluated from
        optimal_range (Dict[str, int]): Optimal range in which no action recommendation to the user is needed. Keys: ("min", "max")  
        recommendation_tolerance (float): Tolerance specifying a offset in which the optimal ranges min and max is added on before a recommendation is made

    Returns:
        List[str]: A list of recommendations for the user
    """
    recommendation_texts: List[str] = []
    weather_data = fetch_weather_data()
    print(weather_data)
    match sensor_specifier:
        case "temperature_inside":
            if value < optimal_range['min'] - recommendation_tolerance:
                recommendation_texts.append("Heizen empfohlen, um die Raumtemperatur zu erhöhen!")
                if weather_data["temperature"] > value:
                    recommendation_texts.append("Öffne auch das Fenster, da die Außentemperatur aufheizt.")
            elif value > optimal_range['max'] + recommendation_tolerance:
                recommendation_texts.append("Nutze Klimageräte oder Ventilatoren, um die Temperatur zu senken!")
                if weather_data["temperature"] < value:
                    recommendation_texts.append("Öffne auch das Fenster, da die Außentemperatur abkühlt.")
        case "humidity_inside":
            if value < optimal_range['min'] - recommendation_tolerance:
                recommendation_texts.append("Luftbefeuchter einsetzen, um die Luftfeuchtigkeit zu erhöhen!")
                if weather_data["humidity"] > value:
                    recommendation_texts.append("Öffne auch das Fenster, da die Außenluftfeuchtigkeit anfeuchtet.")
            elif value > optimal_range['max'] + recommendation_tolerance:
                recommendation_texts.append("Lüfte oder nutze Entfeuchter, um die Luftfeuchtigkeit zu reduzieren!")
                if weather_data["humidity"] < value:
                    recommendation_texts.append("Öffne auch das Fenster, da die Außenluftfeuchtigkeit trocknet.")
        case "voc_index":
            if value > optimal_range['max'] + recommendation_tolerance:
                recommendation_texts.append("Räume sofort lüften und mögliche Schadstoffquellen entfernen!")
        case "noise_level":
            if value > optimal_range['max'] + recommendation_tolerance:
                recommendation_texts.append("Geräuschquellen (z.B. Personen, Geräte, Umgebungsgeräusche) minimieren!")
    return recommendation_texts

                




