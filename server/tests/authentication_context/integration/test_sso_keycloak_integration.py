import pytest
import requests
import time
from testcontainers.keycloak import KeycloakContainer
from playwright.async_api import (
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
)
from urllib.parse import urlparse, parse_qs

from authentication_context.adapters.secondary import OAuth2SsoGateway


@pytest.fixture(scope="module")
def keycloak_container():
    # Start Keycloak container for SSO integration testing.
    container = KeycloakContainer("quay.io/keycloak/keycloak:24.0")
    container.start()

    # Wait for Keycloak to be ready
    print("⏳ Waiting for Keycloak to be ready...")
    container.get_client()
    print(f"✅ Keycloak ready at: {container.get_url()}")

    yield container

    print("\n🛑 Stopping Keycloak container...")
    container.stop()


@pytest.fixture(scope="module")
def keycloak_config(keycloak_container):
    keycloak_url = keycloak_container.get_url()
    realm_name = "master"  # Use master realm to avoid authentication issues

    # Get credentials from container (testcontainers sets KEYCLOAK_ADMIN and KEYCLOAK_ADMIN_PASSWORD)
    admin_username = keycloak_container.username  # Usually "admin"
    admin_password = keycloak_container.password  # Usually "admin"

    # Test credentials
    test_username = "testuser"
    test_password = "testpass123"
    test_email = "testuser@example.com"
    client_id = "lecoffre-test-client"

    print(f"\n🔧 Configuring Keycloak at {keycloak_url}...")
    print(f"   Admin: {admin_username}")

    # Get admin access token using direct grant with retry
    token_url = f"{keycloak_url}/realms/master/protocol/openid-connect/token"

    # Retry getting token (Keycloak might still be initializing)
    token_response = None
    for attempt in range(5):
        token_response = requests.post(
            token_url,
            data={
                "client_id": "admin-cli",
                "username": admin_username,
                "password": admin_password,
                "grant_type": "password",
            },
            verify=False,
        )

        if token_response.status_code == 200:
            break

        print(f"   ⏳ Attempt {attempt + 1}/5 to get token failed, waiting...")
        time.sleep(2)

    if not token_response or token_response.status_code != 200:
        error_text = token_response.text if token_response else "No response"
        raise Exception(f"Failed to get admin token after retries: {error_text}")

    admin_token = token_response.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json",
    }

    # Create test user in master realm
    print(f"👤 Creating test user: {test_username}")
    user_response = requests.post(
        f"{keycloak_url}/admin/realms/{realm_name}/users",
        json={
            "username": test_username,
            "email": test_email,
            "enabled": True,
            "emailVerified": True,
            "firstName": "Test",
            "lastName": "User",
            "credentials": [
                {"type": "password", "value": test_password, "temporary": False}
            ],
        },
        headers=headers,
        verify=False,
    )

    if user_response.status_code in [201, 409]:  # Created or already exists
        print(f"✅ Test user ready: {test_username}")

        # If user already exists (409), make sure it has the right password
        if user_response.status_code == 409:
            # Get user ID
            users_response = requests.get(
                f"{keycloak_url}/admin/realms/{realm_name}/users",
                headers=headers,
                params={"username": test_username},
                verify=False,
            )
            if users_response.status_code == 200:
                users = users_response.json()
                if users:
                    user_id = users[0]["id"]
                    # Reset password
                    pwd_response = requests.put(
                        f"{keycloak_url}/admin/realms/{realm_name}/users/{user_id}/reset-password",
                        json={
                            "type": "password",
                            "value": test_password,
                            "temporary": False,
                        },
                        headers=headers,
                        verify=False,
                    )
                    if pwd_response.status_code == 204:
                        print(f"✅ Password reset for existing user")
    else:
        print(
            f"⚠️  User creation status: {user_response.status_code} - {user_response.text}"
        )

    # Create OIDC client in master realm
    print(f"🔧 Creating OIDC client: {client_id}")
    client_response = requests.post(
        f"{keycloak_url}/admin/realms/{realm_name}/clients",
        json={
            "clientId": client_id,
            "enabled": True,
            "publicClient": False,  # Confidential client
            "redirectUris": ["http://localhost:8000/auth/sso/callback"],
            "webOrigins": ["http://localhost:8000"],
            "protocol": "openid-connect",
            "standardFlowEnabled": True,  # Enable authorization code flow
            "directAccessGrantsEnabled": False,
            "serviceAccountsEnabled": False,
            "fullScopeAllowed": True,
        },
        headers=headers,
        verify=False,
    )

    if client_response.status_code in [201, 409]:  # Created or already exists
        print(f"✅ Client ready: {client_id}")
    else:
        print(
            f"⚠️  Client creation status: {client_response.status_code} - {client_response.text}"
        )

    # Get client UUID
    clients_response = requests.get(
        f"{keycloak_url}/admin/realms/{realm_name}/clients",
        headers=headers,
        params={"clientId": client_id},
        verify=False,
    )

    if clients_response.status_code != 200:
        raise Exception(f"Failed to get clients: {clients_response.text}")

    clients = clients_response.json()
    if not clients:
        raise Exception(f"Client {client_id} not found")

    client_uuid = clients[0]["id"]

    # Get client secret
    secret_response = requests.get(
        f"{keycloak_url}/admin/realms/{realm_name}/clients/{client_uuid}/client-secret",
        headers=headers,
        verify=False,
    )

    if secret_response.status_code != 200:
        raise Exception(f"Failed to get client secret: {secret_response.text}")

    client_secret = secret_response.json()["value"]

    print(f"✅ Configuration complete:")
    print(f"   - Keycloak URL: {keycloak_url}")
    print(f"   - Realm: {realm_name}")
    print(f"   - Client ID: {client_id}")
    print(f"   - User: {test_username}")

    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "discovery_url": f"{keycloak_url}/realms/{realm_name}/.well-known/openid-configuration",
        "keycloak_url": keycloak_url,
        "realm": realm_name,
        "username": test_username,
        "password": test_password,
        "email": test_email,
        "redirect_uri": "http://localhost:8000/auth/sso/callback",
    }


