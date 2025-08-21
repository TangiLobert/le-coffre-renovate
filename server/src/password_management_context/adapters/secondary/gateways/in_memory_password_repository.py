from typing import Optional, Dict, Tuple
from password_management_context.application.gateways import PasswordRepository


class InMemoryPasswordRepository(PasswordRepository):
    def __init__(self):
        self.storage: Dict[Tuple[Optional[str], str], str] = {}

    def save(self, name: str, value: str, folder: Optional[str] = None):
        self.storage[(folder, name)] = value

    def get(self, name: str, folder: Optional[str] = None) -> str:
        return self.storage.get((folder, name), "")
