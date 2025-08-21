import streamlit as st
from typing import Dict
from database.orm import SensorType
from utility.datafetcher import DataFetcher
from frontend.status_engine import get_single_room_data

from .widgets.utils import sensor_data_language_dict, get_status, SensorStatus
from .widgets.current_insights_widget import render_gauge_column, render_recommendation_column


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

    render_current_insights(arduino_id, sensor_data["data"], config)

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
        str: sensor_specifier as described by sensor_data dictionary keys (take a look at Args section)
    """
    # Mapped on german language!
    sensor_selection = st.selectbox("Sensorauswahl", sensor_data_language_dict.keys(), accept_new_options=False)
    # Take a look at parameter.json to understand the keys here!
    config_param_json_name = sensor_data_language_dict[sensor_selection]

    # Get all placeholder values for the to be placed widgets
    sensor_display_range = tuple(config["parameters"][config_param_json_name]["display_range"].values())
    sensor_optimal_range = config["parameters"][config_param_json_name]["optimal_range"]
    sensor_recommendation_tolerance = config["parameters"][config_param_json_name]["tolerance"]

    _current_sensor_status = get_status(
        sensor_data[config_param_json_name], config_param_json_name, config
    )

    gauge_bar_color = _current_sensor_status.value[0]
    display_unit_of_sensor = config["parameters"][config_param_json_name]["unit"]

    col1, col2 = st.columns(2)

    with col1:
        render_gauge_column(sensor_data[config_param_json_name], sensor_selection, sensor_display_range, gauge_bar_color, display_unit_of_sensor)

    with col2:
        render_recommendation_column(sensor_selection, sensor_data[config_param_json_name], _current_sensor_status, display_unit_of_sensor, sensor_optimal_range, sensor_recommendation_tolerance)

    return config_param_json_name

def render_history_graph(
    arduino_id: str, sensor_data: Dict[str, float], config: dict
):
    pass

