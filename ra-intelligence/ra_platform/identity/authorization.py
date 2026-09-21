from enum import Enum
from uuid import UUID

from ra_platform.identity.models import (
    MembershipRole,
)
from ra_platform.identity.service import (
    AuthenticatedPrincipal,
)


class Permission(str, Enum):
    VIEW_PLATFORM = "view_platform"

    VIEW_ORGANIZATION = "view_organization"
    VIEW_ENGAGEMENT = "view_engagement"
    VIEW_BILLING = "view_billing"
    VIEW_AUDIT = "view_audit"

    CREATE_QUOTE = "create_quote"
    SEND_QUOTE = "send_quote"

    CREATE_INVOICE = "create_invoice"
    SEND_INVOICE = "send_invoice"

    RECORD_PAYMENT = "record_payment"

    MANAGE_USERS = "manage_users"
    MANAGE_MEMBERSHIPS = "manage_memberships"
    MANAGE_SECURITY = "manage_security"


BUSINESS_OPERATIONS = {
    Permission.VIEW_PLATFORM,
    Permission.VIEW_ORGANIZATION,
    Permission.VIEW_ENGAGEMENT,
    Permission.VIEW_BILLING,
    Permission.VIEW_AUDIT,
    Permission.CREATE_QUOTE,
    Permission.SEND_QUOTE,
    Permission.CREATE_INVOICE,
    Permission.SEND_INVOICE,
    Permission.RECORD_PAYMENT,
}


ROLE_PERMISSIONS: dict[
    MembershipRole,
    set[Permission],
] = {
    MembershipRole.PARADIGM_RA_ADMIN: {
        *BUSINESS_OPERATIONS,
        Permission.MANAGE_USERS,
        Permission.MANAGE_MEMBERSHIPS,
        Permission.MANAGE_SECURITY,
    },

    MembershipRole.PARADIGM_RA_EXECUTIVE: {
        *BUSINESS_OPERATIONS,
    },

    MembershipRole.CLIENT_ADMIN: {
        Permission.VIEW_ORGANIZATION,
        Permission.VIEW_ENGAGEMENT,
        Permission.VIEW_BILLING,
    },

    MembershipRole.PARTNER_ADMIN: set(),
}


PLATFORM_ROLES = {
    MembershipRole.PARADIGM_RA_ADMIN,
    MembershipRole.PARADIGM_RA_EXECUTIVE,
}


class AuthorizationError(Exception):
    pass


def authorize(
    *,
    principal: AuthenticatedPrincipal,
    permission: Permission,
    organization_id: UUID | None = None,
) -> None:
    for membership in principal.memberships:
        if (
            membership.role in PLATFORM_ROLES
            and permission
            in ROLE_PERMISSIONS[membership.role]
        ):
            return

    if organization_id is None:
        raise AuthorizationError(
            "Permission denied."
        )

    for membership in principal.memberships:
        if (
            membership.organization_id
            == organization_id
            and permission
            in ROLE_PERMISSIONS[membership.role]
        ):
            return

    raise AuthorizationError(
        "Permission denied."
    )
