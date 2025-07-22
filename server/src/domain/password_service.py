import random
import string


class PasswordService:
    def generate_password(self, length: int) -> str:
        if length <= 8:
            raise ValueError("Password length must be at least 9 characters.")
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))
