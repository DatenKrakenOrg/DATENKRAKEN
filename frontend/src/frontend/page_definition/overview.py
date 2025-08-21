import streamlit as st
from utility.datafetcher import DataFetcher
from frontend.utils import get_rooms_data
from frontend.page_definition.generic_analytics.widgets.utils import get_status, SensorStatus
from typing import Dict, List

def render_overview(unique_arduino_ids: List[str], fetcher: DataFetcher, config: dict) -> None:
    """Renders the overview page when called"""
    
    st.title("Overview")
    
    rooms = get_rooms_data(unique_arduino_ids, fetcher)

    for room in rooms:
        room["status"] = SensorStatus.OPTIMAL
        for sensor_specifier in room["data"]:
            status = get_status(room["data"][sensor_specifier], sensor_specifier, config)
            room["status"] = status
            if status != SensorStatus.OPTIMAL:
                break

    cols = st.columns(len(rooms))

    for idx, room in enumerate(rooms):
        with cols[idx]:
            with st.container(border=True):
                _write_card_content(room, config)

def _write_card_content(room: Dict[str, float], config: dict) -> None:
    """Takes the room data dictionary and renders the streamlit widgets within a streamlit container

    Args:
        room (Dict[str, float]): Room data as described in frontend.status_engine.get_rooms_data
    """
    st.subheader(room["name"])
    match room["status"]:
        case SensorStatus.OPTIMAL:
            st.write(f"🟢 Status: {room["status"].value[1].capitalize()}")
        case SensorStatus.WARNING:
            st.write(f"🟡 Status: {room["status"].value[1].capitalize()}")
        case SensorStatus.CRITICAL:
            st.write(f"🔴 Status: {room["status"].value[1].capitalize()}")
        case _:
            st.write("Unknown")

    st.write(" ")
    for param, value in room["data"].items():
        unit = config["parameters"][param]["unit"]
        st.write(
            f"**{param.replace('_', ' ').capitalize()}**: {value} {unit}"
        )
