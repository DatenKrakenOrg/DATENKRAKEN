"""Module implementing all necessary database operations! Sets the session factory on import.
"""
from .engine import set_engine_session_factory

set_engine_session_factory()