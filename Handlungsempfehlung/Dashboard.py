import streamlit as st
from status_engine import get_status, get_recommendations, get_virtual_recommendations, filter_recommendations, fetch_weather_data
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import json
import os
API_KEY = "756c317560b3496480d121915252507"
LOCATION = "Heidenheim,DE"
st.set_page_config(layout="wide")


#-------------------------------------------------------------
# Example Streamlit Dashboard to Test the Status Engine
# Run with `streamlit run Dashboard.py`
#-------------------------------------------------------------








# -------------------------------
# Parameter-Konfiguration laden
# -------------------------------
def load_config(config_file="parameter.json"):
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, config_file)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()


# -------------------------------
# Gauge-Plot Funktion
# -------------------------------
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



# -------------------------------
# Farbe abhängig vom Status
# -------------------------------
def get_bar_color(param_name, value):
    status = get_status(value, param_name)
    if status == "optimal":
        return "green"
    elif status == "warning":
        return "orange"
    else:  # critical
        return "red"
    

#--------------------------------
# Beispiel-Sensordaten
#--------------------------------
sensor_data = {
    "temperature_inside": 20,   # Beispielwert für Innentemperatur
    "humidity_inside": 35,      # Beispielwert für Innenfeuchtigkeit
    "co2_level": 1200,          # Beispielwert für CO2-Gehalt
    "noise_level": 55           # Beispielwert für Geräuschpegel
}



# -------------------------------
# Dashboard Inhalt
# -------------------------------

st.title("Raumüberwachung Dashboard")

# Statusanzeige in der Sidebar
st.sidebar.header("Statusanzeige")
for param, value in sensor_data.items():
    unit = config["parameters"][param]["unit"]
    status = get_status(value, param)
    st.sidebar.write(f"{param.replace('_', ' ').capitalize()}: {value} {unit} ({status})")

# Empfehlungen holen
recommendations = get_recommendations(sensor_data)

# Wetter-Empfehlungen
virtual_recs = get_virtual_recommendations(API_KEY, LOCATION)
recommendations.extend(virtual_recs)

# Filter anwenden
weather_data = fetch_weather_data(API_KEY, LOCATION)
recommendations = filter_recommendations(sensor_data, weather_data, recommendations)

# Empfehlungen nach Parametern gruppieren
param_to_recs = {key: [] for key in sensor_data.keys()}
for rec in recommendations:
    param_to_recs[rec["parameter"]].append(rec["message"])

# Layout: 4 Spalten
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])


# -------------------------------
# Container für jeden Parameter
# -------------------------------
for idx, (param, value) in enumerate(sensor_data.items()):
    col = [col1, col2, col3, col4][idx]
    with col:
        with st.container(border=True):
            title = param.replace("_", " ").capitalize()
            unit = config["parameters"][param]["unit"]
            optimal_range = config["parameters"][param]["optimal_range"]
            tolerance = config["parameters"][param]["tolerance"]

            display_range = config["parameters"][param]["display_range"]
            value_range = [display_range["min"], display_range["max"]]

            # Farbe für Gauge-Balken
            bar_color = get_bar_color(param, value)

            # Gauge-Chart
            fig = gauge_plot(value, title, value_range, bar_color, unit)
            st.plotly_chart(fig, use_container_width=False)

            # Empfehlungen / Warnungen
            if param_to_recs[param]:
                for msg in param_to_recs[param]:
                    if "!" in msg:
                        st.error(msg)  # Handlungsempfehlung = rot
                    else:
                        st.warning(msg)  # Warnung = gelb
            else:
                st.success("Wert im optimalen Bereich")  # Optimal = grün

# ---------------------------------------
# Aktuelles Wetter in Heidenheim anzeigen
# ---------------------------------------
st.markdown("---")  # Trennlinie

weather_data = fetch_weather_data(API_KEY, "Heidenheim,DE")

if weather_data:
    location_name = weather_data["location"]["name"]
    temp = weather_data["current"]["temp_c"]
    condition = weather_data["current"]["condition"]["text"]
    rain_chance = weather_data["forecast"]["forecastday"][0]["day"]["daily_chance_of_rain"]

    st.subheader(f"Aktuelles Wetter in {location_name}")
    st.write(f"**{condition}**, {temp} °C, Regenwahrscheinlichkeit: {rain_chance} %")
else:
    st.warning("Konnte Wetterdaten nicht abrufen (bitte API-Key prüfen).")