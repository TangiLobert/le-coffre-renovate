from typing import List

from vault_management_context.domain.entities.share import Share
from vault_management_context.domain.value_objects import VaultConfiguration
from vault_management_context.application.gateways import (
    ShamirGateway,
)


class FakeShamirGateway(ShamirGateway):
    def __init__(self):
        self.shares = []
        self._reconstructed_secret = None
        self._reconstruction_failure = False

    def set(self, shares: List[Share]) -> None:
        self.shares = shares

    def split_secret(self, configuration: VaultConfiguration) -> List[Share]:
        return self.shares

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
