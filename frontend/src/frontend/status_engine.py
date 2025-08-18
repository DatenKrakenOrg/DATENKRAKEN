from dotenv import load_dotenv
import json
import os
import requests
import streamlit as st



base_dir = os.path.dirname(__file__)
env_path = os.path.join(base_dir, ".env")

load_dotenv(dotenv_path=env_path) 
API_KEY = os.getenv("WEATHER_API_KEY")
if not API_KEY:
    raise ValueError("WEATHER_API_KEY ist nicht gesetzt!")

location = "Heidenheim,DE"



@st.cache_data(show_spinner=False)
def load_config(config_file="parameter.json"):
    """Load the parameters from a JSON configuration file.

    Args:
        config_file (str, optional): Name of the JSON configuration file. Defaults to "parameter.json".

    Returns:
        dict: Parsed configuration data as a Python dictionary.
    """
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, config_file)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()


def fetch_weather_data(api_key, location="Heidenheim,DE"):
    """Fetch current weather data from the OpenWeatherMap API.

    Builds a request to the OpenWeatherMap REST API for the specified
    location, retrieves the weather information and returns it as a JSON dictionary.

    Args:
        api_key (str): API key for authenticating with the OpenWeatherMap API.
        location (str, optional): Location query in the form. Defaults to "Heidenheim,DE".

    Returns:
        dict | None: Weather data as a parsed JSON dictionary if successful,
        otherwise None if the request fails."""

    url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric&lang=de"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Fehler beim Abrufen der Wetterdaten: {e}")
        return None
    


def get_status(value, param_name):
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
        param_name (str): The name of the parameter to look up in config,
            e.g. "temperature_inside", "humidity_inside", "voc_index",
            "noise_level".

    Returns:
        str: One of "optimal", "warning", "critical", or "unknown"."""
    param_cfg = config["parameters"].get(param_name)
    if not param_cfg:
        return "unknown"

    min_opt = param_cfg["optimal_range"]["min"]
    max_opt = param_cfg["optimal_range"]["max"]
    tolerance = param_cfg["tolerance"]

    if min_opt <= value <= max_opt:
        return "optimal"
    elif (min_opt - tolerance) <= value <= (max_opt + tolerance):
        return "warning"
    else:
        return "critical"


def get_virtual_recommendations(api_key, location="Heidenheim,DE"):
    """Generate weather-based virtual recommendations.

    This function gets current weather data for a location, extracts temperature and
    conditions, and checks configured rules for "virtual_weather" to generate
    recommendation messages.

    Args:
        api_key (str): API key for accessing the OpenWeatherMap API.
        location (str, optional): Location query. Defaults to "Heidenheim,DE".

    Returns:
        list[dict]: A list of recommendation entries. Each entry has:
            - "parameter" (str): Always "virtual_weather".
            - "message" (str): Recommendation text or an error message if rule
              evaluation failed."""
    weather_data = fetch_weather_data(api_key, location)
    if not weather_data:
        return []
    
    weather = {
        "temp": weather_data["main"]["temp"],  
        "condition": weather_data["weather"][0]["description"].lower()
    }

    recs = []
    for rec in config["recommendations"]:
        if rec["parameter"] != "virtual_weather":
            continue

        try:
            if eval(rec["condition"], {}, {"weather": weather}):
                recs.append({
                    "parameter": "virtual_weather",
                    "message": rec["message"]
                })
        except Exception as e:
            recs.append({
                "parameter": "virtual_weather",
                "message": f"Fehler bei Wetter-Empfehlung {rec['id']}: {e}"
            })
    return recs




def get_recommendations(sensor_data):
    """Generate recommendations based on sensor data and configured rules.

    The function evaluates two types of recommendations:
      1. **Status-based**: For each parameter in `sensor_data`, if its status
         (from `get_status`) is "warning", a generic message is added.
      2. **Rule-based**: Iterates through `config["recommendations"]` and
         evaluates each condition against the current parameter value using a
         local context (value, optimal_range, tolerance). If the condition is
         true, the configured message is returned.

    Args:
        sensor_data (dict): Dictionary of parameter values, e.g.:
            {
                "temperature_inside": 22,
                "humidity_inside": 40,
                "voc_index": 120,
                "noise_level": 55
            }

    Returns:
        list[dict]: A list of recommendation objects with the structure:
            {
                "parameter": <str>,
                "message": <str>
            }
    """
    recommendations = []
    for param, value in sensor_data.items():
        status = get_status(value, param)


        if status == "warning":
            recommendations.append({
                "parameter": param,
                "message": "  Wert nähert sich kritischem Bereich an. Überwache den Parameter regelmäßig."
            })


    for rec in config["recommendations"]:
        param = rec["parameter"]
        value = sensor_data.get(param)
        if value is None:
            continue

        min_opt = config["parameters"][param]["optimal_range"]["min"]
        max_opt = config["parameters"][param]["optimal_range"]["max"]
        tolerance = config["parameters"][param]["tolerance"]

        local_context = {
            "value": value,
            "optimal_range": {
                "min": min_opt,
                "max": max_opt
            },
            "tolerance": tolerance
        }

        try:
            if eval(rec["condition"], {}, local_context):
                recommendations.append({
                    "parameter": param,
                    "message": f"  {rec['message']}"
                })
        except Exception as e:
            recommendations.append({
                "parameter": param,
                "message": f"Fehler bei Empfehlung {rec['id']}: {e}"
            })

    return recommendations


def filter_recommendations(sensor_data, weather_data, recommendations):
    """Filter recommendations based on inside vs. outside temperature.

    Removes ventilation-related ("lüften") recommendations if the outside
    temperature is higher than the inside temperature, as airing would not
    be beneficial in that case.

    Args:
        sensor_data (dict): Dictionary of indoor sensor readings, must contain
            "temperature_inside".
        weather_data (dict): Weather data from OpenWeatherMap, must include
            ["main"]["temp"] for the outside temperature.
        recommendations (list[dict]): List of recommendation objects, each
            with at least a "message" field.

    Returns:
        list[dict]: Filtered list of recommendations with unsuitable
        ventilation advice removed."""

    inside_temp = sensor_data.get("temperature_inside")
    outside_temp = weather_data["main"]["temp"]

    filtered = []
    for rec in recommendations:
        if "lüften" in rec["message"].lower() and inside_temp < outside_temp:
            continue
        filtered.append(rec)
    return filtered
