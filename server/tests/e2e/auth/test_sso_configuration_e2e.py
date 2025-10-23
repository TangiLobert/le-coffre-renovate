"""End-to-end tests for SSO configuration with real SSO provider credentials."""

import pytest
import os
from unittest.mock import patch, AsyncMock
from authentication_context.adapters.secondary import (
    InMemorySSOGateway,
)


@pytest.mark.asyncio
class TestSsoConfigurationE2E:
    """End-to-end tests for SSO configuration."""

    @pytest.fixture
    def sso_credentials(self):
        """SSO credentials from environment variables."""
        return {
            "client_id": os.getenv("SSO_CLIENT_ID"),
            "client_secret": os.getenv("SSO_CLIENT_SECRET"),
            "discovery_url": os.getenv("SSO_DISCOVERY_URL"),
        }

    @pytest.fixture
    def sso_discovery_url(self, sso_credentials):
        """SSO provider's OpenID Connect discovery URL.

        Uses SSO_DISCOVERY_URL from environment or fallback for Azure.
        """
        discovery_url = sso_credentials.get("discovery_url")
        if discovery_url:
            return discovery_url

        # Fallback to Azure common endpoint for backward compatibility
        return "https://login.microsoftonline.com/common/v2.0/.well-known/openid_configuration"

    async def test_configure_sso_with_mocked_discovery(
        self, e2e_client, setup, sso_credentials, sso_discovery_url
    ):
        """Test SSO configuration with mocked discovery for consistent testing."""

        # Mock InMemorySSOGateway for e2e tests (like in integration tests)
        with patch.object(
            InMemorySSOGateway, "configure_with_discovery", new_callable=AsyncMock
        ) as mock_configure:
            # Arrange
            config_data = {
                "client_id": sso_credentials.get("client_id") or "test-client-id",
                "client_secret": sso_credentials.get("client_secret") or "test-secret",
                "discovery_url": sso_discovery_url,
            }

            # Act: SSO configuration (no admin auth needed for this route)
            response = e2e_client.post(
                "/auth/sso/configure",
                json=config_data,
            )

            # Assert: Configuration should succeed
            assert response.status_code == 200, f"Configuration failed: {response.text}"

            # Verify that configure_with_discovery was called
            mock_configure.assert_called_once_with(
                client_id=config_data["client_id"],
                client_secret=config_data["client_secret"],
                discovery_url=config_data["discovery_url"],
            )

            # Verify we can get SSO URL after configuration
            url_response = e2e_client.get("/auth/sso/url")
            assert url_response.status_code == 200

            # The endpoint returns the URL directly as a string
            sso_url = url_response.json()
            assert isinstance(sso_url, str)
            assert "http" in sso_url  # Validate it's a URL

    async def test_sso_configuration_flow_validation(self, e2e_client, setup):
        """Test the complete SSO configuration validation flow."""

        # Test 1: Missing credentials should fail
        response = e2e_client.post(
            "/auth/sso/configure",
            json={
                "client_id": "",
                "client_secret": "secret",
                "discovery_url": "https://login.microsoftonline.com/common/v2.0/.well-known/openid_configuration",
            },
        )
        assert response.status_code == 400
        assert (
            "Client ID, client secret, and discovery URL are required"
            in response.json()["detail"]
        )

        # Test 2: Invalid discovery URL should fail with mocked error
        with patch.object(
            InMemorySSOGateway, "configure_with_discovery", new_callable=AsyncMock
        ) as mock_configure:
            mock_configure.side_effect = ValueError(
                "Error discovering endpoints: HTTP 404"
            )

            response = e2e_client.post(
                "/auth/sso/configure",
                json={
                    "client_id": "test-id",
                    "client_secret": "test-secret",
                    "discovery_url": "https://invalid-domain.com/.well-known/openid_configuration",
                },
            )
            assert response.status_code == 400
            assert "Auto-discovery failed" in response.json()["detail"]

        # Test 3: Missing required fields should fail validation
        response = e2e_client.post(
            "/auth/sso/configure",
            json={
                "client_id": "test-id",
                "client_secret": "test-secret",
                # discovery_url missing
            },
        )
        assert response.status_code == 422  # Validation error

    @pytest.mark.skipif(
        not os.getenv("SSO_CLIENT_ID"),
        reason="SSO_CLIENT_ID not set - skipping real SSO integration test",
    )
    async def test_configure_sso_with_real_credentials(
        self, e2e_client, setup, sso_credentials, sso_discovery_url
    ):
        """Test SSO configuration flow with real SSO provider credentials.

        Note: This e2e test uses InMemorySSOGateway (for consistency with other e2e tests),
        so it tests the configuration flow but not the real SSO integration.

        To test with real SSO integration (OAuth2SsoGateway with real HTTP calls),
        see: tests/authentication_context/integration/test_sso_real_integration.py
        """

        # For this e2e test, InMemorySSOGateway is used (even with real credentials)

        # Arrange: Prepare configuration data
        config_data = {
            "client_id": sso_credentials["client_id"],
            "client_secret": sso_credentials["client_secret"],
            "discovery_url": sso_discovery_url,
        }

        # Act: Configure SSO with auto-discovery
        response = e2e_client.post(
            "/auth/sso/configure",
            json=config_data,
        )

        # Assert: Configuration should succeed
        assert response.status_code == 200, f"Configuration failed: {response.text}"

        # Verify we can get SSO URL after configuration
        url_response = e2e_client.get("/auth/sso/url")
        assert url_response.status_code == 200
        print(url_response.json())

        # The endpoint returns the URL directly as a string
        sso_url = url_response.json()
        assert isinstance(sso_url, str)

        discovery_info = sso_credentials.get("discovery_url") or "default provider"
        print(f"\n✅ E2E test passed with credentials for: {discovery_info}")
        print("📍 Note: Using InMemorySSOGateway for e2e consistency")
        print(
            "📍 For real integration testing, run: pytest tests/authentication_context/integration/test_sso_real_integration.py"
        )
