import streamlit as st
import requests
import os
from typing import Dict
from enum import Enum
from database.orm import SensorType

sensor_data_language_dict = {
    "Temperatur": "temperature_inside",
    "Luftfeuchtigkeit": "humidity_inside",
    "Luftqualität (Voc-Index)": "voc_index",
    "Lautstärke": "noise_level",
}

sensor_specifier_type_dict = {
    "temperature_inside": SensorType.TEMPERATURE,
    "humidity_inside": SensorType.HUMIDITY,
    "voc_index": SensorType.VOC,
    "noise_level": SensorType.NOISE
}


class SensorStatus(Enum):
    """Enum representing the status of sensor based on a value

    Args:
        Enum (Tuple[str]): First index representing a color (f.e. used for a gauge meter), second index representing a string that can be shown in the UI
    """

    OPTIMAL = ("green", "Optimal")
    WARNING = ("orange", "Suboptimal")
    CRITICAL = ("red", "Kritisch")


def get_status(value, sensor_specifier, config) -> SensorStatus:
    """Evaluate the status of a sensor reading against configured thresholds.

    The function checks the given value against the parameter configuration
    loaded in the global `config` dictionary. Each parameter defines an
    optimal range and a tolerance. The returned status is determined as:

        - "optimal": Value is within the defined optimal range.
        - "warning": Value is outside the optimal range but within the
          tolerance margin.
        - "critical": Value is outside both the optimal range and tolerance.
        - "unknown": If the parameter is not defined in the configuration.

    Args:
        value (int | float): The sensor reading to evaluate.
        sensor_specifier (str): The name of the parameter to look up in config,
            e.g. "temperature_inside", "humidity_inside", "voc_index",
            "noise_level".

    Returns:
        SensorStatus: One of SensorStatus."""
    param_cfg = config["parameters"][sensor_specifier]
    if not param_cfg:
        return "unknown"

    min_opt = param_cfg["optimal_range"]["min"]
    max_opt = param_cfg["optimal_range"]["max"]
    tolerance = param_cfg["tolerance"]

    if min_opt <= value <= max_opt:
        return SensorStatus.OPTIMAL
    elif (min_opt - tolerance) <= value <= (max_opt + tolerance):
        return SensorStatus.WARNING
    else:
        return SensorStatus.CRITICAL


@st.cache_data(ttl="0.25h")
def fetch_weather_data() -> Dict[str, float]:
    """Fetch current weather data from the OpenWeatherMap API.

    Builds a request to the OpenWeatherMap REST API for the specified
    location, retrieves the weather information and returns it as a JSON dictionary.

    Returns:
        Dict[str, float] | None: Weather data as Dict[str, float], with humidty and temperature as keys,
        otherwise None if the request fails."""

    url = f"https://api.openweathermap.org/data/2.5/weather?q={os.getenv('LOCATION')}&appid={os.getenv('WEATHER_API_KEY')}&units=metric&lang=de"
    try:
        response = requests.get(url)
        response.raise_for_status()
        response_json = response.json()

        return {
            "temperature": response_json["main"]["temp"],
            "humidity": response_json["main"]["humidity"],
        }
    except Exception as e:
        #new changes Soft-fail on weather API errors; UI will skip weather hints
        st.info("Weather data temporarily unavailable.")
        return None
