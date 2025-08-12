from typing import List

from vault_management_context.domain.entities.share import Share
from vault_management_context.domain.value_objects import VaultConfiguration
from vault_management_context.application.gateways import (
    ShamirGateway,
)


class FakeShamirGateway(ShamirGateway):
    def set(self, shares: List[Share]) -> None:
        self.shares = shares

    def split_secret(self, configuration: VaultConfiguration) -> List[Share]:
        return self.shares
