from typing import Optional, Protocol

from vault_management_context.domain.models import (
    Vault,
)


class VaultRepository(Protocol):
    def get(self) -> Optional[Vault]: ...
    def save(self, vault: Vault) -> None: ...