@pytest.fixture
def oauth2_sso_gateway(keycloak_config) -> OAuth2SsoGateway:
    gateway = OAuth2SsoGateway(
        base_url=keycloak_config["keycloak_url"],
        redirect_uri=keycloak_config["redirect_uri"],
    )
    return gateway


@pytest.mark.asyncio
async def test_configure_sso_with_oidc_discovery(oauth2_sso_gateway, keycloak_config):
    # This tests that the OIDC discovery endpoint is accessible and returns valid configuration.

    print("\n🔍 Testing OIDC auto-discovery with real Keycloak...")

    # Use the real OAuth2SsoGateway with auto-discovery
    await oauth2_sso_gateway.configure_with_discovery(
        client_id=keycloak_config["client_id"],
        client_secret=keycloak_config["client_secret"],
        discovery_url=keycloak_config["discovery_url"],
    )

    print("✅ Successfully configured SSO via OIDC discovery")

    # Verify we can get authorization URL
    auth_url = await oauth2_sso_gateway.get_authorize_url()

    assert (
        keycloak_config["keycloak_url"] in auth_url
    ), "Auth URL should contain Keycloak URL"
    assert "redirect_uri=" in auth_url, "Auth URL should contain redirect_uri"
    assert (
        "response_type=code" in auth_url
    ), "Auth URL should use authorization code flow"

    print(f"✅ Got valid authorization URL: {auth_url[:100]}...")


