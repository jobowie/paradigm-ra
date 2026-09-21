import argparse
import getpass
import json
import sqlite3

from uuid import UUID

from ra_platform.api.dependencies import (
    get_database_path,
)
from ra_platform.identity.models import (
    AuditEvent,
    MembershipRole,
    OrganizationMembership,
    User,
)
from ra_platform.organizations.models import (
    Organization,
    OrganizationType,
)
from ra_platform.persistence.sqlite import (
    create_connection,
    initialize_database,
)
from ra_platform.persistence.sqlite_repositories import (
    SQLiteAuditEventRepository,
    SQLiteOrganizationMembershipRepository,
    SQLiteOrganizationRepository,
    SQLiteUserRepository,
)
from ra_platform.security.auth import (
    hash_password,
)


INTERNAL_ROLES = {
    MembershipRole.PARADIGM_RA_ADMIN,
    MembershipRole.PARADIGM_RA_EXECUTIVE,
}


def get_or_create_paradigm_ra(
    connection: sqlite3.Connection,
) -> Organization:
    row = connection.execute(
        """
        SELECT id
        FROM organizations
        WHERE lower(name) = lower(?)
          AND type = ?
        LIMIT 1
        """,
        (
            "Paradigm Ra",
            OrganizationType.PARADIGM_RA.value,
        ),
    ).fetchone()

    repository = SQLiteOrganizationRepository(
        connection
    )

    if row is not None:
        organization = repository.get(
            UUID(row["id"])
        )

        if organization is None:
            raise RuntimeError(
                "Paradigm Ra organization lookup failed."
            )

        return organization

    organization = Organization(
        name="Paradigm Ra",
        type=OrganizationType.PARADIGM_RA,
    )

    repository.add(organization)

    return organization


def bootstrap_internal_user(
    *,
    connection: sqlite3.Connection,
    email: str,
    display_name: str,
    password: str,
    role: MembershipRole,
    must_change_password: bool = True,
) -> User:
    if role not in INTERNAL_ROLES:
        raise ValueError(
            "Only Paradigm Ra internal roles "
            "may be bootstrapped here."
        )

    normalized_email = (
        email.strip().lower()
    )

    if len(password) < 12:
        raise ValueError(
            "Password must be at least "
            "12 characters."
        )

    users = SQLiteUserRepository(
        connection
    )

    existing = users.get_by_email(
        normalized_email
    )

    if existing is not None:
        raise ValueError(
            "A user with that email "
            "already exists."
        )

    paradigm_ra = get_or_create_paradigm_ra(
        connection
    )

    user = User(
        email=normalized_email,
        display_name=display_name.strip(),
        password_hash=hash_password(
            password
        ),
        must_change_password=(
            must_change_password
        ),
    )

    users.add(user)

    memberships = (
        SQLiteOrganizationMembershipRepository(
            connection
        )
    )

    memberships.add(
        OrganizationMembership(
            user_id=user.id,
            organization_id=paradigm_ra.id,
            role=role,
        )
    )

    audit = SQLiteAuditEventRepository(
        connection
    )

    audit.add(
        AuditEvent(
            actor_user_id=None,
            organization_id=paradigm_ra.id,
            action="identity.user_bootstrapped",
            resource_type="user",
            resource_id=user.id,
            metadata_json=json.dumps(
                {
                    "email":
                        normalized_email,
                    "role":
                        role.value,
                    "must_change_password":
                        must_change_password,
                },
                sort_keys=True,
            ),
        )
    )

    connection.commit()

    return user


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Create a Paradigm Ra "
            "internal platform user."
        )
    )

    parser.add_argument(
        "--email",
        required=True,
    )

    parser.add_argument(
        "--display-name",
        required=True,
    )

    parser.add_argument(
        "--role",
        required=True,
        choices=[
            MembershipRole
            .PARADIGM_RA_ADMIN.value,
            MembershipRole
            .PARADIGM_RA_EXECUTIVE.value,
        ],
    )

    parser.add_argument(
        "--permanent-password",
        action="store_true",
        help=(
            "Do not require a password "
            "change on first login."
        ),
    )

    args = parser.parse_args()

    password = getpass.getpass(
        "Password: "
    )

    confirmation = getpass.getpass(
        "Confirm password: "
    )

    if password != confirmation:
        raise SystemExit(
            "Passwords do not match."
        )

    connection = create_connection(
        get_database_path()
    )

    initialize_database(connection)

    try:
        user = bootstrap_internal_user(
            connection=connection,
            email=args.email,
            display_name=args.display_name,
            password=password,
            role=MembershipRole(
                args.role
            ),
            must_change_password=(
                not args.permanent_password
            ),
        )

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    print(
        "Created internal user:"
    )
    print(
        f"  id: {user.id}"
    )
    print(
        f"  email: {user.email}"
    )
    print(
        f"  role: {args.role}"
    )

    print(
        "  password mode: "
        + (
            "permanent"
            if args.permanent_password
            else "temporary"
        )
    )


if __name__ == "__main__":
    main()
