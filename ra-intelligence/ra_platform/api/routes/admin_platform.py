import json
import sqlite3

from datetime import date, datetime, timezone
from decimal import Decimal

from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from pydantic import (
    BaseModel,
    Field,
)

from ra_platform.api.auth import (
    get_current_principal,
)
from ra_platform.billing.models import (
    BillingCadence,
    BillingType,
    EngagementBillingTerms,
    Invoice,
    TimeEntry,
    TimeEntryFriction,
    TimeEntryStatus,
    TimeEntryWorkstream,
)
from ra_platform.billing.numbering import (
    invoice_prefix_for_organization_name,
    next_invoice_number,
)
from ra_platform.billing.terms_service import (
    BillingTermsValidationError,
    prepare_successor_billing_terms,
)
from ra_platform.billing.service import (
    approve_time_entry,
    reopen_time_entry,
    create_invoice_from_time_entries,
)
from ra_platform.api.dependencies import (
    get_database_connection,
)
from ra_platform.identity.authorization import (
    AuthorizationError,
    Permission,
    authorize,
)
from ra_platform.identity.service import (
    AuthenticatedPrincipal,
)
from ra_platform.engagements.models import (
    Engagement,
    EngagementSource,
    EngagementStatus,
)
from ra_platform.organizations.company_profile import (
    OrganizationCompanyProfile,
    OrganizationContact,
)
from ra_platform.organizations.billing_profile import (
    OrganizationBillingProfile,
)
from ra_platform.organizations.billing_profile_service import (
    BillingProfileUpdateError,
    update_organization_billing_profile,
)
from ra_platform.organizations.models import (
    OrganizationStatus,
    OrganizationType,
)
from ra_platform.persistence.billing_profiles import (
    SQLiteOrganizationBillingProfileRepository,
)
from ra_platform.persistence.organization_details import (
    SQLiteOrganizationCompanyProfileRepository,
    SQLiteOrganizationContactRepository,
)
from ra_platform.security.financial_data import (
    FinancialDataEncryptionError,
    masked_financial_value,
)
from ra_platform.persistence.sqlite_repositories import (
    SQLiteAuditEventRepository,
    SQLiteBillingUnitOfWork,
    SQLiteEngagementBillingTermsRepository,
    SQLiteEngagementRepository,
    SQLiteInvoiceRepository,
    SQLiteOrganizationRepository,
    SQLiteTimeEntryRepository,
)


router = APIRouter(
    prefix="/admin",
    tags=["admin-platform"],
)


class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    type: str
    status: str


class UpdateOrganizationRequest(BaseModel):
    name: str | None = None
    status: OrganizationStatus | None = None


class CompanyProfileResponse(BaseModel):
    id: UUID | None
    organization_id: UUID

    business_type: str | None
    industry: str | None
    website: str | None
    phone: str | None
    company_size: str | None

    address_line1: str | None
    address_line2: str | None
    city: str | None
    state_region: str | None
    postal_code: str | None
    country: str


class UpdateCompanyProfileRequest(BaseModel):
    business_type: str | None = None
    industry: str | None = None
    website: str | None = None
    phone: str | None = None
    company_size: str | None = None

    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state_region: str | None = None
    postal_code: str | None = None
    country: str | None = None


class ContactResponse(BaseModel):
    id: UUID
    organization_id: UUID

    name: str
    title: str | None
    email: str | None
    phone: str | None
    contact_type: str | None

    is_primary: bool


class CreateContactRequest(BaseModel):
    name: str = Field(min_length=1)

    title: str | None = None
    email: str | None = None
    phone: str | None = None
    contact_type: str | None = None

    is_primary: bool = False


class UpdateContactRequest(BaseModel):
    name: str | None = None
    title: str | None = None
    email: str | None = None
    phone: str | None = None
    contact_type: str | None = None

    is_primary: bool | None = None


class BillingProfileResponse(BaseModel):
    id: UUID | None
    organization_id: UUID

    billing_name: str | None
    billing_email: str | None

    address_line1: str | None
    address_line2: str | None
    city: str | None
    state_region: str | None
    postal_code: str | None
    country: str

    bank_name: str | None
    account_type: str | None

    has_routing_number: bool
    routing_number_masked: str | None

    has_account_number: bool
    account_number_masked: str | None


class UpdateBillingProfileRequest(BaseModel):
    billing_name: str | None = None
    billing_email: str | None = None

    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state_region: str | None = None
    postal_code: str | None = None
    country: str | None = None

    bank_name: str | None = None
    account_type: str | None = None

    routing_number: str | None = None
    account_number: str | None = None

    clear_routing_number: bool = False
    clear_account_number: bool = False


def build_billing_profile_response(
    *,
    organization_id: UUID,
    profile: OrganizationBillingProfile | None,
) -> BillingProfileResponse:
    if profile is None:
        return BillingProfileResponse(
            id=None,
            organization_id=organization_id,
            billing_name=None,
            billing_email=None,
            address_line1=None,
            address_line2=None,
            city=None,
            state_region=None,
            postal_code=None,
            country="US",
            bank_name=None,
            account_type=None,
            has_routing_number=False,
            routing_number_masked=None,
            has_account_number=False,
            account_number_masked=None,
        )

    return BillingProfileResponse(
        id=profile.id,
        organization_id=(
            profile.organization_id
        ),
        billing_name=profile.billing_name,
        billing_email=profile.billing_email,
        address_line1=profile.address_line1,
        address_line2=profile.address_line2,
        city=profile.city,
        state_region=profile.state_region,
        postal_code=profile.postal_code,
        country=profile.country,
        bank_name=profile.bank_name,
        account_type=profile.account_type,
        has_routing_number=(
            profile
            .routing_number_ciphertext
            is not None
        ),
        routing_number_masked=(
            masked_financial_value(
                profile.routing_number_last4
            )
        ),
        has_account_number=(
            profile
            .account_number_ciphertext
            is not None
        ),
        account_number_masked=(
            masked_financial_value(
                profile.account_number_last4
            )
        ),
    )


