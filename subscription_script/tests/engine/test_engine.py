import pytest
from unittest import mock
from unittest.mock import call
from subscription_script.sql import engine as engine_module
from subscription_script.sql.engine import set_engine_session_factory
from sqlalchemy.exc import OperationalError


@pytest.fixture(autouse=True)
def reset_globals():
    """
    Reset global variables
    """
    engine_module._engine = None
    engine_module._session_factory = None


def test_successful_initialization(mocker):
    """
    Tests the successful creation of the engine and session factory
    on the first call.
    """
    # --- Arrange ---
    # Mock environment variables.
    def get_env_logic(key, default=None):
        if key == "DB_USERNAME":
            return "test_user"
        if key == "DB_PASSWORD":
            return "test_password"
        if key == "DB_HOST":
            return "localhost"
        return None

    # Mock the environment variables to return dummy credentials.
    mock_getenv = mocker.patch("os.getenv", side_effect=get_env_logic)

    # Mock the engine object that create_engine is supposed to return.
    mock_create_engine_return = mocker.patch("sqlalchemy.Engine")
    mock_create_engine = mocker.patch(
        "subscription_script.sql.engine.create_engine",
        return_value=mock_create_engine_return,
    )

    # --- Act ---
    set_engine_session_factory()

    # --- Assert ---
    # Verify that os.getenv was called for each required variable.
    called_envs = [call("DB_USERNAME"), call("DB_PASSWORD"), call("DB_HOST")]
    mock_getenv.assert_has_calls(called_envs)

    # Verify that create_engine was called with the correct connection string.
    expected_con_string = (
        "postgresql+psycopg2://test_user:test_password@localhost/datenkraken"
    )
    mock_create_engine.assert_called_once_with(
        expected_con_string, pool_size=5, pool_recycle=3600
    )

    # Check that the global variables were set correctly using plain asserts.
    assert engine_module._engine is not None
    assert engine_module._session_factory is not None
    assert engine_module._engine == mock_create_engine_return


def test_already_initialized(mocker):
    """
    Tests that the function does not re-initialize the engine and
    session factory if they already exist.
    """
    # --- Arrange ---
    # Manually set the global variables to simulate prior initialization.
    engine_module._engine = mock.MagicMock()
    engine_module._session_factory = mock.MagicMock()

    # Mock create_engine and sessionmaker
    mock_create_engine =  mock_create_engine_return = mocker.patch("sqlalchemy.Engine")
    mock_create_engine = mocker.patch(
        "subscription_script.sql.engine.create_engine",
        return_value=mock_create_engine_return,
    )

    mock_sessionmaker_return = mocker.patch("sqlalchemy.orm.Session")
    mock_sessionmaker = mocker.patch(
        "subscription_script.sql.engine.sessionmaker",
        return_value=mock_sessionmaker_return,
    )

    # --- Act ---
    set_engine_session_factory()

    # --- Assert ---
    # Verify that create_engine was not called since the engine was already set.
    mock_create_engine.assert_not_called()
    mock_sessionmaker.assert_not_called()

def test_operational_error_on_connection(mocker):
    """
    Tests that an OperationalError is caught, logged, and re-raised.
    """
    # --- Arrange ---
    # Mock environment variables.
    def get_env_logic(key, default=None):
        if key == "DB_USERNAME":
            return "test_user"
        if key == "DB_PASSWORD":
            return "test_password"
        if key == "DB_HOST":
            return "localhost"
        return None

    # Mock the environment variables to return dummy credentials.
    mock_getenv = mocker.patch("os.getenv", side_effect=get_env_logic)

    # Mock engine
    mock_create_engine = mocker.patch(
        "subscription_script.sql.engine.create_engine",
    )

    # Configure the mock create_engine to raise an OperationalError.
    mock_create_engine.side_effect = OperationalError("Connection failed", {}, None)

    # Mock logging
    mock_logging = mocker.patch("logging.critical")
    # --- Act & Assert ---
    with pytest.raises(OperationalError):
        set_engine_session_factory()

    # Verify that a critical error was logged.
    mock_logging.assert_called_once()

def test_generic_error_on_connection(mocker):
    """
    Tests that an OperationalError is caught, logged, and re-raised.
    """
    # --- Arrange ---
    # Mock environment variables.
    def get_env_logic(key, default=None):
        if key == "DB_USERNAME":
            return "test_user"
        if key == "DB_PASSWORD":
            return "test_password"
        if key == "DB_HOST":
            return "localhost"
        return None

    # Mock the environment variables to return dummy credentials.
    mock_getenv = mocker.patch("os.getenv", side_effect=get_env_logic)

    # Mock engine
    mock_create_engine = mocker.patch(
        "subscription_script.sql.engine.create_engine"
    )

    mock_create_engine.side_effect = Exception("Generic exception")

    # Mock logging
    mock_logging = mocker.patch("logging.warning")
    # --- Act & Assert ---
    with pytest.raises(Exception):
        set_engine_session_factory()

    # Verify that a critical error was logged.
    mock_logging.assert_called_once()
