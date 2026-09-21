import sqlite3

import pytest

from ra_platform.identity.models import (
    MembershipRole,
)
from ra_platform.persistence.sqlite import (
    initialize_database,
)
from ra_platform.persistence.sqlite_repositories import (
    SQLiteAuditEventRepository,
    SQLiteOrganizationMembershipRepository,
    SQLiteUserRepository,
)
from ra_platform.scripts.bootstrap_internal_user import (
    bootstrap_internal_user,
)


def make_connection():
    connection = sqlite3.connect(
        ":memory:"
    )
    connection.row_factory = sqlite3.Row

    initialize_database(connection)

    return connection


def test_bootstrap_internal_admin_with_permanent_password():
    connection = make_connection()

    user = bootstrap_internal_user(
        connection=connection,
        email="ADMIN@PARADIGMRA.TECH",
        display_name="Platform Admin",
        password="secure-test-password",
        role=(
            MembershipRole.PARADIGM_RA_ADMIN
        ),
        must_change_password=False,
    )

    users = SQLiteUserRepository(
        connection
    )

    memberships = (
        SQLiteOrganizationMembershipRepository(
            connection
        )
    )

    stored = users.get_by_email(
        "admin@paradigmra.tech"
    )

    assert stored is not None
    assert stored.id == user.id

    assert stored.password_hash != (
        "secure-test-password"
    )

    assert (
        stored.must_change_password
        is False
    )

    stored_memberships = (
        memberships.list_for_user(
            user.id
        )
    )

    assert len(stored_memberships) == 1

    assert (
        stored_memberships[0].role
        == MembershipRole.PARADIGM_RA_ADMIN
    )


def test_bootstrap_executive_defaults_to_temporary_password():
    connection = make_connection()

    user = bootstrap_internal_user(
        connection=connection,
        email="ceo@paradigmra.tech",
        display_name="CEO",
        password="secure-test-password",
        role=(
            MembershipRole
            .PARADIGM_RA_EXECUTIVE
        ),
    )

    users = SQLiteUserRepository(
        connection
    )

    stored = users.get(
        user.id
    )

    assert stored is not None

    assert (
        stored.must_change_password
        is True
    )

    memberships = (
        SQLiteOrganizationMembershipRepository(
            connection
        )
    )

    membership = memberships.list_for_user(
        user.id
    )[0]

    assert membership.role == (
        MembershipRole
        .PARADIGM_RA_EXECUTIVE
    )


def test_bootstrap_rejects_duplicate_email():
    connection = make_connection()

    bootstrap_internal_user(
        connection=connection,
        email="admin@paradigmra.tech",
        display_name="Admin",
        password="secure-test-password",
        role=(
            MembershipRole.PARADIGM_RA_ADMIN
        ),
    )

    with pytest.raises(
        ValueError,
        match="already exists",
    ):
        bootstrap_internal_user(
            connection=connection,
            email="ADMIN@PARADIGMRA.TECH",
            display_name="Duplicate",
            password="another-secure-password",
            role=(
                MembershipRole
                .PARADIGM_RA_EXECUTIVE
            ),
        )


def test_bootstrap_creates_audit_event():
    connection = make_connection()

    user = bootstrap_internal_user(
        connection=connection,
        email="admin@paradigmra.tech",
        display_name="Admin",
        password="secure-test-password",
        role=(
            MembershipRole.PARADIGM_RA_ADMIN
        ),
    )

    membership = (
        SQLiteOrganizationMembershipRepository(
            connection
        ).list_for_user(
            user.id
        )[0]
    )

    events = (
        SQLiteAuditEventRepository(
            connection
        ).list_for_organization(
            membership.organization_id
        )
    )

    assert len(events) == 1

    assert events[0].action == (
        "identity.user_bootstrapped"
    )

    assert events[0].resource_id == (
        user.id
    )

    assert (
        '"must_change_password": true'
        in events[0].metadata_json
    )
