# Generated / autofilled by ChatGPT (GPT-5 Thinking).
import pytest
from unittest import mock
import frontend.page_definition.generic_analytics.widgets.utils as utils

@pytest.fixture(autouse=True)
def reset_globals():
    """
    Bypass streamlit caching!
    """
    utils.st.cache_data.clear()


def test_sensor_specifier_type_mapping_integrity():
    from database.orm import SensorType

    assert utils.sensor_specifier_type_dict == {
        "temperature_inside": SensorType.TEMPERATURE,
        "humidity_inside": SensorType.HUMIDITY,
        "voc_index": SensorType.VOC,
        "noise_level": SensorType.NOISE,
    }


def test_sensor_data_language_dict_contains_expected_keys():
    assert utils.sensor_data_language_dict["Temperatur"] == "temperature_inside"
    assert utils.sensor_data_language_dict["Luftfeuchtigkeit"] == "humidity_inside"
    assert utils.sensor_data_language_dict["Luftqualität (Voc-Index)"] == "voc_index"
    assert utils.sensor_data_language_dict["Lautstärke"] == "noise_level"


def test_sensorstatus_enum_values():
    assert utils.SensorStatus.OPTIMAL.value == ("green", "Optimal")
    assert utils.SensorStatus.WARNING.value == ("orange", "Suboptimal")
    assert utils.SensorStatus.CRITICAL.value == ("red", "Kritisch")


def test_get_status_optimal_warning_critical_boundaries():
    cfg = {
        "parameters": {
            "temperature_inside": {
                "optimal_range": {"min": 20, "max": 24},
                "tolerance": 0.5,
            }
        }
    }

    assert utils.get_status(20.0, "temperature_inside", cfg) == utils.SensorStatus.OPTIMAL
    assert utils.get_status(22.0, "temperature_inside", cfg) == utils.SensorStatus.OPTIMAL
    assert utils.get_status(24.0, "temperature_inside", cfg) == utils.SensorStatus.OPTIMAL

    assert utils.get_status(19.5, "temperature_inside", cfg) == utils.SensorStatus.WARNING
    assert utils.get_status(24.5, "temperature_inside", cfg) == utils.SensorStatus.WARNING

    assert utils.get_status(19.49, "temperature_inside", cfg) == utils.SensorStatus.CRITICAL
    assert utils.get_status(24.51, "temperature_inside", cfg) == utils.SensorStatus.CRITICAL


def test_get_status_unknown_when_param_empty():
    cfg = {"parameters": {"humidity_inside": None}}
    assert utils.get_status(50, "humidity_inside", cfg) == "unknown"


def test_get_status_raises_keyerror_when_param_missing():
    cfg = {"parameters": {}}
    with pytest.raises(KeyError):
        utils.get_status(0, "voc_index", cfg)


def test_fetch_weather_data_success_builds_url_and_parses(monkeypatch, mocker):
    # --- Arrange ---
    monkeypatch.setenv("LOCATION", "Heidenheim,de")
    monkeypatch.setenv("WEATHER_API_KEY", "APIKEY123")

    fake_resp = mock.MagicMock()
    fake_resp.raise_for_status.return_value = None
    fake_resp.json.return_value = {"main": {"temp": 18.7, "humidity": 65}}

    get_mock = mocker.patch(
        "frontend.page_definition.generic_analytics.widgets.utils.requests.get",
        return_value=fake_resp,
    )

    # --- Act ---
    result = utils.fetch_weather_data()

    # --- Assert ---
    expected_url = (
        "https://api.openweathermap.org/data/2.5/weather?"
        "q=Heidenheim,de&appid=APIKEY123&units=metric&lang=de"
    )
    get_mock.assert_called_once_with(expected_url)
    assert result == {"temperature": 18.7, "humidity": 65}


def test_fetch_weather_data_http_error_returns_none(monkeypatch, mocker):
    monkeypatch.setenv("LOCATION", "Heidenheim,de")
    monkeypatch.setenv("WEATHER_API_KEY", "BADKEY")

    fake_resp = mock.MagicMock()
    fake_resp.raise_for_status.side_effect = Exception("HTTP 401")

    mocker.patch(
        "frontend.page_definition.generic_analytics.widgets.utils.requests.get",
        return_value=fake_resp,
    )

    assert utils.fetch_weather_data() is None


def test_fetch_weather_data_missing_keys_returns_none(monkeypatch, mocker):
    """
    Wenn die API-Antwort 'main' oder die Keys nicht enthält, soll der try/except -> None liefern.
    """
    monkeypatch.setenv("LOCATION", "Somewhere")
    monkeypatch.setenv("WEATHER_API_KEY", "KEY")

    fake_resp = mock.MagicMock()
    fake_resp.raise_for_status.return_value = None
    fake_resp.json.return_value = {"not_main": {}}

    mocker.patch(
        "frontend.page_definition.generic_analytics.widgets.utils.requests.get",
        return_value=fake_resp,
    )

    assert utils.fetch_weather_data() is None
