"use client";

import {
  FormEvent,
  useState,
} from "react";

const DEFAULT_SCOPE = "";

function defaultExpiration() {
  const date = new Date();

  date.setDate(
    date.getDate() + 14,
  );

  return date
    .toISOString()
    .slice(0, 10);
}

export function AdminQuoteForm() {

  const [clientName, setClientName] =
    useState("");

  const [
    clientEmail,
    setClientEmail,
  ] = useState("");

  const [
    projectName,
    setProjectName,
  ] = useState("");

  const [
    serviceType,
    setServiceType,
  ] = useState("");

  const [scope, setScope] =
    useState(DEFAULT_SCOPE);

  const [deposit, setDeposit] =
    useState("");

  const [
    deployment,
    setDeployment,
  ] = useState("");

  const [terms, setTerms] =
    useState(
      "50% project deposit due upon acceptance. Remaining balance due prior to production deployment and launch. Ongoing support is separate from the initial website build.",
    );

  const [
    expirationDate,
    setExpirationDate,
  ] = useState(
    defaultExpiration(),
  );

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [result, setResult] =
    useState<{
      quote_number: string;
      total: string;
      public_url: string;
    } | null>(null);

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(
        "/api/admin/quotes",
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            client_name:
              clientName,
            client_email:
              clientEmail ||
              null,
            project_name:
              projectName,
            service_type:
              serviceType,
            scope_items:
              scope
                .split("\n")
                .map(
                  (item) =>
                    item.trim(),
                )
                .filter(Boolean),
            deposit_amount:
              deposit,
            deployment_amount:
              deployment,
            terms,
            expiration_date:
              expirationDate,
          }),
        },
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ??
            "Unable to create quote.",
        );
      }

      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to create quote.",
      );
    } finally {
      setLoading(false);
    }
  }

  async function copyLink() {
    if (!result) {
      return;
    }

    await navigator.clipboard.writeText(
      result.public_url,
    );
  }

  return (
    <form
      className="admin-quote-form"
      onSubmit={handleSubmit}
    >
      <div className="admin-form-grid">
        <label>
          <span>Client</span>
          <input
            required
            value={clientName}
            onChange={(event) =>
              setClientName(
                event.target.value,
              )
            }
          />
        </label>

        <label>
          <span>
            Client Email
          </span>
          <input
            type="email"
            value={clientEmail}
            onChange={(event) =>
              setClientEmail(
                event.target.value,
              )
            }
          />
        </label>

        <label>
          <span>Project</span>
          <input
            required
            value={projectName}
            onChange={(event) =>
              setProjectName(
                event.target.value,
              )
            }
          />
        </label>

        <label>
          <span>
            Service Type
          </span>

          <select
            required
            value={serviceType}
            onChange={(event) =>
              setServiceType(
                event.target.value
              )
            }
          >
            <option
              value=""
              disabled
            >
              Select service
            </option>

            <option value="web_software_solutions">
              Web & Software Solutions
            </option>

            <option value="bookkeeping">
              Bookkeeping
            </option>

            <option value="business_automation">
              Business Automation
            </option>

            <option value="business_systems_technical_consulting">
              Business Systems & Technical Consulting
            </option>

            <option value="other">
              Other
            </option>
          </select>
        </label>

        <label>
          <span>
            Project Deposit
          </span>
          <input
            type="number"
            step="0.01"
            min="0"
            required
            value={deposit}
            onChange={(event) =>
              setDeposit(
                event.target.value,
              )
            }
          />
        </label>

        <label>
          <span>
            Deployment Balance
          </span>
          <input
            type="number"
            step="0.01"
            min="0"
            required
            value={deployment}
            onChange={(event) =>
              setDeployment(
                event.target.value,
              )
            }
          />
        </label>

        <label>
          <span>
            Quote Expiration
          </span>
          <input
            type="date"
            required
            value={
              expirationDate
            }
            onChange={(event) =>
              setExpirationDate(
                event.target.value,
              )
            }
          />
        </label>
      </div>

      <label>
        <span>
          Projected Work
        </span>

        <textarea
          rows={10}
          required
          value={scope}
          onChange={(event) =>
            setScope(
              event.target.value,
            )
          }
        />
      </label>

      <label>
        <span>Terms</span>

        <textarea
          rows={5}
          required
          value={terms}
          onChange={(event) =>
            setTerms(
              event.target.value,
            )
          }
        />
      </label>

      <div className="admin-total-preview">
        <span>
          PROJECT TOTAL
        </span>

        <strong>
          $
          {(
            Number(deposit || 0) +
            Number(
              deployment || 0,
            )
          ).toFixed(2)}
        </strong>

        <small>
          Final total is calculated
          again by the Python
          billing domain.
        </small>
      </div>

      <button
        className="button button-primary"
        type="submit"
        disabled={loading}
      >
        {loading
          ? "Creating Quote…"
          : "Create Client Quote"}
      </button>

      {error ? (
        <p className="quote-error">
          {error}
        </p>
      ) : null}

      {result ? (
        <div className="admin-quote-result">
          <p>
            Quote created
          </p>

          <strong>
            {result.quote_number}
          </strong>

          <span>
            ${result.total}
          </span>

          <a
            href={result.public_url}
            target="_blank"
            rel="noreferrer"
          >
            {result.public_url}
          </a>

          <button
            type="button"
            className="button button-secondary"
            onClick={copyLink}
          >
            Copy Client Link
          </button>
        </div>
      ) : null}
    </form>
  );
}
