from audit_logging_context.adapters.secondary import (
    InMemoryAuditLogger,
)


class ListAuditLogsUseCase:
    def __init__(self, audit_logger: InMemoryAuditLogger):
        self._audit_logger = audit_logger

    def execute(self):
        return self._audit_logger.get_logs()
