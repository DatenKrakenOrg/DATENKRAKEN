import pytest
from unittest import mock
import subscription_script.mqtt_util as mqtt_util
from subscription_script.mqtt_util import on_message



@pytest.fixture(autouse=True)
def setup_sequences():
    """
    Reset sequence numbers
    """
    mqtt_util._temp_seq = 0
    mqtt_util._hum_seq = 0
    mqtt_util._voc_seq = 0
    mqtt_util._noise_seq = 0


def test_deserialization_error(mocker):
    """
    Tests whether a error is logged whenever a deserialization error occurs on the payload
    """
    # --- Arrange ---
    mock_msg = mock.MagicMock()
    mock_json = mocker.patch("json.loads")
    mock_json.side_effect = Exception("Test exception")
    mock_logging = mocker.patch("logging.critical")
    on_message(None, None, mock_msg)
    mock_logging.assert_called()


def test_datatype_mismatch_in_payload(mocker):
    mock_msg = mock.MagicMock()

    mocker.patch(
        "json.loads",
        return_value={
            "timestamp": 1753098733,
            # Mismatch
            "value": "23.45",
            "sequence": 123,
            "meta": {"device_id": 303},
        },
    )

    mock_logging = mocker.patch("logging.critical")

    # --- Act ---
    on_message(None, None, mock_msg)

    # --- Assert ---
    mock_logging.assert_called()


@pytest.mark.parametrize(
    "topic, seq_attr, baseline_val, anomaly_val",
    [
        ("dhbw/ai/si2023/6/temp/429", "_temp_seq", [22.34], [22.90]),
        ("dhbw/ai/si2023/6/hum/429", "_hum_seq", [45.2], [46.0]),
        ("dhbw/ai/si2023/6/co2/429", "_voc_seq", [612], [1200]), 
        ("dhbw/ai/si2023/6/mic/429", "_noise_seq", [38.2, 39.1], [55.7]),
    ],
)

def test_sequence_baseline_and_gap(mocker, topic, seq_attr, baseline_val, anomaly_val):
    """First message sets baseline (info only), second with gap triggers warning + sequence alert."""
    # Prevent real DB insert
    mocker.patch("subscription_script.mqtt_util.insert_into_db")

    # Reset the specific sequence counter explicitly
    setattr(mqtt_util, seq_attr, 0)

    mock_msg = mock.MagicMock()
    mock_msg.topic = topic

    baseline_payload = {
        "timestamp": 1753098733,
        "value": baseline_val,
        "sequence": 100,
        "meta": {"device_id": 303},
    }
    mocker.patch("json.loads", return_value=baseline_payload)
    info = mocker.patch("logging.info")
    warn = mocker.patch("logging.warning")
    alert = mocker.patch("subscription_script.mqtt_util.send_sequence_alert")
    on_message(None, None, mock_msg)
    info.assert_called()
    warn.assert_not_called()
    alert.assert_not_called()
    assert getattr(mqtt_util, seq_attr) == 100

    anomaly_payload = {
        "timestamp": 1753098734,
        "value": anomaly_val,
        "sequence": 108,  # expected would be 101 -> gap
        "meta": {"device_id": 303},
    }
    mocker.patch("json.loads", return_value=anomaly_payload)
    info.reset_mock()
    on_message(None, None, mock_msg)
    warn.assert_called_once()
    alert.assert_called_once()
    assert getattr(mqtt_util, seq_attr) == 108


def test_insert(mocker):
    """
    Tests whether a correct insert is possible.
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
    mocker.patch("json.loads", return_value=payload)
    mock_insert = mocker.patch("subscription_script.mqtt_util.insert_into_db")
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