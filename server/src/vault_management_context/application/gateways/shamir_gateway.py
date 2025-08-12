from typing import Protocol
from typing import List
from vault_management_context.domain.models import Share


class ShamirGateway(Protocol):
    def split_secret(self, nb_shares: int, threshold: int) -> List[Share]: ...
