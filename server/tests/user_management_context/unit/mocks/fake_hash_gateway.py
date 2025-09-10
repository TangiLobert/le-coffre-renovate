from user_management_context.application.interfaces.haching_gateway import (
  HashingGateway
)


class FakeHashingGateway(HashingGateway):

    def hash(self, password: str) -> str:
        return f"hashed({password})"
    
    def compare(self, plain_password: str, hashed_password: str) -> bool:
        return hashed_password == self.hash(plain_password)
