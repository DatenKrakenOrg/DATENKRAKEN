import os
import logging
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
from typing import Union, List
from subscription_script.sql.orm import Temperature, Humidity, Voc, Noise

_engine: Union[Engine, None] = None
_session_factory: Union[Session, None] = None


def set_engine_session_factory() -> None:
    """Initializes global engine (with connection pool of size 5 and a session_factory). Must be called once in order to being able to insert orm objects."""
    global _engine
    global _session_factory

    if _engine is None:
        con_string = f"postgresql+psycopg2://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/datenkraken"
        try:
            _engine = create_engine(con_string, pool_size=5, pool_recycle=3600)
        except OperationalError as e:
            logging.critical(f"Database connection could not be established {e}")
            raise
        except Exception as e:
            logging.warning(f"Error occured within database connection {e}")
            raise

    if _session_factory is None:
        _session_factory = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def insert_into_db(orm_objs: List[Union[Temperature, Humidity, Voc, Noise]]) -> None:
    """Can be used to insert mulipe orm objects into a posgresql (timescaledb in our use-case) => Mapping can be found in sql.orm

    Args:
        orm_objs (List[Union[Temperature, Humidity, Voc, Noise]]): Multiple orm objects found in sql.orm that should be inserted into timescale.

    Raises:
        RuntimeError: May be raised whenever no session_factory was initialized (and engine) via sql.engine.set_engine_session_factory()
    """
    if _session_factory is None:
        logging.critical(
            "Database session factory not initialized. Call set_engine_session_factory() first."
        )
        raise RuntimeError(
            "Database session factory not initialized. Call set_engine_session_factory() first."
        )

    try:
        with _session_factory() as session:
            for orm_obj in orm_objs:
                session.add(orm_obj)
            session.commit()
        logging.info(f"Transaction committed for {type(orm_objs[0])}")
    except Exception as e:
        logging.error(f"Error on inserting {orm_obj} into database due to error: {e}")
