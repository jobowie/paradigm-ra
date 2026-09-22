import sqlite3

from datetime import datetime, timezone

from ra_platform.organizations.company_profile import (
    OrganizationCompanyProfile,
    OrganizationContact,
)
from ra_platform.organizations.models import (
    Organization,
    OrganizationType,
)
from ra_platform.persistence.organization_details import (
    SQLiteOrganizationCompanyProfileRepository,
    SQLiteOrganizationContactRepository,
)
from ra_platform.persistence.sqlite import (
    initialize_database,
)
from ra_platform.persistence.sqlite_repositories import (
    SQLiteOrganizationRepository,
)


def build_connection():
    connection = sqlite3.connect(
        ":memory:"
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    initialize_database(
        connection
    )

    return connection


def test_company_profile_round_trip():
    connection = build_connection()

    organization = Organization(
        name="Test Client",
        type=OrganizationType.CLIENT,
    )

    SQLiteOrganizationRepository(
        connection
    ).add(
        organization
    )

    profile = OrganizationCompanyProfile(
        organization_id=organization.id,
        business_type="Coffee Shop",
        industry="Food & Beverage",
        website="https://example.com",
        phone="555-0100",
        company_size="11-50",
        address_line1="123 Test Street",
        city="Test City",
        state_region="CA",
        postal_code="90000",
    )

    repository = (
        SQLiteOrganizationCompanyProfileRepository(
            connection
        )
    )

    repository.upsert(
        profile
    )

    loaded = (
        repository.get_for_organization(
            organization.id
        )
    )

    assert loaded is not None
    assert (
        loaded.business_type
        == "Coffee Shop"
    )
    assert (
        loaded.industry
        == "Food & Beverage"
    )
    assert loaded.city == "Test City"


def test_organization_rename_preserves_identity():
    connection = build_connection()

    organization = Organization(
        name="Old Name",
        type=OrganizationType.CLIENT,
    )

    repository = (
        SQLiteOrganizationRepository(
            connection
        )
    )

    repository.add(
        organization
    )

    original_id = organization.id

    organization.name = "New Name"

    organization.updated_at = (
        datetime.now(
            timezone.utc
        )
    )

    repository.update(
        organization
    )

    loaded = repository.get(
        original_id
    )

    assert loaded is not None
    assert loaded.id == original_id
    assert loaded.name == "New Name"


def test_contact_round_trip():
    connection = build_connection()

    organization = Organization(
        name="Test Client",
        type=OrganizationType.CLIENT,
    )

    SQLiteOrganizationRepository(
        connection
    ).add(
        organization
    )

    repository = (
        SQLiteOrganizationContactRepository(
            connection
        )
    )

    contact = OrganizationContact(
        organization_id=organization.id,
        name="Jane Doe",
        title="CFO",
        email="jane@example.com",
        contact_type="billing",
        is_primary=True,
    )

    repository.add(
        contact
    )

    loaded = repository.get(
        contact.id
    )

    assert loaded is not None
    assert loaded.name == "Jane Doe"
    assert loaded.is_primary is True


def test_only_one_primary_contact():
    connection = build_connection()

    organization = Organization(
        name="Test Client",
        type=OrganizationType.CLIENT,
    )

    SQLiteOrganizationRepository(
        connection
    ).add(
        organization
    )

    repository = (
        SQLiteOrganizationContactRepository(
            connection
        )
    )

    first = OrganizationContact(
        organization_id=organization.id,
        name="First Contact",
        is_primary=True,
    )

    second = OrganizationContact(
        organization_id=organization.id,
        name="Second Contact",
        is_primary=True,
    )

    repository.add(
        first
    )

    repository.add(
        second
    )

    contacts = (
        repository.list_for_organization(
            organization.id
        )
    )

    primary = [
        item
        for item in contacts
        if item.is_primary
    ]

    assert len(primary) == 1
    assert primary[0].id == second.id
