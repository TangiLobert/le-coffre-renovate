from typing import List, Optional

from vault_management_context.domain.models import Vault, Share


class VaultCreationService:
    @staticmethod
    def pre_check(existing_vault: Optional[Vault]):
        if existing_vault is not None:
            raise ValueError("Already setup")

    @staticmethod
    def create_vault(nb_shares: int, threshold: int, shares: List[Share]) -> Vault:
        if nb_shares < 2:
            raise ValueError("Number of shares must be at least 2")
        if threshold < 2:
            raise ValueError("Threshold must be at least 2")
        if threshold > nb_shares:
            raise ValueError("Threshold cannot be greater than number of shares")

        return Vault(nb_shares=nb_shares, threshold=threshold, shares=shares)
