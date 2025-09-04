class FakePasswordHashingGateway:
    def hash_password(self, password: str) -> str:
        return f"hashed({password})"

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return f"hashed({password})" == hashed_password
