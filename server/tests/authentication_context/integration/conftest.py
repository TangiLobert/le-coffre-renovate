import pytest
from authentication_context.adapters.secondary import (
    InMemorySSOGateway,
)


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
    gateway = InMemorySSOGateway(
        authorize_url="https://test-sso.example.com/authorize",
        valid_codes=sso_test_data,
    )
    return gateway
