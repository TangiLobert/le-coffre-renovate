from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class PasswordMetadataResponse:
    id: UUID
    name: str
    folder: Optional[str] = None
