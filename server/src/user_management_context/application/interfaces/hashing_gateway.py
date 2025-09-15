from typing import Protocol


class HashingGateway(Protocol):
    def hash(self, password: str) -> str:
        ...

    def compare(self, plain_password: str, hashed_password: str) -> bool:
        ...
