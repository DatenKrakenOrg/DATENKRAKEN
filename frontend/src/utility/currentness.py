from dotenv import load_dotenv
load_dotenv()
from database.sql.engine import commit_select_scalar, set_engine_session_factory
from sqlalchemy.sql import select
from bronze_sql.orm import Humidity, Noise, Temperature, Voc
from datetime import datetime, timezone

set_engine_session_factory()

def __actuality_below_five_minutes(orm_table):
    now = datetime.now(timezone.utc)

    stmt_temp = (
        select(orm_table.time)
        .where(orm_table.time <= now)  # ignore future timestamps (2036 incident)
        .order_by(orm_table.time.desc())
        .limit(1)
    )
    result = commit_select_scalar(stmt_temp)

    if not result:
        print("No valid temperature data found.")
        return False

    last_time_stamp = result[0]

    if last_time_stamp.tzinfo is None:
        last_time_stamp = last_time_stamp.replace(tzinfo=timezone.utc)
    else:
        last_time_stamp = last_time_stamp.astimezone(timezone.utc)

    diff_minutes = (now - last_time_stamp).total_seconds() / 60

    # print(f"Now: {now}")
    # print(f"Last valid timestamp: {last_time_stamp}")
    # print(f"Time difference: {diff_minutes:.2f} minutes")

    return diff_minutes <= 5

def all_sensor_below_five_minutes():
    flag = True
    for orm in [Temperature, Noise, Humidity, Voc]:
        flag &=  __actuality_below_five_minutes(orm)
    return flag
