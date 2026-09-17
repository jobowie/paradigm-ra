"use client";

import { useState } from "react";

interface QuoteAcceptanceProps {
  token: string;
  initialStatus: string;
  acceptedAt: string | null;
}

export function QuoteAcceptance({
  token,
  initialStatus,
  acceptedAt,
}: QuoteAcceptanceProps) {
  const [status, setStatus] = useState(
    initialStatus,
  );

  const [accepted, setAccepted] = useState(
    acceptedAt,
  );

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleAccept() {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        `https://ra-platform-api.onrender.com/quotes/public/${encodeURIComponent(token)}/accept`,
        {
          method: "POST",
        },
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ??
            "Unable to accept quote.",
        );
      }

      setStatus(data.status);
      setAccepted(data.accepted_at);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to accept quote.",
      );
    } finally {
      setLoading(false);
    }
  }

  if (status === "accepted") {
    return (
      <div className="quote-accepted">
        <span className="quote-status-dot" />
        <div>
          <strong>Quote accepted</strong>
          <p>
            Thank you. Paradigm Ra has recorded
            your acceptance.
          </p>

          {accepted ? (
            <small>
              Accepted{" "}
              {new Date(
                accepted,
              ).toLocaleString()}
            </small>
          ) : null}
        </div>
      </div>
    );
  }

  return (
    <div className="quote-action">
      <button
        className="button button-primary quote-accept-button"
        type="button"
        disabled={loading}
        onClick={handleAccept}
      >
        {loading
          ? "Accepting…"
          : "Accept Quote"}
      </button>

      <p className="quote-accept-copy">
        By accepting, you approve the scope,
        total, and payment terms shown above.
      </p>

      {error ? (
        <p className="quote-error">
          {error}
        </p>
      ) : null}
    </div>
  );
}
