import pytest
from unittest import mock
from frontend.utils import load_config, get_rooms_data, get_single_room_data
from database.orm import Temperature, Humidity, Voc, Noise
from datetime import datetime
import frontend.utils as utils


@pytest.fixture(autouse=True)
def reset_globals():
    """
    Bypass streamlit caching!
    """
    utils.st.cache_data.clear()


def test_get_rooms_data_no_ids():
    # --- Arrange ---
    unique_arduino_ids = []
    fetcher = mock.MagicMock()

    # --- Act ---
    result = get_rooms_data(unique_arduino_ids, fetcher)

    # --- Assert ---
    fetcher.assert_not_called()

    assert len(result) == 0


def test_get_rooms_data(mocker):
    # --- Arrange ---
    unique_arduino_ids = ["301"]
    fetcher = mock.MagicMock()
    room_data_of_301 = {
        "name": "301",
        "data": {
            "temperature_inside": 10.0,
            "humidity_inside": 10.0,
            "voc_index": 10.0,
            "noise_level": 10.0,
        },
    }

    mocker.patch(
        "frontend.utils.get_single_room_data",
        return_value = room_data_of_301,
    )
    # --- Act ---
    result = get_rooms_data(unique_arduino_ids, fetcher)

    # --- Assert ---
    assert len(result) == 1
    assert result[0] == room_data_of_301

def test_single_room_data_no_data(mocker):
    # --- Arrange ---
    arduino_id = "301"
    room_data_fetcher = (
            Temperature(bucket_time=None,
                arduino_id=None,
                avg_value_in_bucket=None,
            ),
            Humidity(
                bucket_time=None,
                arduino_id=None,
                avg_value_in_bucket=None,
            ),
            Voc(
                bucket_time=None,
                arduino_id=None,
                avg_value_in_bucket=None,
            ),
            Noise(
                bucket_time=None,
                arduino_id=None,
                avg_value_in_bucket=None,
            ),
        )
    fetcher = mock.MagicMock()
    fetcher.get_newest_bucket.return_value = room_data_fetcher
    room_data= {
        "name": arduino_id,
        "data": {
            "temperature_inside": None,
            "humidity_inside": None,
            "voc_index": None,
            "noise_level": None,
        }
    }
    
    
    # --- Act ---
    result = get_single_room_data(arduino_id, fetcher)

    # --- Assert ---
    fetcher.get_newest_bucket.assert_called_once()
    assert result == room_data

def test_single_room_data_all_fields_filled(mocker):
    # --- Arrange ---
    arduino_id = "301"
    now = datetime(2025, 1, 1, 12, 0, 0)

    room_data_fetcher = (
        Temperature(bucket_time=now, arduino_id=arduino_id, avg_value_in_bucket=21.2349),
        Humidity(bucket_time=now, arduino_id=arduino_id, avg_value_in_bucket=45.6789),
        Voc(bucket_time=now, arduino_id=arduino_id, avg_value_in_bucket=120.9876),
        Noise(bucket_time=now, arduino_id=arduino_id, avg_value_in_bucket=33.3333),
    )

    fetcher = mocker.Mock()
    fetcher.get_newest_bucket.return_value = room_data_fetcher

    expected = {
        "name": arduino_id,
        "data": {
            "temperature_inside": 21.23,
            "humidity_inside": 45.68,
            "voc_index": 120.99,
            "noise_level": 33.33,
        },
    }

    # --- Act ---
    result = get_single_room_data(arduino_id, fetcher)

    # --- Assert ---
    fetcher.get_newest_bucket.assert_called_once_with(arduino_id)
    assert result == expected



def test_load_config(mocker):
    # --- Arrange ---
    mock_dirname = mocker.patch(
        "frontend.utils.os.path.dirname", return_value="/app/directory"
    )
    mock_join = mocker.patch(
        "frontend.utils.os.path.join", return_value="/app/directory/parameter.json"
    )
    mock_open = mocker.patch(
        "builtins.open", mocker.mock_open(read_data='{"key": "value", "number": 42}')
    )

    # --- Act ---
    result = load_config()

    # --- Assert ---
    mock_dirname.assert_called_once()
    mock_join.assert_called_once_with("/app/directory", "parameter.json")
    mock_open.assert_called_once_with(
        "/app/directory/parameter.json", "r", encoding="utf-8"
    )
    assert result == {"key": "value", "number": 42}
