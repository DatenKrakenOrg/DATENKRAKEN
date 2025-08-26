import streamlit as st
import os
import json
from typing import List, Dict
from utility.datafetcher import DataFetcher

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

def get_rooms_data(unique_arduino_ids: List[str], fetcher: DataFetcher) -> List[dict]:
    """Gets data of newest datapoint for all rooms within the database gold layer

    Args:
        unique_arduino_ids (List[str]): List of all arduinos_ids
        fetcher (DataFetcher): DataFetcher used to fetch database

    Returns:
        List[dict]: List of dictionaries containing keys: name: str (arduino_id of room), data: Dict[str, float] (newest sensor value of room)
    """
    all_rooms_data = []
    for room in unique_arduino_ids:
        all_rooms_data.append(get_single_room_data(room, fetcher))
    return all_rooms_data


def get_single_room_data(arduino_id: str, fetcher: DataFetcher) -> Dict[str, float]:
    """Gets data of newest datapoint for a single room within the database gold layer

    Args:
        arduino_id (List[str]): Arduino id of room
        fetcher (DataFetcher): DataFetcher used to fetch database

    Returns:
        Dict[str, float]: List of dictionaries containing keys: name: str (arduino_id of room), data: Dict[str, float] (newest sensor value of room)
    """
    room_data = fetcher.get_newest_bucket(arduino_id)
    return {
        "name": arduino_id,
        "data": {
            "temperature_inside": round(room_data[0].avg_value_in_bucket, 2) if room_data[0].avg_value_in_bucket else None,
            "humidity_inside": round(room_data[1].avg_value_in_bucket, 2) if room_data[1].avg_value_in_bucket else None,
            "voc_index": round(room_data[2].avg_value_in_bucket, 2) if room_data[2].avg_value_in_bucket else None,
            "noise_level": round(room_data[3].avg_value_in_bucket, 2) if room_data[3].avg_value_in_bucket else None,
        }
    }

