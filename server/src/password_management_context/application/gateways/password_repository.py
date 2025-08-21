from typing import Optional, Protocol


class PasswordRepository(Protocol):
    def save(self, name: str, value: str, folder: Optional[str]): ...

    def get(self, name: str, folder: Optional[str]) -> str: ...
