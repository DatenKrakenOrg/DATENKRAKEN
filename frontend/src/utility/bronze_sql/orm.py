from sqlalchemy import BigInteger, SmallInteger, Float, DateTime, Text, Column, Identity
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# PK must be set although there is none => Needed by sqlalchemy on insert this feature isnt needed therefore it doesnt matter if the column isnt actually a pk
class Temperature(Base):
    """ORM: Maps bronze.temperature. Only deleted_at is nullable!"""

    __tablename__ = "temperature"
    id = Column(BigInteger, Identity(), primary_key=True, autoincrement=True)
    time = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    arduino_id = Column(Text(), nullable=False)
    temperature = Column(Float(), nullable=False)

    __table_args__ = {"schema": "bronze"}


class Humidity(Base):
    """ORM: Maps bronze.humidity. Only deleted_at is nullable!"""

    __tablename__ = "humidity"

    id = Column(BigInteger, Identity(), primary_key=True)
    time = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    arduino_id = Column(Text(), nullable=False)
    humidity = Column(SmallInteger(), nullable=False)

    __table_args__ = {"schema": "bronze"}


class Voc(Base):
    """ORM: Maps bronze.voc. Only deleted_at is nullable!"""

    __tablename__ = "voc"

    id = Column(BigInteger, Identity(), primary_key=True)
    time = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    arduino_id = Column(Text(), nullable=False)
    voc = Column(SmallInteger(), nullable=False)

    __table_args__ = {"schema": "bronze"}


class Noise(Base):
    """ORM: Maps bronze.noise. Only deleted_at is nullable!"""

    __tablename__ = "noise"

    id = Column(BigInteger, Identity(), primary_key=True)
    time = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    arduino_id = Column(Text(), nullable=False)
    noise = Column(SmallInteger(), nullable=False)

    __table_args__ = {"schema": "bronze"}
