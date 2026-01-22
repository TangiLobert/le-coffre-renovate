from audit_logging_context.application.gateways import (
    AuditLoggerGateway,
)


class ListAuditLogsUseCase:
    def __init__(self, audit_logger: AuditLoggerGateway):
        self._audit_logger = audit_logger

    def execute(self):
        return self._audit_logger.get_logs()
