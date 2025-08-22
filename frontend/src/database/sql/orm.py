from sqlalchemy import Float, DateTime, Text, Column
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class SensorValue:
    """Base ORM Objects for sensor datapoints"""

    bucket_time = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    arduino_id = Column(Text(), nullable=False)
    avg_value_in_bucket = Column(Float(), nullable=False)


# PK must be set although there is none => Needed by sqlalchemy on insert this feature isnt needed therefore it doesnt matter if the column isnt actually a pk
class Temperature(SensorValue, Base):
    """ORM: Maps gold.temperature. Only deleted_at is nullable!"""

    __tablename__ = "temperature"
    __table_args__ = {"schema": "gold"}


class Humidity(SensorValue, Base):
    """ORM: Maps gold.humidity. Only deleted_at is nullable!"""

    __tablename__ = "humidity"
    __table_args__ = {"schema": "gold"}


class Voc(SensorValue, Base):
    """ORM: Maps gold.voc. Only deleted_at is nullable!"""

    __tablename__ = "voc"
    __table_args__ = {"schema": "gold"}


class Noise(SensorValue, Base):
    """ORM: Maps gold.noise. Only deleted_at is nullable!"""

    __tablename__ = "noise"
    __table_args__ = {"schema": "gold"}
