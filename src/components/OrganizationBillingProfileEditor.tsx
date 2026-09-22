"use client";

import {
  FormEvent,
  useEffect,
  useState,
} from "react";


interface BillingProfile {
  id: string | null;
  organization_id: string;

  billing_name: string | null;
  billing_email: string | null;

  address_line1: string | null;
  address_line2: string | null;
  city: string | null;
  state_region: string | null;
  postal_code: string | null;
  country: string;

  bank_name: string | null;
  account_type: string | null;

  has_routing_number: boolean;
  routing_number_masked: string | null;

  has_account_number: boolean;
  account_number_masked: string | null;
}


interface Props {
  organizationId: string;
  organizationName: string;
  title?: string;
}


export function OrganizationBillingProfileEditor({
  organizationId,
  organizationName,
  title,
}: Props) {
  const [
    profile,
    setProfile,
  ] = useState<BillingProfile | null>(
    null,
  );


  const [
    editing,
    setEditing,
  ] = useState(false);

  const [
    billingName,
    setBillingName,
  ] = useState("");

  const [
    billingEmail,
    setBillingEmail,
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
    bankName,
    setBankName,
  ] = useState("");

  const [
    accountType,
    setAccountType,
  ] = useState("");

  const [
    routingNumber,
    setRoutingNumber,
  ] = useState("");

  const [
    accountNumber,
    setAccountNumber,
  ] = useState("");

  const [
    clearRouting,
    setClearRouting,
  ] = useState(false);

  const [
    clearAccount,
    setClearAccount,
  ] = useState(false);

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
    data: BillingProfile,
  ) {
    setProfile(data);

    setBillingName(
      data.billing_name ?? ""
    );

    setBillingEmail(
      data.billing_email ?? ""
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

    setBankName(
      data.bank_name ?? ""
    );

    setAccountType(
      data.account_type ?? ""
    );

    setRoutingNumber("");
    setAccountNumber("");
    setClearRouting(false);
    setClearAccount(false);
  }


  useEffect(() => {
    async function load() {
      setLoading(true);
      setError("");

      try {
        const response = await fetch(
          `/api/admin/organizations/${organizationId}/billing-profile`,
          {
            cache: "no-store",
          },
        );

        const data =
          await response.json();

        if (!response.ok) {
          throw new Error(
            data?.detail ??
              "Unable to load billing profile."
          );
        }

        hydrate(data);

      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Unable to load billing profile."
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

    const payload: Record<
      string,
      unknown
    > = {
      billing_name:
        billingName || null,
      billing_email:
        billingEmail || null,
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
      bank_name:
        bankName || null,
      account_type:
        accountType || null,
    };

    if (routingNumber.trim()) {
      payload.routing_number =
        routingNumber.trim();
    }

    if (accountNumber.trim()) {
      payload.account_number =
        accountNumber.trim();
    }

    if (clearRouting) {
      payload.clear_routing_number =
        true;
    }

    if (clearAccount) {
      payload.clear_account_number =
        true;
    }

    try {
      const response = await fetch(
        `/api/admin/organizations/${organizationId}/billing-profile`,
        {
          method: "PUT",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify(
            payload
          ),
        },
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ??
            "Unable to save billing profile."
        );
      }

      hydrate(data);

      setEditing(false);

      setNotice(
        "Billing profile saved."
      );

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to save billing profile."
      );

    } finally {
      setSaving(false);
    }
  }


  if (loading) {
    return (
      <p className="admin-platform-empty">
        Loading billing profile…
      </p>
    );
  }


  if (!editing) {
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

    return (
      <section className="admin-org-profile-card">
        <div className="admin-section-heading">
          <div>
            <p className="kicker">
              BILLING PROFILE
            </p>

            <h3>
              {title ?? organizationName}
            </h3>
          </div>

          <button
            type="button"
            className="admin-inline-action"
            onClick={() =>
              setEditing(true)
            }
          >
            Edit Billing Profile
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

        <div className="admin-org-profile-grid">
          <div>
            <span>Billing Identity</span>

            <strong>
              {profile?.billing_name
                || organizationName}
            </strong>

            <small>
              {profile?.billing_email
                || "No billing email"}
            </small>
          </div>

          <div>
            <span>Address</span>

            {address.length ? (
              address.map(
                (line) => (
                  <small key={line}>
                    {line}
                  </small>
                ),
              )
            ) : (
              <small>
                No billing address
              </small>
            )}
          </div>

          <div>
            <span>
              Secure Account Information
            </span>

            <strong>
              {profile?.bank_name
                || "Not configured"}
            </strong>

            <small>
              {profile?.account_type
                || ""}
            </small>

            <small>
              Routing{" "}
              {profile?.routing_number_masked
                || "—"}
            </small>

            <small>
              Account{" "}
              {profile?.account_number_masked
                || "—"}
            </small>
          </div>
        </div>
      </section>
    );
  }


  return (
    <section className="admin-platform-section admin-billing-profile">
      <div className="admin-section-heading">
        <div>
          <p className="kicker">
            BILLING PROFILE
          </p>

          <h3>
            {title ?? organizationName}
          </h3>
        </div>
      </div>

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

      <form
        className="admin-billing-profile-form"
        onSubmit={handleSave}
      >
        <label>
          <span>
            Billing Name
          </span>

          <input
            value={billingName}
            onChange={(event) =>
              setBillingName(
                event.target.value
              )
            }
          />
        </label>

        <label>
          <span>
            Billing Email
          </span>

          <input
            type="email"
            value={billingEmail}
            onChange={(event) =>
              setBillingEmail(
                event.target.value
              )
            }
          />
        </label>

        <label className="admin-billing-profile-wide">
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

        <label className="admin-billing-profile-wide">
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

        <label>
          <span>Country</span>

          <input
            value={country}
            onChange={(event) =>
              setCountry(
                event.target.value
              )
            }
          />
        </label>

        <label>
          <span>Bank Name</span>

          <input
            value={bankName}
            onChange={(event) =>
              setBankName(
                event.target.value
              )
            }
          />
        </label>

        <label>
          <span>Account Type</span>

          <input
            value={accountType}
            onChange={(event) =>
              setAccountType(
                event.target.value
              )
            }
            placeholder="Checking"
          />
        </label>

        <label>
          <span>
            Routing Number
          </span>

          <input
            type="password"
            autoComplete="off"
            value={routingNumber}
            onChange={(event) =>
              setRoutingNumber(
                event.target.value
              )
            }
            placeholder={
              profile?.routing_number_masked
              ?? "Not stored"
            }
          />
        </label>

        <label>
          <span>
            Account Number
          </span>

          <input
            type="password"
            autoComplete="off"
            value={accountNumber}
            onChange={(event) =>
              setAccountNumber(
                event.target.value
              )
            }
            placeholder={
              profile?.account_number_masked
              ?? "Not stored"
            }
          />
        </label>

        {profile?.has_routing_number ? (
          <label className="admin-billing-clear">
            <input
              type="checkbox"
              checked={clearRouting}
              onChange={(event) =>
                setClearRouting(
                  event.target.checked
                )
              }
            />

            <span>
              Remove stored routing number
            </span>
          </label>
        ) : null}

        {profile?.has_account_number ? (
          <label className="admin-billing-clear">
            <input
              type="checkbox"
              checked={clearAccount}
              onChange={(event) =>
                setClearAccount(
                  event.target.checked
                )
              }
            />

            <span>
              Remove stored account number
            </span>
          </label>
        ) : null}

        <div className="admin-billing-profile-actions">
          <button
            type="button"
            className="admin-cancel-button"
            onClick={() => {
              hydrate(profile!);
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
              : "Save Billing Profile"}
          </button>
        </div>
      </form>
    </section>
  );
}
