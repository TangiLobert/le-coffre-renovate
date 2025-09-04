from uuid import UUID

from rights_access_context.application.gateways import (
    RightsRepository,
)
from rights_access_context.application.responses import AccessResult, Granted
from rights_access_context.domain.value_objects import Permission


class CheckAccessUseCase:
    def __init__(self, rights_repository: RightsRepository):
        self.rights_repository = rights_repository

    def execute(
        self, user_id: UUID, resource_id: UUID, permission: Permission = Permission.READ
    ) -> AccessResult:
        # Récupère toutes les permissions du user sur la ressource
        all_permissions = self.rights_repository.get_all_permissions(
            user_id, resource_id
        )
        print("all_permissions", all_permissions)

        if not all_permissions:
            # Aucune permission trouvée → NotFound
            return AccessResult(granted=Granted.NOT_FOUND)

        if permission in all_permissions:
            # Permission demandée accordée
            return AccessResult(granted=Granted.ACCESS)

        if Permission.READ in all_permissions:
            # Pas la permission demandée, mais au moins la lecture → ViewOnly
            return AccessResult(granted=Granted.VIEW_ONLY)

        # Cas de fallback si aucune condition match
        return AccessResult(granted=Granted.NOT_FOUND)
