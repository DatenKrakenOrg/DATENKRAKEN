import streamlit as st
from utility.datafetcher import DataFetcher
from frontend.utils import get_rooms_data
from frontend.page_definition.generic_analytics.widgets.utils import get_status, SensorStatus
from utility.currentness import temperature_below_five_minutes, noise_below_five_minutes, voc_below_five_minutes, humidity_below_five_minutes, all_sensor_below_five_minutes
from typing import Dict, List

def render_overview(unique_arduino_ids: List[str], fetcher: DataFetcher, config: dict) -> None:
    """Renders the overview page when called"""
    
    st.title("Overview")
    
    #new changes Visible loading and success feedback + error/empty states
    from frontend.utils import render_error_panel
    from database.sql.engine import is_db_healthy  # new changes
    try:
        with st.spinner("Loading room data..."):
            rooms = get_rooms_data(unique_arduino_ids, fetcher)
    except Exception:
        render_error_panel("Could not load data from the database.", "Please check database connectivity and credentials.")
        return

    #new changes If DB is down, show error and stop (no success toast)
    if not is_db_healthy():
        render_error_panel("Database unavailable.", "Please check connectivity and credentials.")
        return

    if not rooms:
        render_error_panel("No data available yet.", "Once the first measurements arrive, they will appear here.")
        return

    for room in rooms:
        room["status"] = SensorStatus.OPTIMAL
        for sensor_specifier in room["data"]:
            status = get_status(room["data"][sensor_specifier], sensor_specifier, config)
            room["status"] = status
            if status != SensorStatus.OPTIMAL:
                break

    #new changes Toast only once per session and only if any value exists
    has_any_value = any(any(v is not None for v in r["data"].values()) for r in rooms)
    if has_any_value and not st.session_state.get("overview_toast_shown"):
        st.toast("Data loaded successfully.", icon="✅")
        st.session_state["overview_toast_shown"] = True

    cols = st.columns(len(rooms))

    for idx, room in enumerate(rooms):
        with cols[idx]:
            with st.container(border=True):
                _write_card_content(room, config)
                #new changes Guard staleness checks to avoid breaking the card on DB issues
                try:
                    arduino_id = int(list(unique_arduino_ids)[idx])
                    if not temperature_below_five_minutes(arduino_id):
                        st.warning(f"{room['name']}: Temperature data is older than 5 minutes")
                    if not humidity_below_five_minutes(arduino_id):
                        st.warning(f"{room['name']}: Humidity data is older than 5 minutes")
                    if not voc_below_five_minutes(arduino_id):
                        st.warning(f"{room['name']}: VOC data is older than 5 minutes")
                    if not noise_below_five_minutes(arduino_id):
                        st.warning(f"{room['name']}: Noise data is older than 5 minutes")
                except Exception:
                    st.info("Staleness checks are temporarily unavailable.")


def _write_card_content(room: Dict[str, float], config: dict) -> None:
    """Takes the room data dictionary and renders the streamlit widgets within a streamlit container

    Args:
        room (Dict[str, float]): Room data as described in frontend.status_engine.get_rooms_data
        config (dict): Configuration with parameter metadata (units, etc.)
    """
    # Status → icon mapping
    status_map = {
        SensorStatus.OPTIMAL: "🟢",
        SensorStatus.WARNING: "🟡",
        SensorStatus.CRITICAL: "🔴",
    }
    icon = status_map.get(room["status"], "❔")

    # Three columns, content goes in the middle
    _, col, _ = st.columns([1, 3, 1])

    with col:
        st.subheader(room["name"])
        st.write(f"{icon} Status: {room['status'].value[1].capitalize()}")
        st.write(" ")

        for param, value in room["data"].items():
            unit = config["parameters"][param]["unit"]
            st.write(f"**{param.replace('_', ' ').capitalize()}**: {value} {unit}")
