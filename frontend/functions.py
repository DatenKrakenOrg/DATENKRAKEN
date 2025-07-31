import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import json
import os
import requests
from status_engine import get_status, get_recommendations, get_virtual_recommendations, filter_recommendations, fetch_weather_data
API_KEY = os.getenv("WEATHER_API_KEY")
LOCATION = "Heidenheim,DE"

def load_config(config_file="parameter.json"):
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, config_file)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def gauge_plot(value, title, value_range, bar_color, unit):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={'suffix': f" {unit}"},
        title={'text': title},
        gauge={
            'axis': {'range': value_range, 'tickcolor': "gray"},
            'bgcolor': "lightgray",
            'bar': {'color': bar_color, 'thickness': 1},
            'steps': [
                {'range': value_range, 'color': "lightgray"},
            ],
        }
    ))
    fig.update_layout(width=250, height=250, margin=dict(l=20, r=20, t=50, b=20))
    return fig


def get_bar_color(param_name, value):
    status = get_status(value, param_name)
    if status == "optimal":
        return "green"
    elif status == "warning":
        return "orange"
    else:  
        return "red"
    
    
def define_page(roomNumber, sensor_data):
    
    st.set_page_config(page_title=f"Raum {roomNumber} Dashboard", layout="wide")
    st.title("Raumüberwachung Dashboard")
    config = load_config()

    st.sidebar.header("Statusanzeige")
    for param, value in sensor_data.items():
        unit = config["parameters"][param]["unit"]
        status = get_status(value, param)
        st.sidebar.write(f"{param.replace('_', ' ').capitalize()}: {value} {unit} ({status})")


    recommendations = get_recommendations(sensor_data)
    virtual_recs = get_virtual_recommendations(API_KEY, LOCATION)
    recommendations.extend(virtual_recs)
    weather_data = fetch_weather_data(API_KEY, LOCATION)
    recommendations = filter_recommendations(sensor_data, weather_data, recommendations)
    param_to_recs = {key: [] for key in sensor_data.keys()}
    for rec in recommendations:
        param_to_recs[rec["parameter"]].append(rec["message"])

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    for idx, (param, value) in enumerate(sensor_data.items()):
        col = [col1, col2, col3, col4][idx]
        with col:
            with st.container(border=True):
                title = param.replace("_", " ").capitalize()
                unit = config["parameters"][param]["unit"]


                status = get_status(value, param)

                display_range = config["parameters"][param]["display_range"]
                value_range = [display_range["min"], display_range["max"]]
                bar_color = get_bar_color(param, value)
                fig = gauge_plot(value, title, value_range, bar_color, unit)
                st.plotly_chart(fig, use_container_width=False)


                if param_to_recs[param]:
                    for msg in param_to_recs[param]:
                        if "!" in msg:
                            st.error(msg)
                        else:
                            st.warning(msg)
                else:

                    if status == "critical":
                        st.error("Wert ist kritisch!")
                    elif status == "warning":
                        st.warning("Wert im Toleranzbereich!")
                    else:
                        st.success("Wert im optimalen Bereich")