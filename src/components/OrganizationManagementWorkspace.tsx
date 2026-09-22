"use client";

import {
  FormEvent,
  useEffect,
  useState,
} from "react";

import {
  OrganizationBillingProfileEditor,
} from "./OrganizationBillingProfileEditor";


import {
  OrganizationCompanyProfileCard,
} from "./OrganizationCompanyProfileCard";

import {
  OrganizationContactsCard,
} from "./OrganizationContactsCard";


interface Organization {
  id: string;
  name: string;
  type: string;
  status: string;
}


interface Engagement {
  id: string;
  client_organization_id: string;
  owner_organization_id: string;
  name: string;
  service_type: string;
  source: string;
  status: string;
}


function formatValue(
  value: string,
) {
  return value
    .replaceAll("_", " ")
    .replace(
      /\b\w/g,
      (character) =>
        character.toUpperCase(),
    );
}


export function OrganizationManagementWorkspace() {
  const [
    organizations,
    setOrganizations,
  ] = useState<Organization[]>([]);

  const [
    selectedOrganization,
    setSelectedOrganization,
  ] = useState<Organization | null>(
    null,
  );

  const [
    engagements,
    setEngagements,
  ] = useState<Engagement[]>([]);

  const [
    addingEngagement,
    setAddingEngagement,
  ] = useState(false);

  const [
    engagementName,
    setEngagementName,
  ] = useState("");

  const [
    serviceType,
    setServiceType,
  ] = useState("");

  const [
    source,
    setSource,
  ] = useState("direct");


  const [
    editingOrganization,
    setEditingOrganization,
  ] = useState(false);

  const [
    organizationName,
    setOrganizationName,
  ] = useState("");

  const [
    organizationStatus,
    setOrganizationStatus,
  ] = useState("active");

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    saving,
    setSaving,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState("");

  const [
    notice,
    setNotice,
  ] = useState("");


  useEffect(() => {
    async function loadOrganizations() {
      try {
        const [
          clientsResponse,
          platformResponse,
        ] = await Promise.all([
          fetch(
            "/api/admin/organizations",
            {
              cache: "no-store",
            },
          ),
          fetch(
            "/api/admin/platform-organization",
            {
              cache: "no-store",
            },
          ),
        ]);

        const clients =
          await clientsResponse.json();

        const platform =
          await platformResponse.json();

        if (!clientsResponse.ok) {
          throw new Error(
            clients?.detail ??
              "Unable to load organizations."
          );
        }

        if (!platformResponse.ok) {
          throw new Error(
            platform?.detail ??
              "Unable to load Paradigm Ra."
          );
        }

        setOrganizations([
          platform,
          ...clients,
        ]);

      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Unable to load organizations."
        );

      } finally {
        setLoading(false);
      }
    }

    loadOrganizations();
  }, []);


  async function openOrganization(
    organization: Organization,
  ) {
    setSelectedOrganization(
      organization
    );

    setOrganizationName(
      organization.name
    );

    setOrganizationStatus(
      organization.status
    );

    setEditingOrganization(false);
    setAddingEngagement(false);
    setEngagements([]);
    setError("");
    setNotice("");

    const response = await fetch(
      `/api/admin/organizations/${organization.id}/engagements`,
      {
        cache: "no-store",
      },
    );

    const data =
      await response.json();

    if (!response.ok) {
      setError(
        data?.detail ??
          "Unable to load engagements."
      );

      return;
    }

    setEngagements(data);
  }


  async function handleAddEngagement(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!selectedOrganization) {
      return;
    }

    setSaving(true);
    setError("");
    setNotice("");

    try {
      const response = await fetch(
        `/api/admin/organizations/${selectedOrganization.id}/engagements`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            name:
              engagementName.trim(),
            service_type:
              serviceType.trim(),
            source,
            status: "proposed",
          }),
        },
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ??
            "Unable to create engagement."
        );
      }

      setEngagements(
        (current) => [
          ...current,
          data,
        ],
      );

      setEngagementName("");
      setServiceType("");
      setSource("direct");
      setAddingEngagement(false);

      setNotice(
        `${data.name} engagement created.`
      );

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to create engagement."
      );

    } finally {
      setSaving(false);
    }
  }


  async function handleOrganizationSave(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!selectedOrganization) {
      return;
    }

    setSaving(true);
    setError("");
    setNotice("");

    try {
      const response = await fetch(
        `/api/admin/organizations/${selectedOrganization.id}`,
        {
          method: "PUT",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            name:
              organizationName.trim(),
            status:
              organizationStatus,
          }),
        },
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ??
            "Unable to update organization."
        );
      }

      setSelectedOrganization(
        data
      );

      setOrganizations(
        (current) =>
          current.map(
            (organization) =>
              organization.id
              === data.id
                ? data
                : organization
          )
      );

      setOrganizationName(
        data.name
      );

      setOrganizationStatus(
        data.status
      );

      setEditingOrganization(false);

      setNotice(
        "Organization updated."
      );

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to update organization."
      );

    } finally {
      setSaving(false);
    }
  }


  if (loading) {
    return (
      <p className="admin-platform-empty">
        Loading organizations…
      </p>
    );
  }


  if (!selectedOrganization) {
    return (
      <div className="admin-org-workspace">
        {error ? (
          <p className="admin-error">
            {error}
          </p>
        ) : null}

        <section className="admin-platform-section">
          <div className="admin-section-heading">
            <div>
              <p className="kicker">
                ORGANIZATIONS
              </p>

              <h3>
                Operating entities
              </h3>
            </div>
          </div>

          <div className="admin-org-list">
            {organizations.map(
              (organization) => (
                <button
                  key={organization.id}
                  type="button"
                  className="admin-org-card"
                  onClick={() =>
                    openOrganization(
                      organization
                    )
                  }
                >
                  <div>
                    <span>
                      {formatValue(
                        organization.type
                      )}
                    </span>

                    <strong>
                      {organization.name}
                    </strong>
                  </div>

                  <small>
                    {formatValue(
                      organization.status
                    )}
                  </small>

                  <b>
                    Manage →
                  </b>
                </button>
              ),
            )}
          </div>
        </section>
      </div>
    );
  }


  return (
    <div className="admin-org-workspace">
      <button
        type="button"
        className="admin-workspace-back"
        onClick={() => {
          setSelectedOrganization(
            null
          );
          setEngagements([]);
          setError("");
          setNotice("");
        }}
      >
        ← Organizations
      </button>

      <section className="admin-org-hero">
        <div>
          <p className="kicker">
            {formatValue(
              selectedOrganization.type
            )}
          </p>

          <h2>
            {selectedOrganization.name}
          </h2>

          <span className="admin-status-pill admin-status-active">
            {formatValue(
              selectedOrganization.status
            )}
          </span>
        </div>

        <div className="admin-org-hero-actions">
          <button
            type="button"
            className="admin-org-edit-button"
            onClick={() => {
              setOrganizationName(
                selectedOrganization.name
              );

              setOrganizationStatus(
                selectedOrganization.status
              );

              setEditingOrganization(
                true
              );
            }}
          >
            Edit Organization
          </button>

          <button
            type="button"
            className="button button-primary"
            onClick={() =>
              setAddingEngagement(
                true
              )
            }
          >
            + Add Engagement
          </button>
        </div>
      </section>

      {error ? (
        <p className="admin-error">
          {error}
        </p>
      ) : null}

      {notice ? (
        <p className="admin-notice">
          {notice}
        </p>
      ) : null}

      {editingOrganization ? (
        <form
          className="admin-org-identity-form"
          onSubmit={
            handleOrganizationSave
          }
        >
          <div>
            <p className="kicker">
              ORGANIZATION IDENTITY
            </p>

            <h3>
              Edit organization
            </h3>
          </div>

          <label>
            <span>
              Company Name
            </span>

            <input
              required
              value={
                organizationName
              }
              onChange={(event) =>
                setOrganizationName(
                  event.target.value
                )
              }
            />
          </label>

          <label>
            <span>
              Status
            </span>

            <select
              value={
                organizationStatus
              }
              onChange={(event) =>
                setOrganizationStatus(
                  event.target.value
                )
              }
            >
              <option value="active">
                Active
              </option>

              <option value="inactive">
                Inactive
              </option>
            </select>
          </label>

          <div className="admin-org-edit-actions">
            <button
              type="button"
              className="admin-cancel-button"
              onClick={() =>
                setEditingOrganization(
                  false
                )
              }
            >
              Cancel
            </button>

            <button
              type="submit"
              className="button button-primary"
              disabled={saving}
            >
              {saving
                ? "Saving…"
                : "Save Organization"}
            </button>
          </div>
        </form>
      ) : null}

      <div className="admin-org-overview-grid">
        <OrganizationCompanyProfileCard
          organizationId={
            selectedOrganization.id
          }
        />

        <OrganizationContactsCard
          organizationId={
            selectedOrganization.id
          }
        />
      </div>

      <OrganizationBillingProfileEditor
        organizationId={
          selectedOrganization.id
        }
        organizationName={
          selectedOrganization.name
        }
      />

      <section className="admin-platform-section">
        <div className="admin-section-heading">
          <div>
            <p className="kicker">
              ENGAGEMENTS
            </p>

            <h3>
              Active work faucets
            </h3>
          </div>
        </div>

        {addingEngagement ? (
          <form
            className="admin-engagement-create"
            onSubmit={
              handleAddEngagement
            }
          >
            <label>
              <span>
                Engagement Name
              </span>

              <input
                required
                value={engagementName}
                onChange={(event) =>
                  setEngagementName(
                    event.target.value
                  )
                }
                placeholder="Bookkeeping"
              />
            </label>

            <label>
              <span>
                Service Type
              </span>

              <input
                required
                value={serviceType}
                onChange={(event) =>
                  setServiceType(
                    event.target.value
                  )
                }
                placeholder="bookkeeping"
              />
            </label>

            <label>
              <span>
                Source
              </span>

              <select
                value={source}
                onChange={(event) =>
                  setSource(
                    event.target.value
                  )
                }
              >
                <option value="direct">
                  Direct
                </option>

                <option value="contract_conversion">
                  Contract Conversion
                </option>

                <option value="partner">
                  Partner
                </option>

                <option value="existing_client">
                  Existing Client
                </option>

                <option value="referral">
                  Referral
                </option>

                <option value="website">
                  Website
                </option>

                <option value="event">
                  Event
                </option>

                <option value="other">
                  Other
                </option>
              </select>
            </label>

            <div className="admin-engagement-create-actions">
              <button
                type="button"
                className="admin-cancel-button"
                onClick={() =>
                  setAddingEngagement(
                    false
                  )
                }
              >
                Cancel
              </button>

              <button
                type="submit"
                className="button button-primary"
                disabled={saving}
              >
                {saving
                  ? "Creating…"
                  : "Create Engagement"}
              </button>
            </div>
          </form>
        ) : null}

        <div className="admin-engagement-list">
          {engagements.length ? (
            engagements.map(
              (engagement) => (
                <article
                  key={engagement.id}
                  className="admin-engagement-card"
                >
                  <div>
                    <span>
                      {formatValue(
                        engagement.service_type
                      )}
                    </span>

                    <strong>
                      {engagement.name}
                    </strong>

                    <small>
                      {formatValue(
                        engagement.source
                      )}
                      {" · "}
                      {formatValue(
                        engagement.status
                      )}
                    </small>
                  </div>

                  <button
                    type="button"
                    className="admin-inline-action"
                  >
                    Open Engagement →
                  </button>
                </article>
              ),
            )
          ) : (
            <p className="admin-platform-empty">
              No engagements yet.
            </p>
          )}
        </div>
      </section>
    </div>
  );
}
