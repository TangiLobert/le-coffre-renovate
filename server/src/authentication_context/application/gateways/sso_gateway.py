from typing import Protocol


class SsoGateway(Protocol):
    async def get_authorize_url(self) -> str: ...
