"""Unit tests for run_migrations retry behavior."""
import pytest
from unittest.mock import patch
from sqlalchemy.exc import OperationalError as SQLAlchemyOperationalError

# Import Psycopg2OperationalError from src.main so tests use the exact same class
# object that tenacity is configured with (psycopg2 may not be installed).
from src.main import Psycopg2OperationalError


@pytest.fixture(autouse=True)
def _freeze_tenacity_sleep(monkeypatch):
    """Prevent real sleeping in tenacity retries during tests."""
    monkeypatch.setattr("tenacity.nap.time.sleep", lambda _: None)


@patch("src.main.command")
@patch("src.main.get_database_url", return_value="postgresql://test")
@patch("src.main.Config")
def test_success_on_first_attempt(mock_config, mock_url, mock_command):
    from src.main import run_migrations
    run_migrations()
    mock_command.upgrade.assert_called_once()


@patch("src.main.command")
@patch("src.main.get_database_url", return_value="postgresql://test")
@patch("src.main.Config")
def test_retries_on_sqlalchemy_operational_error(mock_config, mock_url, mock_command):
    from src.main import run_migrations
    error = SQLAlchemyOperationalError("connection failed", None, None)
    mock_command.upgrade.side_effect = [error, error, None]
    run_migrations()
    assert mock_command.upgrade.call_count == 3


@patch("src.main.command")
@patch("src.main.get_database_url", return_value="postgresql://test")
@patch("src.main.Config")
def test_retries_on_psycopg2_operational_error(mock_config, mock_url, mock_command):
    from src.main import run_migrations
    mock_command.upgrade.side_effect = [Psycopg2OperationalError("conn reset"), None]
    run_migrations()
    assert mock_command.upgrade.call_count == 2


@patch("src.main.command")
@patch("src.main.get_database_url", return_value="postgresql://test")
@patch("src.main.Config")
def test_does_not_retry_on_non_operational_error(mock_config, mock_url, mock_command):
    from src.main import run_migrations
    mock_command.upgrade.side_effect = ValueError("bad migration SQL")
    with pytest.raises(ValueError, match="bad migration SQL"):
        run_migrations()
    assert mock_command.upgrade.call_count == 1


@patch("src.main.command")
@patch("src.main.get_database_url", return_value="postgresql://test")
@patch("src.main.Config")
def test_reraises_after_max_attempts(mock_config, mock_url, mock_command):
    import tenacity
    from src.main import _run_migrations_with_retry
    error = SQLAlchemyOperationalError("db down", None, None)
    mock_command.upgrade.side_effect = error
    limited = tenacity.retry(
        wait=tenacity.wait_none(),
        retry=tenacity.retry_if_exception_type((SQLAlchemyOperationalError, Psycopg2OperationalError)),
        stop=tenacity.stop_after_attempt(3),
        reraise=True,
    )(_run_migrations_with_retry.__wrapped__)
    with pytest.raises(SQLAlchemyOperationalError):
        limited(mock_config())
    assert mock_command.upgrade.call_count == 3
