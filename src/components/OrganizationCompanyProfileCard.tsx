"use client";

import {
  FormEvent,
  useEffect,
  useState,
} from "react";


interface CompanyProfile {
  id: string | null;
  organization_id: string;

  business_type: string | null;
  industry: string | null;
  website: string | null;
  phone: string | null;
  company_size: string | null;

  address_line1: string | null;
  address_line2: string | null;
  city: string | null;
  state_region: string | null;
  postal_code: string | null;
  country: string;
}


interface Props {
  organizationId: string;
}


export function OrganizationCompanyProfileCard({
  organizationId,
}: Props) {
  const [
    profile,
    setProfile,
  ] = useState<CompanyProfile | null>(
    null,
  );

  const [
    editing,
    setEditing,
  ] = useState(false);

  const [
    businessType,
    setBusinessType,
  ] = useState("");

  const [
    industry,
    setIndustry,
  ] = useState("");

  const [
    website,
    setWebsite,
  ] = useState("");

  const [
    phone,
    setPhone,
  ] = useState("");

  const [
    companySize,
    setCompanySize,
  ] = useState("");

  const [
    addressLine1,
    setAddressLine1,
  ] = useState("");

  const [
    addressLine2,
    setAddressLine2,
  ] = useState("");

  const [
    city,
    setCity,
  ] = useState("");

  const [
    stateRegion,
    setStateRegion,
  ] = useState("");

  const [
    postalCode,
    setPostalCode,
  ] = useState("");

  const [
    country,
    setCountry,
  ] = useState("US");

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


  function hydrate(
    data: CompanyProfile,
  ) {
    setProfile(data);

    setBusinessType(
      data.business_type ?? ""
    );

    setIndustry(
      data.industry ?? ""
    );

    setWebsite(
      data.website ?? ""
    );

    setPhone(
      data.phone ?? ""
    );

    setCompanySize(
      data.company_size ?? ""
    );

    setAddressLine1(
      data.address_line1 ?? ""
    );

    setAddressLine2(
      data.address_line2 ?? ""
    );

    setCity(
      data.city ?? ""
    );

    setStateRegion(
      data.state_region ?? ""
    );

    setPostalCode(
      data.postal_code ?? ""
    );

    setCountry(
      data.country || "US"
    );
  }


  useEffect(() => {
    async function load() {
      setLoading(true);
      setError("");

      try {
        const response = await fetch(
          `/api/admin/organizations/${organizationId}/company-profile`,
          {
            cache: "no-store",
          },
        );

        const data =
          await response.json();

        if (!response.ok) {
          throw new Error(
            data?.detail ??
              "Unable to load company profile."
          );
        }

        hydrate(data);

      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Unable to load company profile."
        );

      } finally {
        setLoading(false);
      }
    }

    load();
  }, [organizationId]);


  async function handleSave(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setSaving(true);
    setError("");
    setNotice("");

    try {
      const response = await fetch(
        `/api/admin/organizations/${organizationId}/company-profile`,
        {
          method: "PUT",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            business_type:
              businessType || null,
            industry:
              industry || null,
            website:
              website || null,
            phone:
              phone || null,
            company_size:
              companySize || null,
            address_line1:
              addressLine1 || null,
            address_line2:
              addressLine2 || null,
            city:
              city || null,
            state_region:
              stateRegion || null,
            postal_code:
              postalCode || null,
            country:
              country || "US",
          }),
        },
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ??
            "Unable to save company profile."
        );
      }

      hydrate(data);

      setEditing(false);

      setNotice(
        "Company profile saved."
      );

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to save company profile."
      );

    } finally {
      setSaving(false);
    }
  }


  if (loading) {
    return (
      <section className="admin-org-detail-card">
        <p className="admin-platform-empty">
          Loading company profile…
        </p>
      </section>
    );
  }


  const address = [
    profile?.address_line1,
    profile?.address_line2,
    [
      profile?.city,
      profile?.state_region,
      profile?.postal_code,
    ]
      .filter(Boolean)
      .join(" "),
    profile?.country,
  ].filter(Boolean);


  if (!editing) {
    return (
      <section className="admin-org-detail-card">
        <div className="admin-section-heading">
          <div>
            <p className="kicker">
              COMPANY PROFILE
            </p>

            <h3>
              Company details
            </h3>
          </div>

          <button
            type="button"
            className="admin-inline-action"
            onClick={() =>
              setEditing(true)
            }
          >
            Edit →
          </button>
        </div>

        {notice ? (
          <p className="admin-notice">
            {notice}
          </p>
        ) : null}

        {error ? (
          <p className="admin-error">
            {error}
          </p>
        ) : null}

        <div className="admin-org-detail-grid">
          <div>
            <span>
              Business Type
            </span>

            <strong>
              {profile?.business_type
                || "Not specified"}
            </strong>
          </div>

          <div>
            <span>
              Industry
            </span>

            <strong>
              {profile?.industry
                || "Not specified"}
            </strong>
          </div>

          <div>
            <span>
              Website
            </span>

            <strong>
              {profile?.website
                || "Not specified"}
            </strong>
          </div>

          <div>
            <span>
              Phone
            </span>

            <strong>
              {profile?.phone
                || "Not specified"}
            </strong>
          </div>

          <div>
            <span>
              Company Size
            </span>

            <strong>
              {profile?.company_size
                || "Not specified"}
            </strong>
          </div>

          <div className="admin-org-detail-wide">
            <span>
              Primary Address
            </span>

            {address.length ? (
              address.map(
                (line) => (
                  <strong key={line}>
                    {line}
                  </strong>
                ),
              )
            ) : (
              <strong>
                Not specified
              </strong>
            )}
          </div>
        </div>
      </section>
    );
  }


  return (
    <section className="admin-org-detail-card">
      <div className="admin-section-heading">
        <div>
          <p className="kicker">
            COMPANY PROFILE
          </p>

          <h3>
            Edit company details
          </h3>
        </div>
      </div>

      <form
        className="admin-org-edit-form"
        onSubmit={handleSave}
      >
        <label>
          <span>
            Business Type
          </span>

          <input
            value={businessType}
            onChange={(event) =>
              setBusinessType(
                event.target.value
              )
            }
            placeholder="Coffee Shop"
          />
        </label>

        <label>
          <span>
            Industry
          </span>

          <input
            value={industry}
            onChange={(event) =>
              setIndustry(
                event.target.value
              )
            }
            placeholder="Food & Beverage"
          />
        </label>

        <label>
          <span>
            Website
          </span>

          <input
            value={website}
            onChange={(event) =>
              setWebsite(
                event.target.value
              )
            }
            placeholder="https://..."
          />
        </label>

        <label>
          <span>
            Phone
          </span>

          <input
            value={phone}
            onChange={(event) =>
              setPhone(
                event.target.value
              )
            }
          />
        </label>

        <label>
          <span>
            Company Size
          </span>

          <input
            value={companySize}
            onChange={(event) =>
              setCompanySize(
                event.target.value
              )
            }
            placeholder="11–50"
          />
        </label>

        <label>
          <span>
            Country
          </span>

          <input
            value={country}
            onChange={(event) =>
              setCountry(
                event.target.value
              )
            }
          />
        </label>

        <label className="admin-org-edit-wide">
          <span>
            Address Line 1
          </span>

          <input
            value={addressLine1}
            onChange={(event) =>
              setAddressLine1(
                event.target.value
              )
            }
          />
        </label>

        <label className="admin-org-edit-wide">
          <span>
            Address Line 2
          </span>

          <input
            value={addressLine2}
            onChange={(event) =>
              setAddressLine2(
                event.target.value
              )
            }
          />
        </label>

        <label>
          <span>City</span>

          <input
            value={city}
            onChange={(event) =>
              setCity(
                event.target.value
              )
            }
          />
        </label>

        <label>
          <span>
            State / Region
          </span>

          <input
            value={stateRegion}
            onChange={(event) =>
              setStateRegion(
                event.target.value
              )
            }
          />
        </label>

        <label>
          <span>
            Postal Code
          </span>

          <input
            value={postalCode}
            onChange={(event) =>
              setPostalCode(
                event.target.value
              )
            }
          />
        </label>

        <div className="admin-org-edit-actions">
          <button
            type="button"
            className="admin-cancel-button"
            onClick={() => {
              if (profile) {
                hydrate(profile);
              }

              setEditing(false);
              setError("");
            }}
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
              : "Save Company Profile"}
          </button>
        </div>
      </form>
    </section>
  );
}
