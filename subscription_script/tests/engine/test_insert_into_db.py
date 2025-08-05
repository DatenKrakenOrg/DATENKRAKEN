import pytest
from unittest import mock
from subscription_script.sql import engine as engine_module
from subscription_script.sql.engine import insert_into_db
from sqlalchemy.exc import IntegrityError

@pytest.fixture(autouse=True)
def reset_globals():
    """
    Reset global variables
    """
    engine_module._engine = None
    engine_module._session_factory = None


def test_error_on_missing_ses_factory(mocker):
    """
    Tests whether a critical log occurs whenever session_factory is unset
    """
    # --- Arrange ---

    # Mock logs
    mock_logging = mocker.patch(
        "logging.critical"
    )

    # --- Act ---
    with pytest.raises(RuntimeError):
        insert_into_db([])

    # --- Assert ---
    mock_logging.assert_called_once()


def test_insert_into_db_exception_on_commit(mocker):
    """
    Given a list of ORM objects,
    When session.commit() raises an exception,
    Then the error should be logged and the exception should be handled.
    """
    # --- Arrange ---

    # Create Mock objects for parameters
    mock_obj_1 = mocker.MagicMock()
    mock_obj_1.__repr__ = mocker.Mock(return_value="<Temperature object>")
    mock_obj_2 = mocker.MagicMock()
    mock_obj_2.__repr__ = mocker.Mock(return_value="<Humidity object>")
    orm_objects_to_insert = [mock_obj_1, mock_obj_2]

    # Create Session mock
    mock_session = mocker.MagicMock()

    # Let commit raise integrity error as example
    error_to_raise = IntegrityError("Duplicate key value violates unique constraint", {}, None)
    mock_session.commit.side_effect = error_to_raise

    # Mock session maker. Attention to context manager protocol
    mock_session_factory = mocker.patch("subscription_script.sql.engine._session_factory")
    mock_session_factory.return_value.__enter__.return_value = mock_session
    # Mock the logger to capture the error message.
    mock_logging_error = mocker.patch("logging.error")

    # --- Act ---
    insert_into_db(orm_objects_to_insert)

    # --- Assert ---
    mock_logging_error.assert_called_once()

def test_insert_into_db_successful(mocker):
    """
    Tests successful insert
    """
    # --- Arrange ---

    # Create Mock objects for parameters
    mock_obj_1 = mocker.MagicMock()
    mock_obj_1.__repr__ = mocker.Mock(return_value="<Temperature object>")
    mock_obj_2 = mocker.MagicMock()
    mock_obj_2.__repr__ = mocker.Mock(return_value="<Humidity object>")
    orm_objects_to_insert = [mock_obj_1, mock_obj_2]

    # Create Session mock
    mock_session = mocker.MagicMock()

    # Mock session maker. Attention to context manager protocol
    mock_session_factory = mocker.patch("subscription_script.sql.engine._session_factory")
    mock_session_factory.return_value.__enter__.return_value = mock_session
    # Mock the logger to capture the info message.
    mock_logging_info = mocker.patch("logging.info")

    # --- Act ---
    insert_into_db(orm_objects_to_insert)

    # --- Assert ---
    mock_logging_info.assert_called_once()