class CreateEngagementRequest(BaseModel):
    name: str = Field(
        min_length=1
    )

    service_type: str = Field(
        min_length=1
    )

    source: EngagementSource = (
        EngagementSource.DIRECT
    )

    status: EngagementStatus = (
        EngagementStatus.PROPOSED
    )


class EngagementResponse(BaseModel):
    id: UUID
    client_organization_id: UUID
    owner_organization_id: UUID

    name: str
    service_type: str
    source: str
    status: str


class CreateBillingTermsRequest(BaseModel):
    billing_type: BillingType
    billing_cadence: BillingCadence

    hourly_rate: Decimal | None = Field(
        default=None,
        gt=0,
    )

    expected_hours_min: (
        Decimal | None
    ) = Field(
        default=None,
        ge=0,
    )

    expected_hours_max: (
        Decimal | None
    ) = Field(
        default=None,
        ge=0,
    )

    payment_terms_days: int = Field(
        default=30,
        ge=0,
    )

    effective_from: date


class BillingTermsResponse(BaseModel):
    id: UUID
    engagement_id: UUID

    billing_type: str
    billing_cadence: str

    hourly_rate: str | None

    expected_hours_min: str | None
    expected_hours_max: str | None

    payment_terms_days: int

    effective_from: str
    effective_to: str | None


def require_permission(
    *,
    principal: AuthenticatedPrincipal,
    permission: Permission,
    organization_id: UUID | None = None,
) -> None:
    try:
        authorize(
            principal=principal,
            permission=permission,
            organization_id=organization_id,
        )
    except AuthorizationError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        ) from exc


def _normalize_optional_text(
    value: str | None,
) -> str | None:
    if value is None:
        return None

    normalized = value.strip()

    return normalized or None


def build_company_profile_response(
    *,
    organization_id: UUID,
    profile: OrganizationCompanyProfile | None,
) -> CompanyProfileResponse:
    if profile is None:
        return CompanyProfileResponse(
            id=None,
            organization_id=organization_id,
            business_type=None,
            industry=None,
            website=None,
            phone=None,
            company_size=None,
            address_line1=None,
            address_line2=None,
            city=None,
            state_region=None,
            postal_code=None,
            country="US",
        )

    return CompanyProfileResponse(
        id=profile.id,
        organization_id=profile.organization_id,
        business_type=profile.business_type,
        industry=profile.industry,
        website=profile.website,
        phone=profile.phone,
        company_size=profile.company_size,
        address_line1=profile.address_line1,
        address_line2=profile.address_line2,
        city=profile.city,
        state_region=profile.state_region,
        postal_code=profile.postal_code,
        country=profile.country,
    )


def build_contact_response(
    contact: OrganizationContact,
) -> ContactResponse:
    return ContactResponse(
        id=contact.id,
        organization_id=contact.organization_id,
        name=contact.name,
        title=contact.title,
        email=contact.email,
        phone=contact.phone,
        contact_type=contact.contact_type,
        is_primary=contact.is_primary,
    )


