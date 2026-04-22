from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterator
from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from identity_access_management_context.application.gateways import Token
from security.rate_limit_middleware import RateLimitMiddleware
from security.rate_limiter import InMemoryRateLimiter
from shared_kernel.adapters.secondary import UtcTimeGateway
from starlette.testclient import TestClient


class _FakeTokenGateway:
    """Minimal token gateway for middleware unit tests."""

    def __init__(self) -> None:
        self._tokens: dict[str, Token] = {}

    def register(self, token: str, user_id: str) -> None:
        self._tokens[token] = Token(value=token, user_id=UUID(user_id), email="", roles=[], claims={})

    async def validate_token(self, token: str) -> Token | None:
        return self._tokens.get(token)


def _create_app(
    *,
    user_max: int = 300,
    unauth_max: int = 30,
    auth_max: int = 100,
    window: int = 60,
    login_status_code: int = 401,
    token_gateway: _FakeTokenGateway | None = None,
    trusted_proxies: set[str] | None = None,
    trusted_proxy_hops: int = 1,
) -> FastAPI:
    app = FastAPI(root_path="/api")

    app.state.rate_limiter = InMemoryRateLimiter()
    app.state.time_provider = UtcTimeGateway()
    app.state.token_gateway = token_gateway
    app.state.rate_limit_user_max_requests = user_max
    app.state.rate_limit_unauth_max_requests = unauth_max
    app.state.rate_limit_auth_max_requests = auth_max
    app.state.rate_limit_window_seconds = window
    app.state.rate_limit_trusted_proxies = trusted_proxies if trusted_proxies is not None else {"127.0.0.1", "::1"}
    app.state.rate_limit_trusted_proxy_hops = trusted_proxy_hops

    app.add_middleware(RateLimitMiddleware)

    @app.get("/health")
    async def health():
        return PlainTextResponse("ok")

    @app.get("/passwords")
    async def passwords():
        return PlainTextResponse("passwords")

    @app.post("/auth/login")
    async def login():
        return PlainTextResponse("login", status_code=login_status_code)

    @app.post("/auth/register-admin")
    async def register_admin():
        return PlainTextResponse("registered", status_code=200)

    @app.post("/auth/refresh-token")
    async def refresh_token():
        return PlainTextResponse("refreshed", status_code=200)

    @app.get("/auth/sso/callback")
    async def sso_callback():
        return PlainTextResponse("sso-ok", status_code=200)

    @app.get("/auth/sso/url")
    async def sso_url():
        return PlainTextResponse("sso-url", status_code=200)

    @app.get("/auth/sso/is-configured")
    async def sso_is_configured():
        return PlainTextResponse("configured", status_code=200)

    @app.get("/other")
    async def other():
        return PlainTextResponse("other")

    return app


@pytest.fixture
def app() -> FastAPI:
    return _create_app(user_max=10, unauth_max=5, auth_max=3, window=60)


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c


class TestExemptPaths:
    def test_given_health_path_when_dispatching_should_pass_through(self, client: TestClient):
        for _ in range(20):
            assert client.get("/api/health").status_code == 200

    def test_given_docs_or_openapi_path_when_dispatching_should_pass_through(self, client: TestClient):
        for _ in range(20):
            assert client.get("/docs").status_code != 429
            assert client.get("/openapi.json").status_code != 429

    def test_given_non_api_path_when_dispatching_should_pass_through(self):
        app = _create_app(user_max=1, unauth_max=1, auth_max=1, window=60)
        with TestClient(app) as c:
            for _ in range(5):
                assert c.get("/other").status_code == 200


class TestUnauthenticatedIpBucket:
    def test_given_unauth_limit_reached_when_dispatching_should_block_caller(self, client: TestClient):
        for _ in range(5):
            assert client.get("/api/passwords").status_code == 200
        r = client.get("/api/passwords")

        assert r.status_code == 429
        assert "Too many requests" in r.json()["detail"]

    def test_given_request_succeeds_when_dispatching_should_emit_ratelimit_headers(self, client: TestClient):
        r = client.get("/api/passwords")

        assert r.status_code == 200
        assert r.headers["X-RateLimit-Limit"] == "5"
        assert "X-RateLimit-Remaining" in r.headers

    def test_given_request_blocked_when_dispatching_should_emit_retry_after(self, client: TestClient):
        for _ in range(5):
            client.get("/api/passwords")

        r = client.get("/api/passwords")

        assert r.status_code == 429
        assert int(r.headers["Retry-After"]) > 0


