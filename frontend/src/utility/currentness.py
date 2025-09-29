from database.sql.engine import commit_select_scalar, set_engine_session_factory
from sqlalchemy.sql import select
from database.sql.orm import HumidityBronze, NoiseBronze, TemperatureBronze, VocBronze
from datetime import datetime, timezone

set_engine_session_factory()

def __actuality_below_five_minutes(orm_table, arduino_id: int) -> bool:
    """Check if the latest timestamp for a given arduino_id is within 5 minutes."""
    now = datetime.now(timezone.utc)

    stmt = (
        select(orm_table.time)
        .where(orm_table.arduino_id == arduino_id)
        .order_by(orm_table.time.desc())
        .limit(1)
    )

    result = commit_select_scalar(stmt)

    if not result:
        print(f"No valid data found for Arduino {arduino_id} in {orm_table.__tablename__}")
        return False

    last_time_stamp = result[0]

    # Normalize timezone
    if last_time_stamp.tzinfo is None:
        last_time_stamp = last_time_stamp.replace(tzinfo=timezone.utc)
    else:
        last_time_stamp = last_time_stamp.astimezone(timezone.utc)

    #new changes Consider clock skew: treat small future offsets as fresh
    diff_minutes = abs((now - last_time_stamp).total_seconds()) / 60
    return diff_minutes <= 5


def temperature_below_five_minutes(arduino_id: int) -> bool:
    return __actuality_below_five_minutes(TemperatureBronze, arduino_id)


def noise_below_five_minutes(arduino_id: int) -> bool:
    return __actuality_below_five_minutes(NoiseBronze, arduino_id)


def humidity_below_five_minutes(arduino_id: int) -> bool:
    return __actuality_below_five_minutes(HumidityBronze, arduino_id)


def voc_below_five_minutes(arduino_id: int) -> bool:
    return __actuality_below_five_minutes(VocBronze, arduino_id)


def all_sensor_below_five_minutes(arduino_id: int) -> bool:
    return (
        temperature_below_five_minutes(arduino_id)
        and noise_below_five_minutes(arduino_id)
        and humidity_below_five_minutes(arduino_id)
        and voc_below_five_minutes(arduino_id)
    )
