# Generated with Chat-GPT

import pytest
from datetime import datetime, timedelta, timezone

import database.sql.engine as engine
from database.sql.orm import TemperatureBronze, HumidityBronze, NoiseBronze, VocBronze

from utility import currentness  # assuming you put your function into utility/actuality.py

@pytest.fixture(autouse=True)
def setup_engine_mock():
    # Prevent DB connections
    engine.set_engine_session_factory = lambda: None
    engine._session_factory = None


def test___currentness_below_five_minutes_recent_timestamp(mocker):
    # Arrange: DB returns a timestamp within the last 5 minutes
    now = datetime.now(timezone.utc)
    recent = now - timedelta(minutes=3)

    mocker.patch(
        "utility.currentness.commit_select_scalar",
        return_value=[recent],
    )

    # Act
    result = currentness.__actuality_below_five_minutes(TemperatureBronze, arduino_id="401")

    # Assert
    assert result is True


def test___currentness_below_five_minutes_old_timestamp(mocker):
    # Arrange: DB returns a timestamp older than 5 minutes
    now = datetime.now(timezone.utc)
    old = now - timedelta(minutes=10)

    mocker.patch(
        "utility.currentness.commit_select_scalar",
        return_value=[old],
    )

    # Act
    result = currentness.__actuality_below_five_minutes(HumidityBronze, arduino_id="401")

    # Assert
    assert result is False


def test___currentness_below_five_minutes_none_returns_false(mocker):
    # Arrange: DB returns no rows
    mocker.patch(
        "utility.currentness.commit_select_scalar",
        return_value=None,
    )

    # Act
    result = currentness.__actuality_below_five_minutes(NoiseBronze, arduino_id="401")

    # Assert
    assert result is False


def test_all_sensor_below_five_minutes_all_ok(mocker):
    now = datetime.now(timezone.utc)
    recent = now - timedelta(minutes=2)

    mocker.patch(
        "utility.currentness.commit_select_scalar",
        return_value=[recent],
    )

    # Act
    result = currentness.all_sensor_below_five_minutes(arduino_id="401")

    # Assert
    assert result is True


def test_all_sensor_below_five_minutes_one_old_fails(mocker):
    now = datetime.now(timezone.utc)
    recent = now - timedelta(minutes=2)
    old = now - timedelta(minutes=20)

    # First three sensors return recent, last returns old
    mocker.patch(
        "utility.currentness.commit_select_scalar",
        side_effect=[[recent], [recent], [recent], [old]],
    )

    # Act
    result = currentness.all_sensor_below_five_minutes(arduino_id="401")

    # Assert
    assert result is False
