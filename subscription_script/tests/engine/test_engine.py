import pytest
from unittest import mock
from subscription_script.sql.engine import set_engine_session_factory
from sqlalchemy.exc import OperationalError

@pytest.fixture(autouse=True)
def reset_globals():
    """
    A pytest fixture that automatically runs before each test.
    It resets the global _engine and _session_factory variables,
    acting as the setup/teardown logic.
    """
    global _engine, _session_factory
    _engine = None
    _session_factory = None
    # 'yield' would go here if we had teardown logic after the test runs.


@mock.patch('os.getenv')
@mock.patch('sqlalchemy.create_engine')
def test_successful_initialization(mock_create_engine, mock_getenv):
    """
    Tests the successful creation of the engine and session factory
    on the first call.
    """
    # --- Arrange ---
    # Mock the environment variables to return dummy credentials.
    mock_getenv.side_effect = ['test_user', 'test_password', 'localhost']
    
    # Mock the engine object that create_engine is supposed to return.
    mock_engine_instance = mock.Mock()
    mock_create_engine.return_value = mock_engine_instance

    # --- Act ---
    set_engine_session_factory()

    # --- Assert ---
    # Verify that os.getenv was called for each required variable.
    mock_getenv.assert_has_calls([
        mock.call('DB_USERNAME'),
        mock.call('DB_PASSWORD'),
        mock.call('DB_HOST'),
    ])

    # Verify that create_engine was called with the correct connection string.
    expected_con_string = "postgresql+psycopg2://test_user:test_password@localhost/datenkraken"
    mock_create_engine.assert_called_once_with(expected_con_string, pool_size=5, pool_recycle=3600)

    # Check that the global variables were set correctly using plain asserts.
    global _engine, _session_factory
    assert _engine is not None
    assert _session_factory is not None
    assert _engine == mock_engine_instance


@mock.patch('sqlalchemy.create_engine')
def test_already_initialized(mock_create_engine):
    """
    Tests that the function does not re-initialize the engine and
    session factory if they already exist.
    """
    # --- Arrange ---
    # Manually set the global variables to simulate prior initialization.
    global _engine, _session_factory
    _engine = mock.Mock()
    _session_factory = mock.Mock()

    # --- Act ---
    set_engine_session_factory()

    # --- Assert ---
    # Verify that create_engine was not called since the engine was already set.
    mock_create_engine.assert_not_called()


@mock.patch('os.getenv')
@mock.patch('sqlalchemy.create_engine')
@mock.patch('logging.critical')
def test_operational_error_on_connection(mock_log_critical, mock_create_engine, mock_getenv):
    """
    Tests that an OperationalError is caught, logged, and re-raised.
    """
    # --- Arrange ---
    # Mock environment variables.
    mock_getenv.side_effect = ['user', 'pass', 'host']
    
    # Configure the mock create_engine to raise an OperationalError.
    mock_create_engine.side_effect = OperationalError("Connection failed", {}, None)

    # --- Act & Assert ---
    # Use pytest.raises to check that the correct exception is re-raised.
    with pytest.raises(OperationalError):
        set_engine_session_factory()

    # Verify that a critical error was logged.
    mock_log_critical.assert_called_once()
    assert "Database connection could not be established" in mock_log_critical.call_args[0][0]


@mock.patch('os.getenv')
@mock.patch('sqlalchemy.create_engine')
@mock.patch('logging.warning')
def test_generic_exception_on_connection(mock_log_warning, mock_create_engine, mock_getenv):
    """
    Tests that a generic Exception is caught, logged as a warning, and re-raised.
    """
    # --- Arrange ---
    # Mock environment variables.
    mock_getenv.side_effect = ['user', 'pass', 'host']
    
    # Configure the mock create_engine to raise a generic Exception.
    mock_create_engine.side_effect = Exception("Something went wrong")

    # --- Act & Assert ---
    # Check that the generic exception is re-raised.
    with pytest.raises(Exception):
        set_engine_session_factory()

    # Verify that a warning was logged.
    mock_log_warning.assert_called_once()
    assert "Error occured within database connection" in mock_log_warning.call_args[0][0]