"""Integration tests with real SSO provider credentials."""

import pytest
import os
import httpx
from authentication_context.adapters.secondary.oauth2_sso_gateway import (
    OAuth2SsoGateway,
)


@pytest.mark.skipif(
    not os.getenv("SSO_CLIENT_ID"),
    reason="SSO_CLIENT_ID not set - skipping real SSO integration test",
)
@pytest.mark.asyncio
async def test_configure_sso_with_real_azure_autodiscovery():
    """Test SSO configuration with real OpenID Connect provider credentials and auto-discovery.

    This test makes real HTTP calls to the SSO provider's OpenID Connect discovery endpoint.
    Works with any OpenID Connect provider (Azure, Google, Okta, Keycloak, etc.).

    Set these environment variables to run this test:
    - SSO_CLIENT_ID (required)
    - SSO_CLIENT_SECRET (required)
    - SSO_DISCOVERY_URL (required)

    Example for Azure:
      export SSO_DISCOVERY_URL="https://login.microsoftonline.com/common/v2.0/.well-known/openid_configuration"
    """
    # Arrange: Get real SSO credentials
    client_id = os.getenv("SSO_CLIENT_ID")
    client_secret = os.getenv("SSO_CLIENT_SECRET")
    discovery_url = os.getenv("SSO_DISCOVERY_URL")

    assert client_id, "SSO_CLIENT_ID environment variable is required"
    assert client_secret, "SSO_CLIENT_SECRET environment variable is required"
    assert discovery_url, "SSO_DISCOVERY_URL environment variable is required"
    redirect_uri = "http://localhost:8000/auth/sso/callback"
    base_url = "http://localhost:8000"

    # Create real OAuth2 gateway (not mocked)
    gateway = OAuth2SsoGateway(base_url=base_url, redirect_uri=redirect_uri)

    # Act: Configure with real auto-discovery (makes real HTTP call to SSO provider)
    await gateway.configure_with_discovery(
        client_id=client_id,
        client_secret=client_secret,
        discovery_url=discovery_url,
    )

    # Assert: Gateway should be properly configured
    authorize_url = await gateway.get_authorize_url()

    # Verify the authorization URL is properly formatted
    assert authorize_url.startswith("https://"), "Authorization URL should use HTTPS"
    assert client_id in authorize_url, "Client ID should be in the authorization URL"
    assert "response_type=code" in authorize_url, "Response type should be 'code'"
    # Note: redirect_uri might be URL-encoded, so we check for the base part or encoded version
    assert "redirect_uri=" in authorize_url, "Redirect URI parameter should be present"

    print(f"\n✅ Successfully configured SSO with discovery: {discovery_url}")
    print(f"📍 Authorization URL: {authorize_url[:150]}...")
    print(f"📍 Full URL: {authorize_url}")


@pytest.mark.skipif(
    not os.getenv("SSO_CLIENT_ID"),
    reason="SSO_CLIENT_ID not set - skipping real SSO integration test",
)
@pytest.mark.asyncio
async def test_sso_discovery_endpoint_structure():
    """Test that the SSO provider's discovery endpoint returns expected OpenID Connect metadata.

    This validates that the discovery endpoint is accessible and returns
    all required OpenID Connect fields.
    """

    # Arrange: Get discovery URL from env
    discovery_url = os.getenv("SSO_DISCOVERY_URL")
    assert discovery_url, "SSO_DISCOVERY_URL environment variable is required"

    # Act: Fetch real discovery metadata from SSO provider
    async with httpx.AsyncClient() as client:
        response = await client.get(discovery_url)
        response.raise_for_status()
        metadata = response.json()

    # Assert: Verify all required OpenID Connect fields are present
    required_fields = [
        "authorization_endpoint",
        "token_endpoint",
        "userinfo_endpoint",
        "jwks_uri",
        "issuer",
    ]

    for field in required_fields:
        assert field in metadata, f"Missing required field: {field}"
        assert metadata[field], f"Field {field} is empty"

    # Verify OpenID Connect standard structure
    assert metadata["authorization_endpoint"].startswith("https://")
    assert metadata["userinfo_endpoint"].startswith("https://")

    print(f"\n✅ SSO discovery endpoint validated: {discovery_url}")
    print(f"📍 Issuer: {metadata['issuer']}")
    print(f"📍 Authorization endpoint: {metadata['authorization_endpoint']}")
    print(f"📍 Token endpoint: {metadata['token_endpoint']}")
    print(f"📍 Userinfo endpoint: {metadata['userinfo_endpoint']}")
