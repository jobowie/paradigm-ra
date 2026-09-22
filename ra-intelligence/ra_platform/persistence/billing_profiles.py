from __future__ import annotations

import sqlite3

from uuid import UUID

from ra_platform.organizations.billing_profile import (
    OrganizationBillingProfile,
)


class SQLiteOrganizationBillingProfileRepository:
    def __init__(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        self.connection = connection

    def get_for_organization(
        self,
        organization_id: UUID,
    ) -> OrganizationBillingProfile | None:
        row = self.connection.execute(
            """
            SELECT *
            FROM organization_billing_profiles
            WHERE organization_id = ?
            LIMIT 1
            """,
            (
                str(
                    organization_id
                ),
            ),
        ).fetchone()

        if row is None:
            return None

        return self._hydrate(
            row
        )

    def upsert(
        self,
        profile: OrganizationBillingProfile,
    ) -> None:
        self.connection.execute(
            """
            INSERT INTO organization_billing_profiles (
                id,
                organization_id,

                billing_name,
                billing_email,

                address_line1,
                address_line2,
                city,
                state_region,
                postal_code,
                country,

                bank_name,
                account_type,

                routing_number_ciphertext,
                routing_number_last4,

                account_number_ciphertext,
                account_number_last4,

                created_at,
                updated_at
            )
            VALUES (
                ?, ?,
                ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?,
                ?, ?,
                ?, ?,
                ?, ?
            )
            ON CONFLICT(organization_id)
            DO UPDATE SET
                billing_name =
                    excluded.billing_name,
                billing_email =
                    excluded.billing_email,

                address_line1 =
                    excluded.address_line1,
                address_line2 =
                    excluded.address_line2,
                city =
                    excluded.city,
                state_region =
                    excluded.state_region,
                postal_code =
                    excluded.postal_code,
                country =
                    excluded.country,

                bank_name =
                    excluded.bank_name,
                account_type =
                    excluded.account_type,

                routing_number_ciphertext =
                    excluded.routing_number_ciphertext,
                routing_number_last4 =
                    excluded.routing_number_last4,

                account_number_ciphertext =
                    excluded.account_number_ciphertext,
                account_number_last4 =
                    excluded.account_number_last4,

                updated_at =
                    excluded.updated_at
            """,
            (
                str(profile.id),
                str(
                    profile.organization_id
                ),

                profile.billing_name,
                profile.billing_email,

                profile.address_line1,
                profile.address_line2,
                profile.city,
                profile.state_region,
                profile.postal_code,
                profile.country,

                profile.bank_name,
                profile.account_type,

                (
                    profile
                    .routing_number_ciphertext
                ),
                (
                    profile
                    .routing_number_last4
                ),

                (
                    profile
                    .account_number_ciphertext
                ),
                (
                    profile
                    .account_number_last4
                ),

                profile.created_at.isoformat(),
                profile.updated_at.isoformat(),
            ),
        )

    @staticmethod
    def _hydrate(
        row: sqlite3.Row,
    ) -> OrganizationBillingProfile:
        return OrganizationBillingProfile(
            id=UUID(
                row["id"]
            ),
            organization_id=UUID(
                row["organization_id"]
            ),

            billing_name=(
                row["billing_name"]
            ),
            billing_email=(
                row["billing_email"]
            ),

            address_line1=(
                row["address_line1"]
            ),
            address_line2=(
                row["address_line2"]
            ),
            city=row["city"],
            state_region=(
                row["state_region"]
            ),
            postal_code=(
                row["postal_code"]
            ),
            country=row["country"],

            bank_name=row["bank_name"],
            account_type=(
                row["account_type"]
            ),

            routing_number_ciphertext=(
                row[
                    "routing_number_ciphertext"
                ]
            ),
            routing_number_last4=(
                row[
                    "routing_number_last4"
                ]
            ),

            account_number_ciphertext=(
                row[
                    "account_number_ciphertext"
                ]
            ),
            account_number_last4=(
                row[
                    "account_number_last4"
                ]
            ),

            created_at=(
                row["created_at"]
            ),
            updated_at=(
                row["updated_at"]
            ),
        )
