from datetime.datetime import DateTime
from enum import Enum

class SensorType(Enum):
    TEMPERATURE = 0
    HUMIDITY = 1
    VOC = 2
    NOISE = 3

class SensorValue:
    """Base ORM Objects for sensor datapoints"""
    bucket_time: DateTime
    arduino_id: int
    avg_value_in_bucket: float

class Temperature(SensorValue):
    """To manually ORM: Maps gold.temperature."""

class Humidty(SensorValue):
    """To manually ORM: Maps gold.Humidity."""

class Voc(SensorValue):
    """To manually ORM: Maps gold.Voc."""

class Noise(SensorValue):
    """To manually ORM: Maps gold.Noise."""