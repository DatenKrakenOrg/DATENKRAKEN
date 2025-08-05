from sqlalchemy import BigInteger, SmallInteger, Float, DateTime, Text, Column, Identity
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# PK must be set although there is none => Needed by sqlalchemy on insert this feature isnt needed therefore it doesnt matter if the column isnt actually a pk
class Temperature(Base):
    __tablename__ = "temperature"
    id = Column(BigInteger, Identity(), primary_key=True, autoincrement=True)
    time = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    arduino_id = Column(Text(), nullable=False)
    temperature = Column(Float(), nullable=False)

    __table_args__ = {'schema': 'bronze'}


class Humidity(Base):
    __tablename__ = "humidity"

    id = Column(BigInteger, Identity(), primary_key=True)
    time = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    arduino_id = Column(Text(), nullable=False)
    humidity = Column(SmallInteger(), nullable=False)

    __table_args__ = {'schema': 'bronze'}


class Voc(Base):
    __tablename__ = "voc"

    id = Column(BigInteger, Identity(), primary_key=True)
    time = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    arduino_id = Column(Text(), nullable=False)
    voc = Column(SmallInteger(), nullable=False)

    __table_args__ = {'schema': 'bronze'}


class Noise(Base):
    __tablename__ = "noise"

    id = Column(BigInteger, Identity(), primary_key=True)
    time = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    arduino_id = Column(Text(), nullable=False)
    noise = Column(SmallInteger(), nullable=False)

    __table_args__ = {'schema': 'bronze'}
