from dotenv import load_dotenv
import json
import os
import requests


base_dir = os.path.dirname(__file__)
env_path = os.path.join(base_dir, ".env")

load_dotenv(dotenv_path=env_path) 
API_KEY = os.getenv("WEATHER_API_KEY")
if not API_KEY:
    raise ValueError("WEATHER_API_KEY ist nicht gesetzt!")

location = "Heidenheim,DE"



def load_config(config_file="parameter.json"):
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, config_file)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()


def fetch_weather_data(api_key, location="Heidenheim,DE"):
    

    url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric&lang=de"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Fehler beim Abrufen der Wetterdaten: {e}")
        return None
    


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


def get_virtual_recommendations(api_key, location="Heidenheim,DE"):
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

    inside_temp = sensor_data.get("temperature_inside")
    outside_temp = weather_data["main"]["temp"]

    filtered = []
    for rec in recommendations:
        if "lüften" in rec["message"].lower() and inside_temp < outside_temp:
            continue
        filtered.append(rec)
    return filtered
