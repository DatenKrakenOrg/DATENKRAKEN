import os
from database.orm import SensorType
from datetime import datetime

if os.getenv("ENVIRONMENT") != "PROD":
    from dotenv import load_dotenv
    load_dotenv()

from utility.datafetcher import DataFetcher
print(os.getenv("DB_HOST"))
df = DataFetcher().get_bucket_by_t_interval(
    SensorType.TEMPERATURE,
    "401",
    datetime(2024, 8, 5),
    datetime.now())

print(df["bucket_time"].min())
print(df["bucket_time"].max())
