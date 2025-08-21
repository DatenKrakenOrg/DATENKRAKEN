import streamlit as st
from utility.datafetcher import DataFetcher
from frontend.status_engine import get_rooms_data
from frontend.status_engine import calculate_room_status
from typing import Dict, List

def render_overview(unique_arduino_ids: List[str], fetcher: DataFetcher, config: dict) -> None:
    """Renders the overview page when called"""
    
    st.title("Overview")
    
    rooms = get_rooms_data(unique_arduino_ids, fetcher)

    for room in rooms:
        room["status"] = calculate_room_status(room["data"], config)

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
        case "optimal":
            st.write(f"🟢 Status: {room["status"].capitalize()}")
        case "warning":
            st.write(f"🟡 Status: {room["status"].capitalize()}")
        case "critical":
            st.write(f"🔴 Status: {room["status"].capitalize()}")
        case _:
            st.write("Unknown")

    st.write(" ")
    for param, value in room["data"].items():
        unit = config["parameters"][param]["unit"]
        st.write(
            f"**{param.replace('_', ' ').capitalize()}**: {value} {unit}"
        )
