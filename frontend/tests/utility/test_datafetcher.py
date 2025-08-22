# Generated / autofilled by ChatGPT (GPT-5 Thinking) and HEAVILY... corrected by a human.

import pytest
from unittest import mock
from datetime import datetime, timezone
import pandas as pd

from utility.datafetcher import DataFetcher
from database.sql import engine
from database.orm import Temperature, Humidity, Voc, Noise, SensorType


@pytest.fixture(autouse=True)
def setup_sequences():
    # Mock DB engine/session factory so no real connection is needed
    engine.set_engine_session_factory = mock.MagicMock(return_value=None)
    engine._session_factory = mock.MagicMock()


def test_get_unique_arduino_ids(mocker):
    side_effect_return = [["401"], ["402"], ["403"], ["404"]]
    mocker.patch(
        "utility.datafetcher.commit_select_scalar",
        side_effect=side_effect_return,
    )

    result = DataFetcher().get_unique_arduino_ids()

    assert result[SensorType.TEMPERATURE] == side_effect_return[0]
    assert result[SensorType.HUMIDITY] == side_effect_return[1]
    assert result[SensorType.VOC] == side_effect_return[2]
    assert result[SensorType.NOISE] == side_effect_return[3]


def test_get_newest_bucket_populated(mocker):
    # Arrange: create one "latest" record per sensor type
    t = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
    temp = Temperature(bucket_time=t, arduino_id="401", avg_value_in_bucket=21.5)
    hum = Humidity(bucket_time=t, arduino_id="401", avg_value_in_bucket=45.2)
    voc = Voc(bucket_time=t, arduino_id="401", avg_value_in_bucket=123.0)
    noise = Noise(bucket_time=t, arduino_id="401", avg_value_in_bucket=33.3)

    mocker.patch(
        "utility.datafetcher.commit_select_scalar",
        side_effect=[[temp], [hum], [voc], [noise]],
    )

    # Act
    res_temp, res_hum, res_voc, res_noise = DataFetcher().get_newest_bucket("401")

    # Assert: values are correctly returned as manual ORM objects
    assert isinstance(res_temp, Temperature)
    assert isinstance(res_hum, Humidity)
    assert isinstance(res_voc, Voc)
    assert isinstance(res_noise, Noise)

    assert (res_temp.bucket_time, res_temp.arduino_id, res_temp.avg_value_in_bucket) == (
        t,
        "401",
        21.5,
    )
    assert (res_hum.bucket_time, res_hum.arduino_id, res_hum.avg_value_in_bucket) == (
        t,
        "401",
        45.2,
    )
    assert (res_voc.bucket_time, res_voc.arduino_id, res_voc.avg_value_in_bucket) == (
        t,
        "401",
        123.0,
    )
    assert (res_noise.bucket_time, res_noise.arduino_id, res_noise.avg_value_in_bucket) == (
        t,
        "401",
        33.3,
    )


def test_get_newest_bucket_empty_lists_return_none_objects(mocker):
    # Arrange: DB returns no rows for all sensor types
    mocker.patch(
        "utility.datafetcher.commit_select_scalar",
        side_effect=[[], [], [], []],
    )

    # Act
    res_temp, res_hum, res_voc, res_noise = DataFetcher().get_newest_bucket("401")

    # Assert: default ORM objects with None fields are created
    for obj in (res_temp, res_hum, res_voc, res_noise):
        assert obj.bucket_time is None
        assert obj.arduino_id is None
        assert obj.avg_value_in_bucket is None


def test_get_bucket_by_t_interval_with_rows_and_datetime_conversion(mocker):
    # Arrange
    df_start = datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc)
    df_end = datetime(2025, 1, 2, 0, 0, tzinfo=timezone.utc)

    # Simulate DB rows as returned by commit_select (tuples)
    # Bucket timestamps are strings -> should be converted to datetime
    rows = [
        ("2025-01-01T18:00:00+00:00", 200.0),
        ("2025-01-01T12:00:00+00:00", 180.5),
    ]
    mocker.patch("utility.datafetcher.commit_select", return_value=rows)

    # Act
    df = DataFetcher().get_bucket_by_t_interval(
        SensorType.VOC, "401", df_start, df_end
    )

    # Assert: structure, values, and datetime conversion
    assert list(df.columns) == ["bucket_time", "avg_value_in_bucket"]
    assert len(df) == 2
    assert pd.api.types.is_datetime64_any_dtype(df["bucket_time"])
    assert df.iloc[0]["avg_value_in_bucket"] == 200.0
    assert df.iloc[1]["avg_value_in_bucket"] == 180.5
    assert df.iloc[0]["bucket_time"].isoformat() == "2025-01-01T18:00:00+00:00"
    assert df.iloc[1]["bucket_time"].isoformat() == "2025-01-01T12:00:00+00:00"


def test_get_bucket_by_t_interval_empty_returns_empty_df(mocker):
    # Arrange
    df_start = datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc)
    df_end = datetime(2025, 1, 2, 0, 0, tzinfo=timezone.utc)

    mocker.patch("utility.datafetcher.commit_select", return_value=[])

    # Act
    df = DataFetcher().get_bucket_by_t_interval(
        SensorType.NOISE, "401", df_start, df_end
    )

    # Assert: empty DataFrame with correct columns
    assert list(df.columns) == ["bucket_time", "avg_value_in_bucket"]
    assert df.empty
