import os
import logging
from sqlalchemy import create_engine, Engine, Row
from sqlalchemy import text  # new changes
from sqlalchemy.sql.selectable import Select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from typing import Union, List, Optional

_engine: Union[Engine, None] = None
_session_factory: Union[sessionmaker, None] = None


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


def commit_select(stmt: Select) -> Optional[List[Row]]:
    """Execute a SELECT statement and return all rows.

    Args:
        stmt: The SQLAlchemy ``Select`` statement to execute.

    Raises:
        RuntimeError: If the session factory has not been initialized.

    Returns:
        A list of rows on success, or ``None`` if an exception occurred (already logged).
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
            rows: List[Row] = session.execute(stmt).all()
            logging.info(f"Selection committed for {stmt}")
            return rows
    except Exception as e:
        logging.error(f"Error on selection {stmt} into database due to error: {e}")
        #new changes Return empty list so UI can render an empty state instead of crashing
        return []


def commit_select_scalar(stmt: Select) -> Optional[List[Union[str, float, int]]]:
    """Execute a scalar SELECT statement and return all scalar values.

    Args:
        stmt: The SQLAlchemy ``Select`` statement expected to yield scalar values.

    Raises:
        RuntimeError: If the session factory has not been initialized.

    Returns:
        A list of scalar values on success, or ``None`` if an exception occurred (already logged).
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
            rows: List[Union[str, float, int]] = session.execute(stmt).scalars().all()
            logging.info(f"Selection committed for {stmt}")
            return rows
    except Exception as e:
        logging.error(f"Error on selection {stmt} into database due to error: {e}")
        #new changes Return empty list so UI can render an empty state instead of crashing
        return []


def is_db_healthy() -> bool:
    #new changes Simple DB healthcheck used by the UI
    try:
        if _engine is None:
            set_engine_session_factory()
        with _engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
