"""Hierarchical access-control policies for user-account operations."""

from app.core.exceptions import AuthorizationError
from app.models.user import User, UserRole


class UserAccessPolicy:
    """
    Encapsulates the pure authorization rules governing user-account operations.

    All guarded mutations follow a hierarchical dominance invariant over role
    ranks with self-operation parity: an actor may always act on their own
    account, while third-party operations require a strictly higher rank.
    Failures are raised as AuthorizationError domain exceptions so the service
    layer remains transport-agnostic.
    """

    _ROLE_RANK = {UserRole.tourist: 0, UserRole.admin: 1, UserRole.superadmin: 2}

    def assert_can_delete(self, actor: User, target: User) -> None:
        """
        Enforces the deletion invariant: self-deletion parity or strictly
        higher rank over the target.

        Args:
            actor (User): The authenticated user attempting the deletion.
            target (User): The account to be deleted.

        Raises:
            AuthorizationError: When the actor neither deletes their own
                account nor outranks the target.
        """
        is_self_deletion = actor.cedula == target.cedula
        actor_outranks_target = self._ROLE_RANK[actor.role] > self._ROLE_RANK[target.role]

        if not is_self_deletion and not actor_outranks_target:
            raise AuthorizationError(
                "Privilegios insuficientes o violación de jerarquía. No tiene autorización para eliminar esta cuenta."
            )

    def assert_can_update(self, actor: User, target: User, update_dict: dict) -> None:
        """
        Enforces update invariants: self-update parity or strictly higher rank,
        plus fail-safe guards blocking role mutations for non-superadmins and
        is_active mutations for tourists.

        Args:
            actor (User): The authenticated user attempting the mutation.
            target (User): The account to be updated.
            update_dict (dict): The set of explicitly provided scalar fields.

        Raises:
            AuthorizationError: When the hierarchical invariant or any
                fail-safe field invariant is violated.
        """
        is_self_update = actor.cedula == target.cedula

        if not is_self_update and self._ROLE_RANK[actor.role] <= self._ROLE_RANK[target.role]:
            raise AuthorizationError(
                "Violación de jerarquía: No tiene privilegios para modificar a este usuario."
            )

        if "role" in update_dict and actor.role != UserRole.superadmin:
            raise AuthorizationError(
                "Violación de jerarquía: Solo un superadministrador puede modificar roles."
            )

        if "is_active" in update_dict and actor.role == UserRole.tourist:
            raise AuthorizationError(
                "Privilegios insuficientes. No tiene permisos para modificar el estado de la cuenta."
            )

    def assert_can_recover(self, actor: User, target: User) -> None:
        """
        Enforces recovery precedence: standard admins cannot restore accounts
        of equal or higher tier.

        Args:
            actor (User): The authenticated administrator executing the recovery.
            target (User): The soft-deleted account to be restored.

        Raises:
            AuthorizationError: When a standard admin attempts to recover an
                admin or superadmin account.
        """
        if actor.role == UserRole.admin and target.role in [UserRole.admin, UserRole.superadmin]:
            raise AuthorizationError(
                "Violación de jerarquía: No tiene autorización para recuperar esta cuenta."
            )

    def assert_can_provision_admin(self, actor: User) -> None:
        """
        Enforces provisioning governance: only superadmins may create
        administrative accounts.

        Args:
            actor (User): The authenticated user attempting the provisioning.

        Raises:
            AuthorizationError: When the requester is not a superadmin.
        """
        if actor.role != UserRole.superadmin:
            raise AuthorizationError(
                "Violación de jerarquía: Solo un Superusuario puede aprovisionar cuentas administrativas."
            )

    def can_see(self, viewer_role: UserRole, subject_role: UserRole) -> bool:
        """
        Determines whether a viewer role may see a subject role in directory
        listings.

        Args:
            viewer_role (UserRole): Role of the authenticated actor requesting
                the listing.
            subject_role (UserRole): Role of the entity being listed.

        Returns:
            bool: True when the subject is visible to the viewer; False when
                obscured (standard admins cannot see superadmins).
        """
        return not (viewer_role == UserRole.admin and subject_role == UserRole.superadmin)
