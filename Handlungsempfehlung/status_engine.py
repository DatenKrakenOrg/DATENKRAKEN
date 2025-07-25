import json
import os
import requests

API_KEY = "756c317560b3496480d121915252507"

# Config-Datei laden
def load_config(config_file="parameter.json"):
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, config_file)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()


def fetch_weather_data(api_key, location="Heidenheim,DE"):
    """
    Holt Wetterdaten von WeatherAPI.com (oder OpenWeatherMap).
    """
    url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={location}&days=1&aqi=yes"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Fehler beim Abrufen der Wetterdaten: {e}")
        return None
    

# Berechne den Status für einen einzelnen Wert
def get_status(value, param_name):
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


def get_virtual_recommendations(api_key, location="Berlin,DE"):
    weather_data = fetch_weather_data(api_key, location)
    if not weather_data:
        return []

    weather = {
        "temp": weather_data["current"]["temp_c"],
        "condition": weather_data["current"]["condition"]["text"].lower()
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


# Gibt Handlungsempfehlungen und Warnungen zurück
def get_recommendations(sensor_data):
    recommendations = []
    for param, value in sensor_data.items():
        status = get_status(value, param)

        # Warnung hinzufügen, falls der Wert im Warnbereich liegt
        if status == "warning":
            recommendations.append({
                "parameter": param,
                "message": "  Wert nähert sich kritischem Bereich an. Überwache den Parameter regelmäßig."
            })

    # Kritische Empfehlungen hinzufügen
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
    """
    Filtert Empfehlungen, die unter bestimmten Bedingungen nicht passen.
    Beispiel: 'Lüften' wird unterdrückt, wenn Innen-Temp < Außen-Temp.
    """
    inside_temp = sensor_data.get("temperature_inside")
    outside_temp = weather_data["current"]["temp_c"]

    filtered = []
    for rec in recommendations:
        # Lüften Empfehlung blocken wenn Innen-Temp < Außen-Temp
        if "lüften" in rec["message"].lower() and inside_temp < outside_temp:
            continue
        filtered.append(rec)
    return filtered