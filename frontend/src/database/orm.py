from datetime import datetime
from enum import Enum
from typing import Union

class SensorType(Enum):
    TEMPERATURE = 0
    HUMIDITY = 1
    VOC = 2
    NOISE = 3

class SensorValue:
    """Base ORM Objects for sensor datapoints"""
    bucket_time: Union[datetime, None]
    arduino_id: Union[int, None]
    avg_value_in_bucket: Union[float, None]

    def __init__(self, bucket_time, arduino_id, avg_value_in_bucket):
        self.bucket_time = bucket_time
        self.arduino_id = arduino_id
        self.avg_value_in_bucket = avg_value_in_bucket

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.bucket_time}, {self.arduino_id}, {self.avg_value_in_bucket})"

class Temperature(SensorValue):
    """To manually ORM: Maps gold.temperature."""

    def __init__(self, bucket_time, arduino_id, avg_value_in_bucket):
        super().__init__(bucket_time, arduino_id, avg_value_in_bucket)

class Humidity(SensorValue):
    """To manually ORM: Maps gold.Humidity."""
    def __init__(self, bucket_time, arduino_id, avg_value_in_bucket):
        super().__init__(bucket_time, arduino_id, avg_value_in_bucket)

class Voc(SensorValue):
    """To manually ORM: Maps gold.Voc."""
    def __init__(self, bucket_time, arduino_id, avg_value_in_bucket):
        super().__init__(bucket_time, arduino_id, avg_value_in_bucket)

class Noise(SensorValue):
    """To manually ORM: Maps gold.Noise."""
    def __init__(self, bucket_time, arduino_id, avg_value_in_bucket):
        super().__init__(bucket_time, arduino_id, avg_value_in_bucket)