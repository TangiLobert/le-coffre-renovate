from Crypto.Random import get_random_bytes
from Crypto.Protocol.SecretSharing import Shamir
from typing import List

from vault_management_context.domain.models.share import Share
from vault_management_context.application.gateways import (
    ShamirGateway,
)


class CryptoShamirGateway(ShamirGateway):
    def split_secret(self, nb_shares: int, threshold: int) -> List[Share]:
        secret = get_random_bytes(16)

        shares = Shamir.split(threshold, nb_shares, secret, False)

        return [Share(share[0], share[1].hex()) for share in shares]
