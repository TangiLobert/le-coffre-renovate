from unittest.mock import patch

import pytest
from identity_access_management_context.adapters.secondary.in_memory_login_lockout_gateway import (
    InMemoryLoginLockoutGateway,
)


@pytest.fixture
def gateway() -> InMemoryLoginLockoutGateway:
    return InMemoryLoginLockoutGateway(max_failures=3, lockout_seconds=60)


class TestInMemoryLoginLockoutGateway:
    def test_should_report_unknown_email_as_not_locked(self, gateway: InMemoryLoginLockoutGateway):
        assert gateway.is_locked("unknown@lecoffre.com") is None

    def test_should_not_lock_below_threshold(self, gateway: InMemoryLoginLockoutGateway):
        for _ in range(2):
            gateway.record_failed_login("alice@lecoffre.com")

        assert gateway.is_locked("alice@lecoffre.com") is None

    def test_should_lock_when_max_failures_reached(self, gateway: InMemoryLoginLockoutGateway):
        base_time = 1000.0
        with patch(
            "identity_access_management_context.adapters.secondary.in_memory_login_lockout_gateway.time.monotonic",
            return_value=base_time,
        ):
            for _ in range(3):
                gateway.record_failed_login("alice@lecoffre.com")
            assert gateway.is_locked("alice@lecoffre.com") == 60

    def test_should_report_remaining_lockout_seconds(self, gateway: InMemoryLoginLockoutGateway):
        base_time = 1000.0
        patch_path = (
            "identity_access_management_context.adapters.secondary.in_memory_login_lockout_gateway.time.monotonic"
        )
        with patch(patch_path, return_value=base_time):
            for _ in range(3):
                gateway.record_failed_login("alice@lecoffre.com")

        with patch(patch_path, return_value=base_time + 45):
            assert gateway.is_locked("alice@lecoffre.com") == 15

    def test_should_unlock_after_lockout_duration_elapses(self, gateway: InMemoryLoginLockoutGateway):
        base_time = 1000.0
        patch_path = (
            "identity_access_management_context.adapters.secondary.in_memory_login_lockout_gateway.time.monotonic"
        )
        with patch(patch_path, return_value=base_time):
            for _ in range(3):
                gateway.record_failed_login("alice@lecoffre.com")

        with patch(patch_path, return_value=base_time + 61):
            assert gateway.is_locked("alice@lecoffre.com") is None

    def test_should_reset_counter_after_lockout_applied_so_fresh_sequence_is_required(
        self, gateway: InMemoryLoginLockoutGateway
    ):
        base_time = 1000.0
        patch_path = (
            "identity_access_management_context.adapters.secondary.in_memory_login_lockout_gateway.time.monotonic"
        )
        with patch(patch_path, return_value=base_time):
            for _ in range(3):
                gateway.record_failed_login("alice@lecoffre.com")

        with patch(patch_path, return_value=base_time + 61):
            gateway.record_failed_login("alice@lecoffre.com")
            assert gateway.is_locked("alice@lecoffre.com") is None

    def test_should_clear_lockout_state_on_successful_login(self, gateway: InMemoryLoginLockoutGateway):
        for _ in range(2):
            gateway.record_failed_login("alice@lecoffre.com")

        gateway.record_successful_login("alice@lecoffre.com")

        for _ in range(2):
            gateway.record_failed_login("alice@lecoffre.com")

        assert gateway.is_locked("alice@lecoffre.com") is None

    def test_should_keep_counters_independent_across_emails(self, gateway: InMemoryLoginLockoutGateway):
        for _ in range(3):
            gateway.record_failed_login("alice@lecoffre.com")

        assert gateway.is_locked("bob@lecoffre.com") is None

    @pytest.mark.parametrize(
        "stored_email,queried_email",
        [
            ("Alice@Example.com", "alice@example.com"),
            ("  bob@example.com  ", "bob@example.com"),
            ("CAROL@EXAMPLE.COM", "carol@example.com"),
        ],
    )
    def test_should_normalize_email_case_and_whitespace(
        self, gateway: InMemoryLoginLockoutGateway, stored_email: str, queried_email: str
    ):
        for _ in range(3):
            gateway.record_failed_login(stored_email)

        assert gateway.is_locked(queried_email) is not None

    def test_should_reject_instantiation_with_zero_max_failures(self):
        with pytest.raises(ValueError, match="max_failures"):
            InMemoryLoginLockoutGateway(max_failures=0, lockout_seconds=60)

    def test_should_reject_instantiation_with_zero_lockout_seconds(self):
        with pytest.raises(ValueError, match="lockout_seconds"):
            InMemoryLoginLockoutGateway(max_failures=3, lockout_seconds=0)
