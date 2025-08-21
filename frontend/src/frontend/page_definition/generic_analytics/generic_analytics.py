import streamlit as st
from typing import Dict
from datetime import datetime, timedelta
from utility.datafetcher import DataFetcher
from frontend.status_engine import get_single_room_data

from .widgets.utils import sensor_data_language_dict, sensor_specifier_type_dict, get_status
from .widgets.current_insights_widget import render_gauge_column, render_recommendation_column
from .widgets.history_widget import show_timeline_widget


def define_generic_analytics_page(arduino_id: str, fetcher: DataFetcher, config: dict) -> None:
    """Define and render the Streamlit dashboard page for a specific room.

    Sets up the Streamlit page layout, loads configuration, manages
    session state (overview vs. detail view), and renders either the
    parameter overview grid or the detailed parameter view.

    Args:
        arduino_id (str): Identifier for the room (used in page title).
        fetcher (DataFetcher): DataFetcher used to fetch database.
    """
    st.set_page_config(page_title=f"Raum {arduino_id} Dashboard", layout="wide")
    st.title(f"Raumüberwachung: {arduino_id}")
    sensor_data = get_single_room_data(arduino_id, fetcher)

    sensor_specifier = render_current_insights(arduino_id, sensor_data["data"], config)
    render_history_graph(arduino_id, sensor_specifier, fetcher, config)

    # param_to_recs = build_param_recommendations(sensor_data, config)

    # if st.session_state.view_mode == "detail":
    #     detail_view(config=config, sensor_data=sensor_data, history_df=history_df, param_to_recs=param_to_recs)
    #     return
    # if st.button(f"Detailed view ({arduino_id})"):
    #     if st.session_state.selected_param is None and len(sensor_data) > 0:
    #         st.session_state.selected_param = list(sensor_data.keys())[0]
    #     st.session_state.view_mode = "detail"
    #     st.rerun()
    # render_overview_grid(config, sensor_data, param_to_recs)
    # st.divider()


def render_current_insights(
    arduino_id: str, sensor_data: Dict[str, float], config: dict
) -> str:
    """Renders the current insight widget

    First selects all needed placeholder values for each widget by its sensor specifier out of the config json. Then calls the correct widget to display its components.

    Args:
        arduino_id (str): Current arduino_id (room) that should be displayed
        sensor_data (Dict[str, float]): Sensor data dictionary consisting of keys: ("temperature_inside", "humidity_inside", "voc_index", "noise_level") which maps a sensor to its latest value (float)
        config (dict): Config dictionary as described by frontend/src/frontend/parameter.json

    Returns:
        str: sensor_selection as selected from st.selectbox
    """
    # Mapped on german language!
    sensor_selection = st.selectbox("Sensorauswahl", sensor_data_language_dict.keys(), accept_new_options=False)
    # Take a look at parameter.json to understand the keys here!
    sensor_specifier = sensor_data_language_dict[sensor_selection]

    # Get all placeholder values for the to be placed widgets
    sensor_display_range = tuple(config["parameters"][sensor_specifier]["display_range"].values())
    sensor_optimal_range = config["parameters"][sensor_specifier]["optimal_range"]
    sensor_recommendation_tolerance = config["parameters"][sensor_specifier]["tolerance"]

    _current_sensor_status = get_status(
        sensor_data[sensor_specifier], sensor_specifier, config
    )

    gauge_bar_color = _current_sensor_status.value[0]
    display_unit_of_sensor = config["parameters"][sensor_specifier]["unit"]

    col1, col2 = st.columns(2)

    with col1:
        render_gauge_column(sensor_data[sensor_specifier], sensor_selection, sensor_display_range, gauge_bar_color, display_unit_of_sensor)

    with col2:
        render_recommendation_column(sensor_selection, sensor_data[sensor_specifier], _current_sensor_status, display_unit_of_sensor, sensor_optimal_range, sensor_recommendation_tolerance)

    return sensor_selection

def render_history_graph(
    arduino_id: str, sensor_selection: str, fetcher: DataFetcher, config: dict
):
    sensor_specifier = sensor_data_language_dict[sensor_selection]
    sensor_type = sensor_specifier_type_dict[sensor_specifier]
    display_unit_of_sensor = config["parameters"][sensor_specifier]["unit"]

    time_delta = 1

    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"{sensor_selection}: Historie")
    with col2:
        time_delta_days = st.selectbox("Vergangene Tage ausgehend von Heute", [1, 7, 14, 30, 60], accept_new_options=False)
        time_delta = timedelta(days=time_delta_days)
    
    show_timeline_widget(sensor_type, arduino_id, time_delta, fetcher, display_unit_of_sensor)

    


