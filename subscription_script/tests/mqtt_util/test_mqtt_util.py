import pytest
from unittest import mock
import subscription_script.mqtt_util as mqtt_util
from subscription_script.mqtt_util import on_message



@pytest.fixture(autouse=True)
def setup_sequences():
    mqtt_util._temp_seq = 0
    mqtt_util._hum_seq = 0
    mqtt_util._voc_seq = 0
    mqtt_util._noise_seq = 0


def test_deserialization_error(mocker):
    """
    Tests that the function does not re-initialize the engine and
    session factory if they already exist.
    """
    # --- Arrange ---
    mock_msg = mock.MagicMock()

    mock_json = mocker.patch("json.loads")
    mock_json.side_effect = Exception("Test exception")

    mock_logging = mocker.patch("logging.critical")

    # --- Act ---
    on_message(None, None, mock_msg)

    # --- Assert ---
    mock_logging.assert_called()


def test_datatype_mismatch_in_payload(mocker):
    """
    Tests that the function does not re-initialize the engine and
    session factory if they already exist.
    """
    # --- Arrange ---
    mock_msg = mock.MagicMock()

    mock_json = mocker.patch(
        "json.loads",
        return_value={
            "timestamp": "1753098733",
            # Mismatch
            "value": "23.45",
            "sequence": 123,
            "meta": {"firmware": "v1.2.3", "startup": "1753098730"},
        },
    )

    mock_logging = mocker.patch("logging.critical")

    # --- Act ---
    on_message(None, None, mock_msg)

    # --- Assert ---
    mock_logging.assert_called()


def test_seq_interrupt(mocker):
    """
    Tests that the function does not re-initialize the engine and
    session factory if they already exist.
    """
    # Temp Test
    # --- Arrange ---
    mock_msg = mock.MagicMock()
    mock_msg.topic = "dhbw/ai/si2023/6/temp/429"
    
    payload = {
        "timestamp": "1753098733",
        "value": [24.54, 23.56],
        "sequence": 2,
        "meta": {"firmware": "v1.2.3", "startup": "1753098730"},
    }

    mocker.patch(
        "json.loads",
        return_value=payload,
    )

    mock_logging = mocker.patch("logging.warn")

    # --- Act ---
    on_message(None, None, mock_msg)

    # --- Assert ---
    mock_logging.assert_called()
    assert mqtt_util._temp_seq == payload["sequence"]

    # ---------

    # Humidity Test
    # --- Arrange ---
    mock_msg = mock.MagicMock()
    mock_msg.topic = "dhbw/ai/si2023/6/hum/429"
    
    payload = {
        "timestamp": "1753098733",
        "value": [24.54, 23.56],
        "sequence": 2,
        "meta": {"firmware": "v1.2.3", "startup": "1753098730"},
    }

    mocker.patch(
        "json.loads",
        return_value=payload,
    )

    mock_logging = mocker.patch("logging.warn")

    # --- Act ---
    on_message(None, None, mock_msg)

    # --- Assert ---
    mock_logging.assert_called()
    assert mqtt_util._hum_seq == payload["sequence"]

    # ---------

    # Co2 Test
    # --- Arrange ---
    mock_msg = mock.MagicMock()
    mock_msg.topic = "dhbw/ai/si2023/6/co2/429"
    
    payload = {
        "timestamp": "1753098733",
        "value": [24.54, 23.56],
        "sequence": 2,
        "meta": {"firmware": "v1.2.3", "startup": "1753098730"},
    }

    mocker.patch(
        "json.loads",
        return_value=payload,
    )

    mock_logging = mocker.patch("logging.warn")

    # --- Act ---
    on_message(None, None, mock_msg)

    # --- Assert ---
    mock_logging.assert_called()
    assert mqtt_util._voc_seq == payload["sequence"]

    # ---------

    # Mic Test
    # --- Arrange ---
    mock_msg = mock.MagicMock()
    mock_msg.topic = "dhbw/ai/si2023/6/mic/429"
    
    payload = {
        "timestamp": "1753098733",
        "value": [24.54, 23.56],
        "sequence": 2,
        "meta": {"firmware": "v1.2.3", "startup": "1753098730"},
    }

    mocker.patch(
        "json.loads",
        return_value=payload,
    )

    mock_logging = mocker.patch("logging.warn")

    # --- Act ---
    on_message(None, None, mock_msg)

    # --- Assert ---
    mock_logging.assert_called()
    assert mqtt_util._noise_seq == payload["sequence"]


def test_insert(mocker):
    """
    Tests that the function does not re-initialize the engine and
    session factory if they already exist.
    """
    # Temp Test
    # --- Arrange ---
    mock_msg = mock.MagicMock()
    mock_msg.topic = "dhbw/ai/si2023/6/temp/429"
    
    payload = {
        "timestamp": 1753098733,
        "value": [24.54, 23.56],
        "sequence": 1,
        "meta": {"device_id": 303},
    }

    mocker.patch(
        "json.loads",
        return_value=payload,
    )

    mock_insert = mocker.patch(
        "subscription_script.mqtt_util.insert_into_db"
    )

    # --- Act ---
    on_message(None, None, mock_msg)

    # --- Assert ---
    mock_insert.assert_called_once()

    # ---------

    # Humidity Test
    # --- Arrange ---
    mock_msg = mock.MagicMock()
    mock_msg.topic = "dhbw/ai/si2023/6/hum/429"
    
    payload = {
        "timestamp": 1753098733,
        "value": [24.54, 23.56],
        "sequence": 1,
        "meta": {"device_id": 303},
    }

    mocker.patch(
        "json.loads",
        return_value=payload,
    )

    mock_insert = mocker.patch(
        "subscription_script.mqtt_util.insert_into_db"
    )

    # --- Act ---
    on_message(None, None, mock_msg)

    # --- Assert ---
    mock_insert.assert_called_once()

    # ---------

    # Co2 Test
    # --- Arrange ---
    mock_msg = mock.MagicMock()
    mock_msg.topic = "dhbw/ai/si2023/6/co2/429"
    
    payload = {
        "timestamp": 1753098733,
        "value": [24.54, 23.56],
        "sequence": 1,
        "meta": {"device_id": 303},
    }

    mocker.patch(
        "json.loads",
        return_value=payload,
    )

    mock_insert = mocker.patch(
        "subscription_script.mqtt_util.insert_into_db"
    )

    # --- Act ---
    on_message(None, None, mock_msg)

    # --- Assert ---
    mock_insert.assert_called_once()

    # ---------

    # Mic Test
    # --- Arrange ---
    mock_msg = mock.MagicMock()
    mock_msg.topic = "dhbw/ai/si2023/6/mic/429"
    
    payload = {
        "timestamp": 1753098733,
        "value": [24.54, 23.56],
        "sequence": 1,
        "meta": {"device_id": 303},
    }

    mocker.patch(
        "json.loads",
        return_value=payload,
    )

    mock_insert = mocker.patch(
        "subscription_script.mqtt_util.insert_into_db"
    )

    # --- Act ---
    on_message(None, None, mock_msg)

    # --- Assert ---
    mock_insert.assert_called_once()