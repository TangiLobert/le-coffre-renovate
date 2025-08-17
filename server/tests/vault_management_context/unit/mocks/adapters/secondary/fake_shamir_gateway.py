from typing import List

from vault_management_context.domain.entities.share import Share
from vault_management_context.domain.value_objects import VaultConfiguration
from vault_management_context.domain.value_objects.shamir_result import ShamirResult
from vault_management_context.application.gateways import (
    ShamirGateway,
)


class FakeShamirGateway(ShamirGateway):
    def __init__(self):
        self._shamir_result = None
        self._reconstructed_secret = None
        self._reconstruction_failure = False

    def set_shamir_result(self, result: ShamirResult) -> None:
        self._shamir_result = result

    def create_shares(self, configuration: VaultConfiguration) -> ShamirResult:
        if self._shamir_result is None:
            raise ValueError("No shamir result configured")
        return self._shamir_result

    def set_reconstructed_secret(self, secret: str) -> None:
        self._reconstructed_secret = secret

    def set_reconstruction_failure(self, should_fail: bool) -> None:
        self._reconstruction_failure = should_fail

    def reconstruct_secret(self, shares: List[Share]) -> str:
        if self._reconstruction_failure:
            raise ValueError("Reconstruction failed")

        if self._reconstructed_secret is None:
            raise ValueError("No reconstructed secret configured")

        return self._reconstructed_secret
