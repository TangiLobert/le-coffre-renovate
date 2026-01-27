class LogRepo:
    def __init__(self):
        self.logs: list = []

    def append_event(self, event):
        self.logs.append(event)


class StoreEventUseCase:
    def __init__(self, log_repo: LogRepo):
        self.log_repo = log_repo

    def execute(self, event):
        self.log_repo.append_event(event)
