from typing import List, Dict, Any, Protocol


class AuditLoggerGateway(Protocol):
    def get_logs(self) -> List[Dict[str, Any]]: ...
