import streamlit as st
from frontend import CONFIG, FETCHER, ROOMS
from frontend.status_engine import calculate_room_status
from typing import List, Dict

def render_overview() -> None:
    """Renders the overview page when called"""
    
    st.title("Overview")
    
    rooms = _get_rooms_data()

    for room in rooms:
        room["status"] = calculate_room_status(room["data"], CONFIG)

    cols = st.columns(len(rooms))

    for idx, room in enumerate(rooms):
        with cols[idx]:
            with st.container(border=True):
                _write_card_content(room)

def _get_rooms_data() -> List[dict]:
    """Gets data of newest datapoint within the database gold layer

    Returns:
        List[dict]: List of dictionaries containing keys: name: str (arduino_id of room), data: Dict[str, float] (newest sensor value of room)
    """
    room_data = []
    all_rooms = [room for room in ROOMS.values()]
    # Flatten all_rooms list
    for room in set(room for room_list in all_rooms for room in room_list):
        room_data = FETCHER.get_newest_bucket(room)
        room_data.append(
            {
                "name": room,
                "data": {
                    "temperature_inside": round(room_data[0].avg_value_in_bucket, 2),
                    "humidity_inside": round(room_data[1].avg_value_in_bucket, 2),
                    "voc_index": round(room_data[2].avg_value_in_bucket, 2),
                    "noise_level": round(room_data[3].avg_value_in_bucket, 2),
                },
            }
        )
    return room_data

def _write_card_content(room: Dict[str, float]) -> None:
    """Takes the room data dictionary and renders the streamlit widgets within a streamlit container

    Args:
        room (Dict[str, float]): Room data as described in frontend.room_definition.overview._get_rooms_data
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
        unit = CONFIG["parameters"][param]["unit"]
        st.write(
            f"**{param.replace('_', ' ').capitalize()}**: {value} {unit}"
        )
