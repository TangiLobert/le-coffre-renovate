from src.vault_management_context.business_logic.gateways import VaultRepository


class VaultStatusUseCase:
    def __init__(self, vault_repository: VaultRepository):
        self.vault_repository = vault_repository

    def execute(self) -> bool:
        return self.vault_repository.get() is not None
