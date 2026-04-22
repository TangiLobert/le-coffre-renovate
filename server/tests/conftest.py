import os
import secrets

import pytest


@pytest.fixture(scope="session")
def env_vars():
    os.environ["JWT_SECRET_KEY"] = secrets.token_urlsafe(32)
    os.environ["JWT_ALGORITHM"] = "HS256"
    # Use very high rate limits so e2e tests aren't impacted by incidental traffic;
    # the dedicated rate-limit workflow overrides these on app.state for its scenarios.
    os.environ["RATE_LIMIT_USER_MAX_REQUESTS"] = "10000"
    os.environ["RATE_LIMIT_UNAUTH_MAX_REQUESTS"] = "10000"
    os.environ["RATE_LIMIT_AUTH_MAX_REQUESTS"] = "10000"
    # Login lockout thresholds keep config.py defaults (5 failures / 300s) so the
    # authentication-workflow PHASE 7 can exercise real lockout behavior end-to-end.
    yield
    for key in (
        "JWT_SECRET_KEY",
        "JWT_ALGORITHM",
        "RATE_LIMIT_USER_MAX_REQUESTS",
        "RATE_LIMIT_UNAUTH_MAX_REQUESTS",
        "RATE_LIMIT_AUTH_MAX_REQUESTS",
    ):
        os.environ.pop(key, None)
