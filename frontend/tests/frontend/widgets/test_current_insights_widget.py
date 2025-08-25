# Generated / autofilled by ChatGPT (GPT-5 Thinking).
import pytest
import frontend.page_definition.generic_analytics.widgets.current_insights_widget as current_insights_widget

HEAT = "Heizen empfohlen, um die Raumtemperatur zu erhöhen!"
AC   = "Nutze Klimageräte oder Ventilatoren, um die Temperatur zu senken!"
OPEN_WARMER = "Öffne auch das Fenster, da die Außentemperatur aufheizt."
OPEN_COOLER = "Öffne auch das Fenster, da die Außentemperatur abkühlt."

HUMIDIFY   = "Luftbefeuchter einsetzen, um die Luftfeuchtigkeit zu erhöhen!"
DEHUMIDIFY = "Lüfte oder nutze Entfeuchter, um die Luftfeuchtigkeit zu reduzieren!"
OPEN_MORE_HUMID = "Öffne auch das Fenster, da die Außenluftfeuchtigkeit anfeuchtet."
OPEN_DRIER      = "Öffne auch das Fenster, da die Außenluftfeuchtigkeit trocknet."

VOC_ALERT = "Räume sofort lüften und mögliche Schadstoffquellen entfernen!"
NOISE_MIN = "Geräuschquellen (z.B. Personen, Geräte, Umgebungsgeräusche) minimieren!"

@pytest.fixture(autouse=True)
def reset_globals():
    """
    Bypass streamlit caching!
    """
    current_insights_widget.st.cache_data.clear()

def test_temp_below_min_adds_heat_and_open_when_outside_warmer(mocker):
    mocker.patch("frontend.page_definition.generic_analytics.widgets.utils.fetch_weather_data", return_value={"temperature": 19.0, "humidity": 50})
    res = current_insights_widget._get_recommendation_texts(
        sensor_specifier="temperature_inside",
        value=18.0,
        optimal_range={"min": 20, "max": 24},
        recommendation_tolerance=0.5,
    )
    assert res == [HEAT, OPEN_WARMER]


def test_temp_above_max_adds_ac_and_open_when_outside_cooler(mocker):
    mocker.patch("frontend.page_definition.generic_analytics.widgets.utils.fetch_weather_data", return_value={"temperature": 20.0, "humidity": 50})
    res = current_insights_widget._get_recommendation_texts(
        sensor_specifier="temperature_inside",
        value=26.0,
        optimal_range={"min": 20, "max": 24},
        recommendation_tolerance=0.5,
    )
    assert res == [AC, OPEN_COOLER]


def test_temp_within_tolerance_no_recommendation(mocker):
    mocker.patch("frontend.page_definition.generic_analytics.widgets.utils.fetch_weather_data", return_value={"temperature": 100.0, "humidity": 0})
    res = current_insights_widget._get_recommendation_texts(
        sensor_specifier="temperature_inside",
        value=20.3,
        optimal_range={"min": 20, "max": 24},
        recommendation_tolerance=0.5,
    )
    assert res == []


def test_humidity_below_min_adds_humidify_and_open_when_outside_more_humid(mocker):
    mocker.patch("frontend.page_definition.generic_analytics.widgets.utils.fetch_weather_data", return_value={"temperature": 10.0, "humidity": 55})
    res = current_insights_widget._get_recommendation_texts(
        sensor_specifier="humidity_inside",
        value=30.0,
        optimal_range={"min": 40, "max": 60},
        recommendation_tolerance=3.0,
    )
    assert res == [HUMIDIFY, OPEN_MORE_HUMID]


def test_humidity_above_max_adds_dehumidify_and_open_when_outside_drier(mocker):
    mocker.patch("frontend.page_definition.generic_analytics.widgets.utils.fetch_weather_data", return_value={"temperature": 10.0, "humidity": 40})
    res = current_insights_widget._get_recommendation_texts(
        sensor_specifier="humidity_inside",
        value=70.0,
        optimal_range={"min": 40, "max": 60},
        recommendation_tolerance=3.0,
    )
    assert res == [DEHUMIDIFY, OPEN_DRIER]


def test_voc_above_max_triggers_alert(mocker):
    mocker.patch("frontend.page_definition.generic_analytics.widgets.utils.fetch_weather_data", return_value={"temperature": 0.0, "humidity": 0.0})
    res = current_insights_widget._get_recommendation_texts(
        sensor_specifier="voc_index",
        value=110.0,
        optimal_range={"min": 0, "max": 100},
        recommendation_tolerance=5.0,
    )
    assert res == [VOC_ALERT]


def test_noise_above_max_triggers_minimization(mocker):
    mocker.patch("frontend.page_definition.generic_analytics.widgets.utils.fetch_weather_data", return_value={"temperature": 0.0, "humidity": 0.0})
    res = current_insights_widget._get_recommendation_texts(
        sensor_specifier="noise_level",
        value=75.0,
        optimal_range={"min": 0, "max": 60},
        recommendation_tolerance=5.0,
    )
    assert res == [NOISE_MIN]


def test_all_sensors_no_action_when_exactly_on_edges_with_tolerance(mocker):
    """Kein Vorschlag, wenn value im inklusiven Toleranzbereich liegt:
       min - tol <= value <= max + tol
    """
    mocker.patch("frontend.page_definition.generic_analytics.widgets.utils.fetch_weather_data", return_value={"temperature": 5.0, "humidity": 50.0})

    # Temperature lower violation
    assert current_insights_widget._get_recommendation_texts("temperature_inside", 19.5, {"min": 20, "max": 24}, 0.5) == []
    # Temperaure upper violation
    assert current_insights_widget._get_recommendation_texts("temperature_inside", 24.5, {"min": 20, "max": 24}, 0.5) == []

    # Hum Edge Cases
    assert current_insights_widget._get_recommendation_texts("humidity_inside", 37.0, {"min": 40, "max": 60}, 3.0) == []
    assert current_insights_widget._get_recommendation_texts("humidity_inside", 63.0, {"min": 40, "max": 60}, 3.0) == []

    # Upper violation
    assert current_insights_widget._get_recommendation_texts("voc_index", 105.0, {"min": 0, "max": 100}, 5.0) == []
    assert current_insights_widget._get_recommendation_texts("noise_level", 65.0, {"min": 0, "max": 60}, 5.0) == []
