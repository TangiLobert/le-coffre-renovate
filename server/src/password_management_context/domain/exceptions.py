from uuid import UUID


class PasswordManagementDomainError(Exception):
    """Base exception for all password management domain errors"""

    pass


class PasswordNotFoundError(PasswordManagementDomainError):
    """Raised when attempting to get a password not existing"""

    def __init__(self, uuid: UUID):
        super().__init__(f"The requested password with ID {uuid} was not found")
