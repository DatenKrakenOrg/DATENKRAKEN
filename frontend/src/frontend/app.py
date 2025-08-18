import streamlit as st
import pandas as pd
from functions import define_page, load_config, get_status
from example_room_data import sensor_data_room_1, sensor_data_room_2

status_colors = {"optimal": "green", "warning": "yellow", "critical": "red"}
config = load_config()

def calculate_room_status(sensor_data):
    """Evaluates the overall status of a room based on the most severe status of the parameters.

    Args:
        sensor_data (dict): Dictionary containing sensor readings with the
        following keys:
            - "temperature_inside" (float | int): Room temperature in °C
            - "humidity_inside" (float | int): Relative humidity in %
            - "voc_index" (float | int): Indoor air quality index for volatile organic compounds (VOC)
            - "noise_level" (float | int): Sound level in dB(A)

    Returns:
        str: The aggregated room status, one of:
            - "critical": if any sensor is in a critical state
            - "warning": if no sensor is critical, but at least one is warning
            - "optimal": if all sensors are within optimal range
    """
    room_status = "optimal"
    for param, value in sensor_data.items():
        status = get_status(value, param)
        if status == "critical":
            return "critical"   
        elif status == "warning" and room_status == "optimal":
            room_status = "warning"
    return room_status


def main():
    """Streamlit app entry point for displaying room sensor overviews."""

    
    st.set_page_config(layout="wide")
    st.title("Overview")

    if "rooms" not in st.session_state:
        st.session_state.rooms = [
            {"name": "Room 1", "data": sensor_data_room_1},
            {"name": "Room 2", "data": sensor_data_room_2}
        ]


    for room in st.session_state.rooms:
        room["status"] = calculate_room_status(room["data"])

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

if __name__ == "__main__":
    main()