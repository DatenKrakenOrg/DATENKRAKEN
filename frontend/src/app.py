import streamlit as st
import pandas as pd
from functions import define_page, load_config, get_status
from example_room_data import sensor_data_room_1, sensor_data_room_2


#install uv and execute 'uv sync' first to ensure all dependencies are installed




status_colors = {"optimal": "green", "warning": "yellow", "critical": "red"}
config = load_config()

def calculate_room_status(sensor_data):
    room_status = "optimal"
    for param, value in sensor_data.items():
        status = get_status(value, param)
        if status == "critical":
            return "critical"   
        elif status == "warning" and room_status == "optimal":
            room_status = "warning"
    return room_status



st.set_page_config(layout="wide")
st.title("Overview")

if "rooms" not in st.session_state:
    st.session_state.rooms = [
        {"name": "Room 1", "data": sensor_data_room_1},
        {"name": "Room 2", "data": sensor_data_room_2}
    ]


for room in st.session_state.rooms:
    room_status = "optimal"
    for param, value in room["data"].items():
        status = get_status(value, param)
        if status == "critical":
            room_status = "critical"
            break
        elif status == "warning" and room_status != "critical":
            room_status = "warning"
    room["status"] = room_status

status_colors = {"optimal": "green", "warning": "yellow", "critical": "red"}


cols = st.columns(len(st.session_state.rooms))


for idx, room in enumerate(st.session_state.rooms):
    color = status_colors.get(room["status"], "gray")
    with cols[idx]:
        with st.container(border=True):
            st.subheader(room["name"])
            st.markdown(
                f"""
                <div style="display:flex;align-items:center;">
                    <div style="height:15px;width:15px;background-color:{color};
                    border-radius:50%;margin-right:8px;"></div>
                    <span>Status: {room['status'].capitalize()}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.write(" ")
            for param, value in room["data"].items():
                unit = config["parameters"][param]["unit"]
                st.write(f"**{param.replace('_', ' ').capitalize()}**: {value} {unit}")

