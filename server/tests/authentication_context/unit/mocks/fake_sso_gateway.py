class FakeSsoGateway:
    def __init__(self):
        self._authorize_url = ""

    async def get_authorize_url(self) -> str:
        return self._authorize_url

    def set_authorize_url(self, url: str) -> None:
        """Helper method for tests to set the URL that will be returned"""
        self._authorize_url = url