class TestAuthenticatedUserBucket:
    def test_given_valid_access_token_when_dispatching_should_use_per_user_bucket(self):
        user_id = "00000000-0000-0000-0000-000000000001"
        gateway = _FakeTokenGateway()
        gateway.register("token-a", user_id)
        app = _create_app(user_max=3, unauth_max=100, auth_max=100, token_gateway=gateway)

        with TestClient(app) as c:
            c.cookies.set("access_token", "token-a")
            for _ in range(3):
                assert c.get("/api/passwords").status_code == 200
            r = c.get("/api/passwords")

        assert r.status_code == 429

    def test_given_shared_ip_when_dispatching_should_isolate_user_buckets(self):
        """NAT regression: two users on the same IP each get their own bucket."""
        user_a = "00000000-0000-0000-0000-000000000001"
        user_b = "00000000-0000-0000-0000-000000000002"
        gateway = _FakeTokenGateway()
        gateway.register("token-a", user_a)
        gateway.register("token-b", user_b)
        app = _create_app(user_max=3, unauth_max=2, auth_max=100, token_gateway=gateway)

        with TestClient(app) as c_a, TestClient(app) as c_b:
            c_a.cookies.set("access_token", "token-a")
            c_b.cookies.set("access_token", "token-b")
            for _ in range(3):
                assert c_a.get("/api/passwords").status_code == 200
            assert c_a.get("/api/passwords").status_code == 429

            for _ in range(3):
                assert c_b.get("/api/passwords").status_code == 200
            assert c_b.get("/api/passwords").status_code == 429

    def test_given_unknown_token_when_dispatching_should_fall_back_to_ip_bucket(self):
        app = _create_app(user_max=100, unauth_max=3, auth_max=100, token_gateway=_FakeTokenGateway())
        with TestClient(app) as c:
            c.cookies.set("access_token", "not-a-real-token")
            for _ in range(3):
                assert c.get("/api/passwords").status_code == 200
            r = c.get("/api/passwords")

        assert r.status_code == 429


class TestAuthRouteFloor:
    def test_given_login_path_when_dispatching_should_apply_auth_floor(self, client: TestClient):
        for _ in range(3):
            r = client.post("/api/auth/login")
            assert r.status_code == 401  # stub returns 401
        r = client.post("/api/auth/login")

        assert r.status_code == 429

    @pytest.mark.parametrize(
        "method,path",
        [
            ("post", "/api/auth/register-admin"),
            ("post", "/api/auth/refresh-token"),
            ("get", "/api/auth/sso/callback"),
            ("get", "/api/auth/sso/url"),
            ("get", "/api/auth/sso/is-configured"),
        ],
    )
    def test_given_non_login_auth_path_when_dispatching_should_not_consume_auth_floor(self, method: str, path: str):
        """The auth-route floor is narrow by design: only /api/auth/login trips it."""
        app = _create_app(user_max=100, unauth_max=100, auth_max=2, window=60)
        with TestClient(app) as c:
            # Hit the other /auth/* endpoint enough times to exceed auth_max if it were applied.
            for _ in range(5):
                r = getattr(c, method)(path)
                assert r.status_code != 429, f"{method.upper()} {path} unexpectedly hit the auth floor"

            # Meanwhile the auth floor is untouched — 2 logins still pass.
            for _ in range(2):
                assert c.post("/api/auth/login").status_code == 401
            assert c.post("/api/auth/login").status_code == 429

    def test_given_successful_login_when_dispatching_should_consume_both_floor_and_principal_bucket(self):
        app = _create_app(user_max=100, unauth_max=2, auth_max=100, login_status_code=401)
        with TestClient(app) as c:
            for _ in range(2):
                assert c.post("/api/auth/login").status_code == 401
            r = c.post("/api/auth/login")

        # 3rd login: unauth bucket is exhausted (2/2), so the principal bucket blocks even
        # though auth_max=100 would still allow it.
        assert r.status_code == 429


class TestXForwardedFor:
    def test_given_trusted_peer_when_dispatching_should_honor_xff(self):
        """TestClient connects as 'testclient', so mark it as a trusted proxy."""
        app = _create_app(user_max=100, unauth_max=2, auth_max=100, trusted_proxies={"testclient"})
        with TestClient(app) as c:
            for _ in range(2):
                assert c.get("/api/passwords", headers={"X-Forwarded-For": "203.0.113.9"}).status_code == 200
            assert c.get("/api/passwords", headers={"X-Forwarded-For": "203.0.113.9"}).status_code == 429
            # Different XFF → separate bucket
            assert c.get("/api/passwords", headers={"X-Forwarded-For": "203.0.113.10"}).status_code == 200

    def test_given_untrusted_peer_when_dispatching_should_ignore_xff(self):
        """With no trusted proxies, XFF is discarded and all traffic keys on the TCP peer."""
        app = _create_app(user_max=100, unauth_max=2, auth_max=100, trusted_proxies=set())
        with TestClient(app) as c:
            for _ in range(2):
                assert c.get("/api/passwords", headers={"X-Forwarded-For": "203.0.113.9"}).status_code == 200
            # Rotating XFF doesn't help — peer bucket is full
            r = c.get("/api/passwords", headers={"X-Forwarded-For": "203.0.113.10"})

        assert r.status_code == 429


class TestConcurrency:
    def test_given_concurrent_requests_on_shared_bucket_when_dispatching_should_serialize_correctly(self):
        app = _create_app(user_max=100, unauth_max=100, auth_max=3, login_status_code=401)
        with TestClient(app) as c:

            def _post():
                return c.post("/api/auth/login")

            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(_post) for _ in range(10)]
                results = [f.result() for f in as_completed(futures)]

        allowed = [r for r in results if r.status_code != 429]
        limited = [r for r in results if r.status_code == 429]

        assert len(allowed) == 3
        assert len(limited) == 7