@router.get(
    "/organizations/{organization_id}",
    response_model=OrganizationResponse,
)
def get_organization(
    organization_id: UUID,
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    repository = SQLiteOrganizationRepository(
        connection
    )

    organization = repository.get(
        organization_id
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found.",
        )

    require_permission(
        principal=principal,
        permission=Permission.VIEW_ORGANIZATION,
        organization_id=organization.id,
    )

    return OrganizationResponse(
        id=organization.id,
        name=organization.name,
        type=organization.type.value,
        status=organization.status.value,
    )


@router.put(
    "/organizations/{organization_id}",
    response_model=OrganizationResponse,
)
def update_organization(
    organization_id: UUID,
    body: UpdateOrganizationRequest,
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    repository = SQLiteOrganizationRepository(
        connection
    )

    organization = repository.get(
        organization_id
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found.",
        )

    require_permission(
        principal=principal,
        permission=Permission.MANAGE_ORGANIZATION,
        organization_id=organization.id,
    )

    changed_fields: list[str] = []

    if "name" in body.model_fields_set:
        name = (
            body.name.strip()
            if body.name
            else ""
        )

        if not name:
            raise HTTPException(
                status_code=422,
                detail=(
                    "Organization name "
                    "cannot be empty."
                ),
            )

        organization.name = name
        changed_fields.append("name")

    if "status" in body.model_fields_set:
        if body.status is None:
            raise HTTPException(
                status_code=422,
                detail=(
                    "Organization status "
                    "cannot be empty."
                ),
            )

        organization.status = body.status
        changed_fields.append("status")

    if changed_fields:
        organization.updated_at = datetime.now(
            timezone.utc
        )

        repository.update(
            organization
        )

        SQLiteAuditEventRepository(
            connection
        ).add(
            AuditEvent(
                actor_user_id=principal.user.id,
                organization_id=organization.id,
                action="organization.updated",
                resource_type="organization",
                resource_id=organization.id,
                metadata_json=json.dumps(
                    {
                        "changed_fields":
                            sorted(changed_fields),
                    },
                    sort_keys=True,
                ),
            )
        )

        connection.commit()

    return OrganizationResponse(
        id=organization.id,
        name=organization.name,
        type=organization.type.value,
        status=organization.status.value,
    )


@router.get(
    "/organizations/"
    "{organization_id}/company-profile",
    response_model=CompanyProfileResponse,
)
def get_company_profile(
    organization_id: UUID,
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    organization = SQLiteOrganizationRepository(
        connection
    ).get(
        organization_id
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found.",
        )

    require_permission(
        principal=principal,
        permission=Permission.VIEW_ORGANIZATION,
        organization_id=organization.id,
    )

    profile = (
        SQLiteOrganizationCompanyProfileRepository(
            connection
        ).get_for_organization(
            organization.id
        )
    )

    return build_company_profile_response(
        organization_id=organization.id,
        profile=profile,
    )


@router.put(
    "/organizations/"
    "{organization_id}/company-profile",
    response_model=CompanyProfileResponse,
)
def update_company_profile(
    organization_id: UUID,
    body: UpdateCompanyProfileRequest,
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    organization = SQLiteOrganizationRepository(
        connection
    ).get(
        organization_id
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found.",
        )

    require_permission(
        principal=principal,
        permission=Permission.MANAGE_ORGANIZATION,
        organization_id=organization.id,
    )

    repository = (
        SQLiteOrganizationCompanyProfileRepository(
            connection
        )
    )

    profile = repository.get_for_organization(
        organization.id
    )

    if profile is None:
        profile = OrganizationCompanyProfile(
            organization_id=organization.id
        )

    editable_fields = {
        "business_type",
        "industry",
        "website",
        "phone",
        "company_size",
        "address_line1",
        "address_line2",
        "city",
        "state_region",
        "postal_code",
        "country",
    }

    changed_fields: list[str] = []

    for field in editable_fields:
        if field not in body.model_fields_set:
            continue

        value = getattr(
            body,
            field,
        )

        if field == "country":
            value = (
                _normalize_optional_text(value)
                or "US"
            )
        else:
            value = _normalize_optional_text(
                value
            )

        setattr(
            profile,
            field,
            value,
        )

        changed_fields.append(
            field
        )

    if changed_fields:
        profile.updated_at = datetime.now(
            timezone.utc
        )

        repository.upsert(
            profile
        )

        SQLiteAuditEventRepository(
            connection
        ).add(
            AuditEvent(
                actor_user_id=principal.user.id,
                organization_id=organization.id,
                action=(
                    "organization."
                    "company_profile_updated"
                ),
                resource_type=(
                    "organization_company_profile"
                ),
                resource_id=profile.id,
                metadata_json=json.dumps(
                    {
                        "changed_fields":
                            sorted(changed_fields),
                    },
                    sort_keys=True,
                ),
            )
        )

        connection.commit()

    return build_company_profile_response(
        organization_id=organization.id,
        profile=profile,
    )


@router.get(
    "/organizations/"
    "{organization_id}/contacts",
    response_model=list[ContactResponse],
)
def list_organization_contacts(
    organization_id: UUID,
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    organization = SQLiteOrganizationRepository(
        connection
    ).get(
        organization_id
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found.",
        )

    require_permission(
        principal=principal,
        permission=Permission.VIEW_ORGANIZATION,
        organization_id=organization.id,
    )

    contacts = (
        SQLiteOrganizationContactRepository(
            connection
        ).list_for_organization(
            organization.id
        )
    )

    return [
        build_contact_response(
            contact
        )
        for contact in contacts
    ]


@router.post(
    "/organizations/"
    "{organization_id}/contacts",
    response_model=ContactResponse,
)
def create_organization_contact(
    organization_id: UUID,
    body: CreateContactRequest,
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    organization = SQLiteOrganizationRepository(
        connection
    ).get(
        organization_id
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found.",
        )

    require_permission(
        principal=principal,
        permission=Permission.MANAGE_ORGANIZATION,
        organization_id=organization.id,
    )

    name = body.name.strip()

    if not name:
        raise HTTPException(
            status_code=422,
            detail="Contact name cannot be empty.",
        )

    contact = OrganizationContact(
        organization_id=organization.id,
        name=name,
        title=_normalize_optional_text(
            body.title
        ),
        email=_normalize_optional_text(
            body.email
        ),
        phone=_normalize_optional_text(
            body.phone
        ),
        contact_type=_normalize_optional_text(
            body.contact_type
        ),
        is_primary=body.is_primary,
    )

    SQLiteOrganizationContactRepository(
        connection
    ).add(
        contact
    )

    SQLiteAuditEventRepository(
        connection
    ).add(
        AuditEvent(
            actor_user_id=principal.user.id,
            organization_id=organization.id,
            action="organization.contact_created",
            resource_type="organization_contact",
            resource_id=contact.id,
            metadata_json=json.dumps(
                {
                    "contact_type":
                        contact.contact_type,
                    "is_primary":
                        contact.is_primary,
                },
                sort_keys=True,
            ),
        )
    )

    connection.commit()

    return build_contact_response(
        contact
    )


@router.put(
    "/organizations/"
    "{organization_id}/contacts/"
    "{contact_id}",
    response_model=ContactResponse,
)
def update_organization_contact(
    organization_id: UUID,
    contact_id: UUID,
    body: UpdateContactRequest,
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    organization = SQLiteOrganizationRepository(
        connection
    ).get(
        organization_id
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found.",
        )

    require_permission(
        principal=principal,
        permission=Permission.MANAGE_ORGANIZATION,
        organization_id=organization.id,
    )

    repository = (
        SQLiteOrganizationContactRepository(
            connection
        )
    )

    contact = repository.get(
        contact_id
    )

    if (
        contact is None
        or contact.organization_id
        != organization.id
    ):
        raise HTTPException(
            status_code=404,
            detail="Contact not found.",
        )

    changed_fields: list[str] = []

    text_fields = {
        "name",
        "title",
        "email",
        "phone",
        "contact_type",
    }

    for field in text_fields:
        if field not in body.model_fields_set:
            continue

        value = getattr(
            body,
            field,
        )

        if field == "name":
            value = (
                value.strip()
                if value
                else ""
            )

            if not value:
                raise HTTPException(
                    status_code=422,
                    detail=(
                        "Contact name "
                        "cannot be empty."
                    ),
                )
        else:
            value = _normalize_optional_text(
                value
            )

        setattr(
            contact,
            field,
            value,
        )

        changed_fields.append(
            field
        )

    if "is_primary" in body.model_fields_set:
        if body.is_primary is None:
            raise HTTPException(
                status_code=422,
                detail=(
                    "Primary status "
                    "cannot be empty."
                ),
            )

        contact.is_primary = (
            body.is_primary
        )

        changed_fields.append(
            "is_primary"
        )

    if changed_fields:
        contact.updated_at = datetime.now(
            timezone.utc
        )

        repository.update(
            contact
        )

        SQLiteAuditEventRepository(
            connection
        ).add(
            AuditEvent(
                actor_user_id=principal.user.id,
                organization_id=organization.id,
                action="organization.contact_updated",
                resource_type="organization_contact",
                resource_id=contact.id,
                metadata_json=json.dumps(
                    {
                        "changed_fields":
                            sorted(changed_fields),
                    },
                    sort_keys=True,
                ),
            )
        )

        connection.commit()

    return build_contact_response(
        contact
    )


@router.get(
    "/platform-organization",
    response_model=OrganizationResponse,
)
def get_platform_organization(
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    require_permission(
        principal=principal,
        permission=(
            Permission
            .MANAGE_BILLING_PROFILE
        ),
    )

    organizations = (
        SQLiteOrganizationRepository(
            connection
        ).list_all()
    )

    organization = next(
        (
            item
            for item in organizations
            if item.type
            == OrganizationType.PARADIGM_RA
        ),
        None,
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Paradigm Ra organization "
                "not found."
            ),
        )

    return OrganizationResponse(
        id=organization.id,
        name=organization.name,
        type=organization.type.value,
        status=organization.status.value,
    )


@router.get(
    "/organizations",
    response_model=list[
        OrganizationResponse
    ],
)
def list_client_organizations(
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    require_permission(
        principal=principal,
        permission=(
            Permission.VIEW_ORGANIZATION
        ),
    )

    repository = (
        SQLiteOrganizationRepository(
            connection
        )
    )

    organizations = [
        organization
        for organization
        in repository.list_all()
        if (
            organization.type
            == OrganizationType.CLIENT
        )
    ]

    return [
        OrganizationResponse(
            id=organization.id,
            name=organization.name,
            type=organization.type.value,
            status=(
                organization.status.value
            ),
        )
        for organization
        in organizations
    ]


@router.get(
    "/organizations/"
    "{organization_id}/billing-profile",
    response_model=BillingProfileResponse,
)
def get_organization_billing_profile(
    organization_id: UUID,
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    organization = (
        SQLiteOrganizationRepository(
            connection
        ).get(
            organization_id
        )
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found.",
        )

    require_permission(
        principal=principal,
        permission=(
            Permission
            .MANAGE_BILLING_PROFILE
        ),
        organization_id=(
            organization.id
        ),
    )

    profile = (
        SQLiteOrganizationBillingProfileRepository(
            connection
        ).get_for_organization(
            organization.id
        )
    )

    return build_billing_profile_response(
        organization_id=(
            organization.id
        ),
        profile=profile,
    )


@router.put(
    "/organizations/"
    "{organization_id}/billing-profile",
    response_model=BillingProfileResponse,
)
def update_admin_billing_profile(
    organization_id: UUID,
    body: UpdateBillingProfileRequest,
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    organization = (
        SQLiteOrganizationRepository(
            connection
        ).get(
            organization_id
        )
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found.",
        )

    require_permission(
        principal=principal,
        permission=(
            Permission
            .MANAGE_BILLING_PROFILE
        ),
        organization_id=(
            organization.id
        ),
    )

    repository = (
        SQLiteOrganizationBillingProfileRepository(
            connection
        )
    )

    try:
        profile = (
            update_organization_billing_profile(
                repository=repository,
                organization_id=(
                    organization.id
                ),
                values=body.model_dump(),
                fields_set=set(
                    body.model_fields_set
                ),
            )
        )

    except (
        BillingProfileUpdateError,
        FinancialDataEncryptionError,
    ) as exc:
        connection.rollback()

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    changed_fields = sorted(
        body.model_fields_set
    )

    from ra_platform.identity.models import (
        AuditEvent,
    )
    from ra_platform.persistence.sqlite_repositories import (
        SQLiteAuditEventRepository,
    )
    import json

    SQLiteAuditEventRepository(
        connection
    ).add(
        AuditEvent(
            actor_user_id=(
                principal.user.id
            ),
            organization_id=(
                organization.id
            ),
            action=(
                "organization."
                "billing_profile_updated"
            ),
            resource_type=(
                "organization_billing_profile"
            ),
            resource_id=profile.id,
            metadata_json=json.dumps(
                {
                    "changed_fields":
                        changed_fields,
                },
                sort_keys=True,
            ),
        )
    )

    connection.commit()

    return build_billing_profile_response(
        organization_id=(
            organization.id
        ),
        profile=profile,
    )


@router.get(
    "/organizations/"
    "{organization_id}/engagements",
    response_model=list[
        EngagementResponse
    ],
)
def list_organization_engagements(
    organization_id: UUID,
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    organizations = (
        SQLiteOrganizationRepository(
            connection
        )
    )

    organization = organizations.get(
        organization_id
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found.",
        )

    require_permission(
        principal=principal,
        permission=(
            Permission.VIEW_ENGAGEMENT
        ),
        organization_id=organization.id,
    )

    engagements = (
        SQLiteEngagementRepository(
            connection
        ).list_for_client(
            organization.id
        )
    )

    return [
        EngagementResponse(
            id=engagement.id,
            client_organization_id=(
                engagement.client_organization_id
            ),
            owner_organization_id=(
                engagement.owner_organization_id
            ),
            name=engagement.name,
            service_type=(
                engagement.service_type
            ),
            source=engagement.source.value,
            status=engagement.status.value,
        )
        for engagement
        in engagements
    ]


@router.post(
    "/organizations/"
    "{organization_id}/engagements",
    response_model=EngagementResponse,
)
def create_organization_engagement(
    organization_id: UUID,
    body: CreateEngagementRequest,
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    organizations = (
        SQLiteOrganizationRepository(
            connection
        )
    )

    client = organizations.get(
        organization_id
    )

    if client is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found.",
        )

    require_permission(
        principal=principal,
        permission=(
            Permission.CREATE_ENGAGEMENT
        ),
        organization_id=client.id,
    )

    platform = next(
        (
            item
            for item
            in organizations.list_all()
            if item.type
            == OrganizationType.PARADIGM_RA
        ),
        None,
    )

    if platform is None:
        raise HTTPException(
            status_code=409,
            detail=(
                "Paradigm Ra organization "
                "is not configured."
            ),
        )

    engagement = Engagement(
        client_organization_id=(
            client.id
        ),
        owner_organization_id=(
            platform.id
        ),
        name=body.name.strip(),
        service_type=(
            body.service_type.strip()
        ),
        source=body.source,
        status=body.status,
    )

    SQLiteEngagementRepository(
        connection
    ).add(
        engagement
    )

    from ra_platform.identity.models import (
        AuditEvent,
    )
    from ra_platform.persistence.sqlite_repositories import (
        SQLiteAuditEventRepository,
    )
    import json

    SQLiteAuditEventRepository(
        connection
    ).add(
        AuditEvent(
            actor_user_id=(
                principal.user.id
            ),
            organization_id=(
                client.id
            ),
            action="engagement.created",
            resource_type="engagement",
            resource_id=engagement.id,
            metadata_json=json.dumps(
                {
                    "name":
                        engagement.name,
                    "service_type":
                        engagement.service_type,
                    "source":
                        engagement.source.value,
                    "status":
                        engagement.status.value,
                },
                sort_keys=True,
            ),
        )
    )

    connection.commit()

    return EngagementResponse(
        id=engagement.id,
        client_organization_id=(
            engagement
            .client_organization_id
        ),
        owner_organization_id=(
            engagement
            .owner_organization_id
        ),
        name=engagement.name,
        service_type=(
            engagement.service_type
        ),
        source=engagement.source.value,
        status=engagement.status.value,
    )


@router.post(
    "/engagements/"
    "{engagement_id}/billing-terms",
    response_model=BillingTermsResponse,
)
def create_engagement_billing_terms(
    engagement_id: UUID,
    body: CreateBillingTermsRequest,
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    engagement = (
        SQLiteEngagementRepository(
            connection
        ).get(
            engagement_id
        )
    )

    if engagement is None:
        raise HTTPException(
            status_code=404,
            detail="Engagement not found.",
        )

    require_permission(
        principal=principal,
        permission=(
            Permission.CREATE_INVOICE
        ),
        organization_id=(
            engagement
            .client_organization_id
        ),
    )

    repository = (
        SQLiteEngagementBillingTermsRepository(
            connection
        )
    )

    existing_terms = (
        repository.list_for_engagement(
            engagement.id
        )
    )

    terms = EngagementBillingTerms(
        engagement_id=engagement.id,
        billing_type=body.billing_type,
        billing_cadence=(
            body.billing_cadence
        ),
        hourly_rate=body.hourly_rate,
        expected_hours_min=(
            body.expected_hours_min
        ),
        expected_hours_max=(
            body.expected_hours_max
        ),
        payment_terms_days=(
            body.payment_terms_days
        ),
        effective_from=(
            body.effective_from
        ),
    )

    try:
        (
            closed_terms,
            terms,
        ) = (
            prepare_successor_billing_terms(
                existing_terms=(
                    existing_terms
                ),
                new_terms=terms,
            )
        )

    except BillingTermsValidationError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    if closed_terms is not None:
        repository.update_effective_to(
            closed_terms
        )

    repository.add(
        terms
    )

    connection.commit()

    return BillingTermsResponse(
        id=terms.id,
        engagement_id=(
            terms.engagement_id
        ),
        billing_type=(
            terms.billing_type.value
        ),
        billing_cadence=(
            terms.billing_cadence.value
        ),
        hourly_rate=(
            str(terms.hourly_rate)
            if terms.hourly_rate
            is not None
            else None
        ),
        expected_hours_min=(
            str(
                terms.expected_hours_min
            )
            if terms.expected_hours_min
            is not None
            else None
        ),
        expected_hours_max=(
            str(
                terms.expected_hours_max
            )
            if terms.expected_hours_max
            is not None
            else None
        ),
        payment_terms_days=(
            terms.payment_terms_days
        ),
        effective_from=(
            terms.effective_from
            .isoformat()
        ),
        effective_to=None,
    )


@router.get(
    "/engagements/"
    "{engagement_id}/billing-terms",
    response_model=list[
        BillingTermsResponse
    ],
)
def list_engagement_billing_terms(
    engagement_id: UUID,
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    engagements = (
        SQLiteEngagementRepository(
            connection
        )
    )

    engagement = engagements.get(
        engagement_id
    )

    if engagement is None:
        raise HTTPException(
            status_code=404,
            detail="Engagement not found.",
        )

    require_permission(
        principal=principal,
        permission=Permission.VIEW_BILLING,
        organization_id=(
            engagement.client_organization_id
        ),
    )

    terms = (
        SQLiteEngagementBillingTermsRepository(
            connection
        ).list_for_engagement(
            engagement.id
        )
    )

    return [
        BillingTermsResponse(
            id=item.id,
            engagement_id=(
                item.engagement_id
            ),
            billing_type=(
                item.billing_type.value
            ),
            billing_cadence=(
                item.billing_cadence.value
            ),
            hourly_rate=(
                str(item.hourly_rate)
                if item.hourly_rate
                is not None
                else None
            ),
            expected_hours_min=(
                str(
                    item.expected_hours_min
                )
                if item.expected_hours_min
                is not None
                else None
            ),
            expected_hours_max=(
                str(
                    item.expected_hours_max
                )
                if item.expected_hours_max
                is not None
                else None
            ),
            payment_terms_days=(
                item.payment_terms_days
            ),
            effective_from=(
                item.effective_from
                .isoformat()
            ),
            effective_to=(
                item.effective_to
                .isoformat()
                if item.effective_to
                else None
            ),
        )
        for item in terms
    ]


class CreateTimeEntryRequest(BaseModel):
    work_date: date

    description: str = Field(
        min_length=1
    )

    hours: Decimal = Field(
        gt=0
    )

    workstream: (
        TimeEntryWorkstream
        | None
    ) = None

    friction: (
        TimeEntryFriction
        | None
    ) = None

    operational_note: str | None = None


class UpdateTimeEntryRequest(
    CreateTimeEntryRequest
):
    pass


class TimeEntryResponse(BaseModel):
    id: UUID
    engagement_id: UUID

    work_date: str
    description: str
    hours: str

    workstream: str | None
    friction: str | None
    operational_note: str | None

    status: str

    invoice_id: UUID | None


class GenerateInvoiceRequest(BaseModel):
    issue_date: date | None = None

    bill_to_email: str | None = None
    notes: str | None = None


class InvoiceLineResponse(BaseModel):
    id: UUID
    engagement_id: UUID

    description: str

    quantity: str
    unit_rate: str
    amount: str


class InvoiceResponse(BaseModel):
    id: UUID

    invoice_number: str
    status: str

    issue_date: str | None
    due_date: str | None
    sent_at: str | None

    bill_to_name: str
    bill_to_email: str | None

    subtotal: str
    tax_amount: str
    total: str

    amount_paid: str
    balance_due: str

    line_items: list[
        InvoiceLineResponse
    ]


def build_time_entry_response(
    entry: TimeEntry,
) -> TimeEntryResponse:
    return TimeEntryResponse(
        id=entry.id,
        engagement_id=(
            entry.engagement_id
        ),
        work_date=(
            entry.work_date.isoformat()
        ),
        description=entry.description,
        hours=str(entry.hours),
        workstream=(
            entry.workstream.value
            if entry.workstream
            else None
        ),
        friction=(
            entry.friction.value
            if entry.friction
            else None
        ),
        operational_note=(
            entry.operational_note
        ),
        status=entry.status.value,
        invoice_id=entry.invoice_id,
    )


def build_invoice_response(
    invoice: Invoice,
) -> InvoiceResponse:
    return InvoiceResponse(
        id=invoice.id,
        invoice_number=(
            invoice.invoice_number
        ),
        status=invoice.status.value,
        issue_date=(
            invoice.issue_date.isoformat()
            if invoice.issue_date
            else None
        ),
        due_date=(
            invoice.due_date.isoformat()
            if invoice.due_date
            else None
        ),
        sent_at=(
            invoice.sent_at.isoformat()
            if invoice.sent_at
            else None
        ),
        bill_to_name=(
            invoice.bill_to_name
        ),
        bill_to_email=(
            invoice.bill_to_email
        ),
        subtotal=str(invoice.subtotal),
        tax_amount=str(
            invoice.tax_amount
        ),
        total=str(invoice.total),
        amount_paid=str(
            invoice.amount_paid
        ),
        balance_due=str(
            invoice.balance_due
        ),
        line_items=[
            InvoiceLineResponse(
                id=line.id,
                engagement_id=(
                    line.engagement_id
                ),
                description=(
                    line.description
                ),
                quantity=str(
                    line.quantity
                ),
                unit_rate=str(
                    line.unit_rate
                ),
                amount=str(
                    line.amount
                ),
            )
            for line
            in invoice.line_items
        ],
    )


def get_engagement_or_404(
    *,
    engagement_id: UUID,
    connection: sqlite3.Connection,
):
    engagement = (
        SQLiteEngagementRepository(
            connection
        ).get(engagement_id)
    )

    if engagement is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Engagement not found."
            ),
        )

    return engagement


@router.get(
    "/engagements/"
    "{engagement_id}/time-entries",
    response_model=list[
        TimeEntryResponse
    ],
)
def list_time_entries(
    engagement_id: UUID,
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    engagement = get_engagement_or_404(
        engagement_id=engagement_id,
        connection=connection,
    )

    require_permission(
        principal=principal,
        permission=Permission.VIEW_BILLING,
        organization_id=(
            engagement.client_organization_id
        ),
    )

    entries = (
        SQLiteTimeEntryRepository(
            connection
        ).list_for_engagement(
            engagement.id
        )
    )

    return [
        build_time_entry_response(
            entry
        )
        for entry in entries
    ]


@router.post(
    "/engagements/"
    "{engagement_id}/time-entries",
    response_model=TimeEntryResponse,
)
def create_time_entry(
    engagement_id: UUID,
    body: CreateTimeEntryRequest,
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    engagement = get_engagement_or_404(
        engagement_id=engagement_id,
        connection=connection,
    )

    require_permission(
        principal=principal,
        permission=(
            Permission.CREATE_INVOICE
        ),
        organization_id=(
            engagement.client_organization_id
        ),
    )

    entry = TimeEntry(
        engagement_id=engagement.id,
        work_date=body.work_date,
        description=(
            body.description.strip()
        ),
        hours=body.hours,
        workstream=body.workstream,
        friction=body.friction,
        operational_note=(
            body.operational_note.strip()
            if (
                body.operational_note
                and body.operational_note.strip()
            )
            else None
        ),
    )

    repository = (
        SQLiteTimeEntryRepository(
            connection
        )
    )

    repository.add_many(
        [entry]
    )

    connection.commit()

    return build_time_entry_response(
        entry
    )


@router.put(
    "/time-entries/{time_entry_id}",
    response_model=TimeEntryResponse,
)
def update_admin_time_entry(
    time_entry_id: UUID,
    body: UpdateTimeEntryRequest,
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    repository = (
        SQLiteTimeEntryRepository(
            connection
        )
    )

    entry = repository.get(
        time_entry_id
    )

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail="Time entry not found.",
        )

    engagement = get_engagement_or_404(
        engagement_id=(
            entry.engagement_id
        ),
        connection=connection,
    )

    require_permission(
        principal=principal,
        permission=(
            Permission.CREATE_INVOICE
        ),
        organization_id=(
            engagement.client_organization_id
        ),
    )

    if (
        entry.status
        != TimeEntryStatus.DRAFT
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "Only draft time entries "
                "can be edited."
            ),
        )

    entry.work_date = body.work_date
    entry.description = (
        body.description.strip()
    )
    entry.hours = body.hours
    entry.workstream = body.workstream
    entry.friction = body.friction

    entry.operational_note = (
        body.operational_note.strip()
        if (
            body.operational_note
            and body.operational_note.strip()
        )
        else None
    )

    try:
        repository.update_draft(
            entry
        )

    except ValueError as exc:
        connection.rollback()

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    connection.commit()

    return build_time_entry_response(
        entry
    )


@router.post(
    "/time-entries/"
    "{time_entry_id}/reopen",
    response_model=TimeEntryResponse,
)
def reopen_admin_time_entry(
    time_entry_id: UUID,
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    repository = (
        SQLiteTimeEntryRepository(
            connection
        )
    )

    entry = repository.get(
        time_entry_id
    )

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail="Time entry not found.",
        )

    engagement = get_engagement_or_404(
        engagement_id=(
            entry.engagement_id
        ),
        connection=connection,
    )

    require_permission(
        principal=principal,
        permission=(
            Permission.CREATE_INVOICE
        ),
        organization_id=(
            engagement.client_organization_id
        ),
    )

    try:
        reopen_time_entry(
            entry
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    repository.update_many(
        [entry]
    )

    connection.commit()

    return build_time_entry_response(
        entry
    )


@router.post(
    "/time-entries/"
    "{time_entry_id}/approve",
    response_model=TimeEntryResponse,
)
def approve_admin_time_entry(
    time_entry_id: UUID,
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    repository = (
        SQLiteTimeEntryRepository(
            connection
        )
    )

    entry = repository.get(
        time_entry_id
    )

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Time entry not found."
            ),
        )

    engagement = get_engagement_or_404(
        engagement_id=(
            entry.engagement_id
        ),
        connection=connection,
    )

    require_permission(
        principal=principal,
        permission=(
            Permission.CREATE_INVOICE
        ),
        organization_id=(
            engagement.client_organization_id
        ),
    )

    try:
        approve_time_entry(
            entry
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    repository.update_many(
        [entry]
    )

    connection.commit()

    return build_time_entry_response(
        entry
    )


@router.get(
    "/engagements/"
    "{engagement_id}/invoices",
    response_model=list[
        InvoiceResponse
    ],
)
def list_engagement_invoices(
    engagement_id: UUID,
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    engagement = get_engagement_or_404(
        engagement_id=engagement_id,
        connection=connection,
    )

    require_permission(
        principal=principal,
        permission=Permission.VIEW_BILLING,
        organization_id=(
            engagement.client_organization_id
        ),
    )

    invoices = (
        SQLiteInvoiceRepository(
            connection
        ).list_for_engagement(
            engagement.id
        )
    )

    return [
        build_invoice_response(
            invoice
        )
        for invoice in invoices
    ]


@router.post(
    "/engagements/"
    "{engagement_id}/invoices/generate",
    response_model=InvoiceResponse,
)
def generate_engagement_invoice(
    engagement_id: UUID,
    body: GenerateInvoiceRequest,
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    engagement = get_engagement_or_404(
        engagement_id=engagement_id,
        connection=connection,
    )

    require_permission(
        principal=principal,
        permission=(
            Permission.CREATE_INVOICE
        ),
        organization_id=(
            engagement.client_organization_id
        ),
    )

    organization = (
        SQLiteOrganizationRepository(
            connection
        ).get(
            engagement.client_organization_id
        )
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Client organization "
                "not found."
            ),
        )

    time_entries = (
        SQLiteTimeEntryRepository(
            connection
        ).list_for_engagement(
            engagement.id
        )
    )

    billing_terms = (
        SQLiteEngagementBillingTermsRepository(
            connection
        ).list_for_engagement(
            engagement.id
        )
    )

    invoice_date = (
        body.issue_date
        or date.today()
    )

    effective_terms = [
        terms
        for terms in billing_terms
        if (
            terms.effective_from
            <= invoice_date
            and (
                terms.effective_to
                is None
                or invoice_date
                <= terms.effective_to
            )
        )
    ]

    payment_terms_days = 30

    if effective_terms:
        current_terms = max(
            effective_terms,
            key=lambda terms:
                terms.effective_from,
        )

        payment_terms_days = (
            current_terms
            .payment_terms_days
        )

    try:
        invoice = (
            create_invoice_from_time_entries(
                uow=SQLiteBillingUnitOfWork(
                    connection
                ),
                client_organization_id=(
                    engagement
                    .client_organization_id
                ),
                invoice_number=(
                    next_invoice_number(
                        connection,
                        invoice_date=(
                            invoice_date
                        ),
                        prefix=(
                            invoice_prefix_for_organization_name(
                                organization.name
                            )
                        ),
                    )
                ),
                time_entries=time_entries,
                billing_terms=(
                    billing_terms
                ),
                bill_to_name=(
                    organization.name
                ),
                bill_to_email=(
                    body.bill_to_email
                ),
                issue_date=invoice_date,
                payment_terms_days=(
                    payment_terms_days
                ),
                notes=body.notes,
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    return build_invoice_response(
        invoice
    )


# ---------------------------------------------------------
# Invoice delivery
# ---------------------------------------------------------

import hashlib
import json
import os

from ra_platform.billing.invoice_pdf import (
    build_invoice_pdf,
)
from ra_platform.billing.models import (
    InvoiceStatus,
)
from ra_platform.billing.service import (
    send_invoice as mark_invoice_sent,
)
from ra_platform.identity.models import (
    AuditEvent,
)
from ra_platform.notifications.resend import (
    ResendDeliveryError,
    send_pdf_email,
)
from ra_platform.persistence.sqlite_repositories import (
    SQLiteAuditEventRepository,
    SQLiteUserRepository,
)


class SendInvoiceResponse(BaseModel):
    invoice: InvoiceResponse
    provider_message_id: str
    pdf_sha256: str


@router.post(
    "/invoices/{invoice_id}/send",
    response_model=SendInvoiceResponse,
)
def send_admin_invoice(
    invoice_id: UUID,
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    invoices = SQLiteInvoiceRepository(
        connection
    )

    invoice = invoices.get(
        invoice_id
    )

    if invoice is None:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found.",
        )

    require_permission(
        principal=principal,
        permission=Permission.SEND_INVOICE,
        organization_id=(
            invoice.client_organization_id
        ),
    )

    if (
        invoice.status
        != InvoiceStatus.DRAFT
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "Only draft invoices "
                "can be sent."
            ),
        )

    if not invoice.bill_to_email:
        raise HTTPException(
            status_code=422,
            detail=(
                "Invoice does not have "
                "a billing email."
            ),
        )

    api_key = os.environ.get(
        "RESEND_API_KEY",
        "",
    ).strip()

    from_address = (
        os.environ.get(
            "RA_INVOICE_FROM",
            "",
        ).strip()
        or os.environ.get(
            "RA_LEAD_NOTIFICATION_FROM",
            "",
        ).strip()
    )

    issuer_email = os.environ.get(
        "RA_BILLING_ISSUER_EMAIL",
        "",
    ).strip()

    issuer_title = (
        os.environ.get(
            "RA_BILLING_ISSUER_TITLE",
            "Chief Financial Officer",
        ).strip()
        or "Chief Financial Officer"
    )

    reply_to = (
        os.environ.get(
            "RA_INVOICE_REPLY_TO",
            "",
        ).strip()
        or None
    )

    if (
        not api_key
        or not from_address
        or not issuer_email
    ):
        raise HTTPException(
            status_code=503,
            detail=(
                "Invoice email configuration "
                "is incomplete."
            ),
        )

    issuer = SQLiteUserRepository(
        connection
    ).get_by_email(
        issuer_email
    )

    if issuer is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Configured billing issuer "
                "was not found."
            ),
        )

    try:
        pdf_bytes = build_invoice_pdf(
            invoice=invoice,
            issuer_name=(
                issuer.display_name
            ),
            issuer_title=issuer_title,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Invoice PDF generation "
                "failed."
            ),
        ) from exc

    pdf_sha256 = hashlib.sha256(
        pdf_bytes
    ).hexdigest()

    pdf_filename = (
        f"{invoice.invoice_number}.pdf"
    )

    email_text = "\n".join(
        [
            (
                f"Hello "
                f"{invoice.bill_to_name},"
            ),
            "",
            (
                "Attached is invoice "
                f"{invoice.invoice_number} "
                "from Paradigm Ra."
            ),
            "",
            (
                "Balance due: "
                f"${invoice.balance_due:,.2f}"
            ),
            (
                "Due date: "
                + (
                    invoice.due_date.isoformat()
                    if invoice.due_date
                    else "See attached invoice"
                )
            ),
            "",
            "Thank you,",
            issuer.display_name,
            issuer_title,
            "Paradigm Ra",
        ]
    )

    try:
        delivery = send_pdf_email(
            api_key=api_key,
            from_address=from_address,
            to_address=(
                invoice.bill_to_email
            ),
            reply_to=reply_to,
            subject=(
                "Paradigm Ra Invoice "
                f"{invoice.invoice_number}"
            ),
            text=email_text,
            pdf_bytes=pdf_bytes,
            pdf_filename=pdf_filename,
            idempotency_key=(
                "invoice-send/"
                f"{invoice.id}"
            ),
        )

    except ResendDeliveryError as exc:
        # No invoice state has changed.
        connection.rollback()

        print(
            "INVOICE EMAIL DELIVERY FAILED:",
            str(exc),
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "Invoice email delivery "
                "failed."
            ),
        ) from exc

    try:
        mark_invoice_sent(
            invoice
        )

        invoices.update(
            invoice
        )

        SQLiteAuditEventRepository(
            connection
        ).add(
            AuditEvent(
                actor_user_id=(
                    principal.user.id
                ),
                organization_id=(
                    invoice
                    .client_organization_id
                ),
                action=(
                    "billing.invoice_sent"
                ),
                resource_type="invoice",
                resource_id=invoice.id,
                metadata_json=json.dumps(
                    {
                        "invoice_number": (
                            invoice
                            .invoice_number
                        ),
                        "recipient": (
                            invoice
                            .bill_to_email
                        ),
                        "billing_issuer_user_id": (
                            str(issuer.id)
                        ),
                        "provider": "resend",
                        "provider_message_id": (
                            delivery.message_id
                        ),
                        "pdf_filename": (
                            pdf_filename
                        ),
                        "pdf_sha256": (
                            pdf_sha256
                        ),
                    },
                    sort_keys=True,
                ),
            )
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    return SendInvoiceResponse(
        invoice=build_invoice_response(
            invoice
        ),
        provider_message_id=(
            delivery.message_id
        ),
        pdf_sha256=pdf_sha256,
    )