@pytest.mark.asyncio
async def test_complete_oauth2_flow_with_browser(oauth2_sso_gateway, keycloak_config):
    # Test complete OAuth2 flow: configure -> authorize -> callback -> token exchange.

    print("\n🎯 Testing complete OAuth2/OIDC flow with real Keycloak...")

    # Step 1: Configure SSO via OIDC discovery
    print("\n📝 Step 1: Configuring via OIDC discovery...")
    await oauth2_sso_gateway.configure_with_discovery(
        client_id=keycloak_config["client_id"],
        client_secret=keycloak_config["client_secret"],
        discovery_url=keycloak_config["discovery_url"],
    )
    print("✅ Configured")

    # Step 2: Get authorization URL
    print("\n🔗 Step 2: Getting authorization URL...")
    auth_url = await oauth2_sso_gateway.get_authorize_url()
    print(f"✅ Got auth URL: {auth_url[:80]}...")

    # Step 3: Simulate user authentication with Playwright
    print("\n🌐 Step 3: Simulating browser authentication...")
    auth_code = None
    callback_url = None

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            # Listen for navigation requests to capture the callback URL
            def handle_request(request):
                nonlocal callback_url
                url = request.url
                if "/auth/sso/callback" in url:
                    callback_url = url
                    print(f"✅ Captured callback URL: {url[:80]}...")

            page.on("request", handle_request)
            print(f"   🔹 Request listener set up to capture callback URL")

            print(f"   🔹 Navigating to Keycloak login: {auth_url[:80]}...")
            await page.goto(auth_url, wait_until="networkidle")

            # Wait for login form
            print("   🔹 Waiting for login form...")
            await page.wait_for_selector('input[name="username"]', timeout=15000)

            print(f"   🔹 Filling credentials (user: {keycloak_config['username']})...")
            await page.fill('input[name="username"]', keycloak_config["username"])
            await page.fill('input[name="password"]', keycloak_config["password"])

            print("   🔹 Submitting login...")
            # Use Promise.all to wait for navigation and capture the redirect
            try:
                await page.click('input[type="submit"]')
            except Exception as e:
                # Might fail if redirect happens to unreachable URL
                print(
                    f"   🔹 Click/navigation exception (expected): {type(e).__name__}"
                )

            # Wait for the callback to be intercepted
            print("   🔹 Waiting for callback redirect...")
            for i in range(30):  # Wait up to 15 seconds
                if callback_url:
                    break
                await page.wait_for_timeout(500)

                # Check URL every few iterations
                if i % 4 == 0:
                    current = page.url
                    print(
                        f"   ... still waiting ({i//2}s) - current: {current[:60]}..."
                    )

            if not callback_url:
                # Check current URL in case redirect happened differently
                current_url = page.url
                print(f"   ⚠️  No callback intercepted. Current URL: {current_url}")

                # Take a screenshot for debugging
                screenshot_path = "/tmp/keycloak_test_failure.png"
                await page.screenshot(path=screenshot_path)
                print(f"   📸 Screenshot saved to: {screenshot_path}")

                # Check if we're on an error page
                page_content = await page.content()
                print(f"   Page title: {await page.title()}")

                # Look for specific error messages
                if "invalid" in page_content.lower() or "error" in page_content.lower():
                    print(f"   ❌ Error detected in page")
                    # Print visible text
                    visible_text = await page.locator("body").inner_text()
                    print(f"   Visible text: {visible_text[:500]}")
                    raise Exception(
                        f"Keycloak login/authorization failed: {visible_text[:200]}"
                    )
                elif "chrome-error" in current_url or "about:" in current_url:
                    pytest.fail(
                        f"❌ Redirect failed - check Keycloak client configuration"
                    )
                else:
                    pytest.fail(f"❌ Expected callback redirect, got: {current_url}")

            await browser.close()

        # Parse authorization code
        parsed = urlparse(callback_url)
        query_params = parse_qs(parsed.query)
        auth_code = query_params.get("code", [None])[0]

        if not auth_code:
            # Check for error in callback
            error = query_params.get("error", [None])[0]
            error_description = query_params.get("error_description", [None])[0]
            if error:
                pytest.fail(f"❌ OAuth error: {error} - {error_description}")
            else:
                pytest.fail(f"❌ Authorization code not found in URL: {callback_url}")

        print(f"✅ Got authorization code: {auth_code[:20]}...")

    except PlaywrightTimeoutError as e:
        pytest.fail(f"❌ Playwright timeout: {e}")
    except Exception as e:
        pytest.fail(f"❌ Browser automation error: {e}")

    # Step 4: Exchange authorization code for tokens
    print("\n🔐 Step 4: Exchanging authorization code for tokens...")
    sso_user = await oauth2_sso_gateway.validate_callback(auth_code)

    # Verify SSO user data
    assert (
        sso_user.email == keycloak_config["email"]
    ), f"Email mismatch: expected {keycloak_config['email']}, got {sso_user.email}"
    assert sso_user.display_name is not None, "Display name should be set"
    assert sso_user.sso_user_id is not None, "SSO user ID should be set"
    assert sso_user.sso_provider is not None, "SSO provider should be set"


@pytest.mark.asyncio
async def test_oauth2_flow_with_invalid_code(oauth2_sso_gateway, keycloak_config):
    # Test that invalid authorization code is rejected.
    await oauth2_sso_gateway.configure_with_discovery(
        client_id=keycloak_config["client_id"],
        client_secret=keycloak_config["client_secret"],
        discovery_url=keycloak_config["discovery_url"],
    )

    with pytest.raises(Exception) as exc_info:
        await oauth2_sso_gateway.validate_callback("invalid-code-xyz123")

    # The exception should indicate authentication failure
    error_message = str(exc_info.value).lower()
    assert (
        "invalid" in error_message
        or "fail" in error_message
        or "error" in error_message
    )


@pytest.mark.asyncio
async def test_oidc_discovery_with_invalid_url(oauth2_sso_gateway):
    # Test that invalid discovery URL fails gracefully.
    with pytest.raises(Exception) as exc_info:
        await oauth2_sso_gateway.configure_with_discovery(
            client_id="test-client",
            client_secret="test-secret",
            discovery_url="https://invalid-domain-xyz123.com/.well-known/openid-configuration",
        )
