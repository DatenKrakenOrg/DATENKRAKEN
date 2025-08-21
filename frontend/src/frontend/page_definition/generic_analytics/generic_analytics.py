import streamlit as st
from typing import Dict
from database.orm import SensorType
from utility.datafetcher import DataFetcher
from frontend.status_engine import get_single_room_data

from .widgets.utils import sensor_data_language_dict, get_status, SensorStatus
from .widgets.current_insights_widget import gauge_plot


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
) -> SensorType:
    # Mapped on german language!
    chosen_sensor = st.selectbox("Sensorauswahl", sensor_data_language_dict.keys(), accept_new_options=False)
    # Take a look at parameter.json to understand the keys here!
    config_param_json_name = sensor_data_language_dict[chosen_sensor]

    # Get all placeholder values for the to be placed widgets
    sensor_display_range = tuple(config["parameters"][config_param_json_name]["display_range"].values())

    _current_sensor_status = get_status(
        sensor_data[config_param_json_name], config_param_json_name, config
    )

    gauge_bar_color = (
        "green"
        if _current_sensor_status == SensorStatus.OPTIMAL
        else "orange"
        if _current_sensor_status == SensorStatus.WARNING
        else "red"
    )
    display_unit_of_sensor = config["parameters"][config_param_json_name]["unit"]

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(
            gauge_plot(sensor_data[config_param_json_name], chosen_sensor, sensor_display_range, gauge_bar_color, display_unit_of_sensor)
        )

    with col2:
        st.write("TBD")

    

