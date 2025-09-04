from typing import Protocol


class PasswordHashingGateway(Protocol):
    def hash_password(self, password: str) -> str:
        """Hash a plain text password securely"""
        ...

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        ...
