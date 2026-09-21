from datetime import (
    datetime,
    timedelta,
    timezone,
)
from uuid import uuid4

import pytest

from ra_platform.identity.authorization import (
    AuthorizationError,
    Permission,
    authorize,
)
from ra_platform.identity.models import (
    AuthSession,
    MembershipRole,
    OrganizationMembership,
    User,
)
from ra_platform.identity.service import (
    AuthenticatedPrincipal,
)


def make_principal(
    *,
    role: MembershipRole,
    organization_id=None,
):
    organization_id = (
        organization_id
        or uuid4()
    )

    user = User(
        email=f"{uuid4()}@example.com",
        display_name="Test User",
        password_hash="test-hash",
    )

    membership = OrganizationMembership(
        user_id=user.id,
        organization_id=organization_id,
        role=role,
    )

    session = AuthSession(
        user_id=user.id,
        token_hash="test-token-hash",
        expires_at=(
            datetime.now(timezone.utc)
            + timedelta(hours=1)
        ),
    )

    principal = AuthenticatedPrincipal(
        user=user,
        memberships=[membership],
        session=session,
    )

    return principal, organization_id


def test_admin_can_view_other_client():
    principal, _ = make_principal(
        role=(
            MembershipRole.PARADIGM_RA_ADMIN
        )
    )

    authorize(
        principal=principal,
        permission=Permission.VIEW_BILLING,
        organization_id=uuid4(),
    )


def test_admin_can_create_invoice():
    principal, _ = make_principal(
        role=(
            MembershipRole.PARADIGM_RA_ADMIN
        )
    )

    authorize(
        principal=principal,
        permission=Permission.CREATE_INVOICE,
        organization_id=uuid4(),
    )


def test_executive_can_view_billing():
    principal, _ = make_principal(
        role=(
            MembershipRole
            .PARADIGM_RA_EXECUTIVE
        )
    )

    authorize(
        principal=principal,
        permission=Permission.VIEW_BILLING,
        organization_id=uuid4(),
    )


def test_executive_can_create_invoice():
    principal, _ = make_principal(
        role=(
            MembershipRole
            .PARADIGM_RA_EXECUTIVE
        )
    )

    authorize(
        principal=principal,
        permission=Permission.CREATE_INVOICE,
        organization_id=uuid4(),
    )


def test_executive_can_create_quote():
    principal, _ = make_principal(
        role=(
            MembershipRole
            .PARADIGM_RA_EXECUTIVE
        )
    )

    authorize(
        principal=principal,
        permission=Permission.CREATE_QUOTE,
        organization_id=uuid4(),
    )


def test_executive_can_record_payment():
    principal, _ = make_principal(
        role=(
            MembershipRole
            .PARADIGM_RA_EXECUTIVE
        )
    )

    authorize(
        principal=principal,
        permission=Permission.RECORD_PAYMENT,
        organization_id=uuid4(),
    )


def test_executive_cannot_manage_users():
    principal, _ = make_principal(
        role=(
            MembershipRole
            .PARADIGM_RA_EXECUTIVE
        )
    )

    with pytest.raises(
        AuthorizationError
    ):
        authorize(
            principal=principal,
            permission=Permission.MANAGE_USERS,
        )


def test_client_admin_can_view_own_billing():
    principal, organization_id = (
        make_principal(
            role=MembershipRole.CLIENT_ADMIN
        )
    )

    authorize(
        principal=principal,
        permission=Permission.VIEW_BILLING,
        organization_id=organization_id,
    )


def test_client_admin_cannot_view_other_client():
    principal, _ = make_principal(
        role=MembershipRole.CLIENT_ADMIN
    )

    with pytest.raises(
        AuthorizationError
    ):
        authorize(
            principal=principal,
            permission=Permission.VIEW_BILLING,
            organization_id=uuid4(),
        )


def test_client_admin_cannot_create_invoice():
    principal, organization_id = (
        make_principal(
            role=MembershipRole.CLIENT_ADMIN
        )
    )

    with pytest.raises(
        AuthorizationError
    ):
        authorize(
            principal=principal,
            permission=Permission.CREATE_INVOICE,
            organization_id=organization_id,
        )


def test_partner_admin_gets_no_brewbird_permissions():
    principal, organization_id = (
        make_principal(
            role=MembershipRole.PARTNER_ADMIN
        )
    )

    with pytest.raises(
        AuthorizationError
    ):
        authorize(
            principal=principal,
            permission=Permission.VIEW_BILLING,
            organization_id=organization_id,
        )
