import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from main import app


@pytest.fixture(scope="function")
def database():
    """Create a temporary database for testing"""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)  # Close the file descriptor, we just need the path

    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    yield
    try:
        os.unlink(db_path)
    except OSError:
        pass
    if "DATABASE_URL" in os.environ:
        del os.environ["DATABASE_URL"]


@pytest.fixture
def api_client(database):
    """Test client for API testing"""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def sso_test_data():
    """Test data for SSO integration tests"""
    return {
        "valid_code_123": {
            "sso_user_id": "azure_123456789",
            "email": "john.doe@example.com",
            "display_name": "John Doe",
            "provider": "azure",
        },
        "consistent_code_456": {
            "sso_user_id": "azure_987654321",
            "email": "jane.smith@company.com",
            "display_name": "Jane Smith",
            "provider": "azure",
        },
    }


@pytest.fixture
def sso_gateway(sso_test_data):
    """SSO Gateway configured with test data"""
    from authentication_context.adapters.secondary import InMemorySSOGateway

    gateway = InMemorySSOGateway(
        authorize_url="https://test-sso.example.com/authorize",
        valid_codes=sso_test_data,
    )
    return gateway
