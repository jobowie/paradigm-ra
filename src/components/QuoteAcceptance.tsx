"use client";

import {
  useEffect,
  useState,
} from "react";


const PLATFORM_API =
  "https://ra-platform-api.onrender.com";


interface QuoteAcceptanceProps {
  token: string;
  initialStatus: string;
  acceptedAt: string | null;
}


interface DepositStatus {
  deposit_amount: string;
  invoice_number: string | null;
  invoice_status: string | null;
  amount_paid: string;
  balance_due: string;
  deposit_paid: boolean;
}


function money(
  value: string,
): string {
  return new Intl.NumberFormat(
    "en-US",
    {
      style: "currency",
      currency: "USD",
    },
  ).format(Number(value));
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

  const [deposit, setDeposit] =
    useState<DepositStatus | null>(
      null,
    );

  const [loading, setLoading] =
    useState(false);

  const [paymentLoading, setPaymentLoading] =
    useState(false);

  const [error, setError] =
    useState("");


  useEffect(() => {
    if (status !== "accepted") {
      return;
    }

    const controller =
      new AbortController();

    async function loadPaymentStatus() {
      try {
        const response = await fetch(
          `${PLATFORM_API}/quotes/public/${encodeURIComponent(
            token,
          )}/payment-status`,
          {
            cache: "no-store",
            signal:
              controller.signal,
          },
        );

        if (!response.ok) {
          throw new Error(
            "Unable to load payment status.",
          );
        }

        const data =
          (await response.json()) as DepositStatus;

        setDeposit(data);

      } catch (err) {
        if (
          err instanceof DOMException &&
          err.name === "AbortError"
        ) {
          return;
        }

        setError(
          err instanceof Error
            ? err.message
            : "Unable to load payment status.",
        );
      }
    }

    loadPaymentStatus();

    return () => {
      controller.abort();
    };
  }, [status, token]);


  async function handleAccept() {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${PLATFORM_API}/quotes/public/${encodeURIComponent(
          token,
        )}/accept`,
        {
          method: "POST",
        },
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ??
            "Unable to accept quote.",
        );
      }

      setStatus(data.status);
      setAccepted(
        data.accepted_at,
      );

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


  async function handlePayment() {
    setPaymentLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${PLATFORM_API}/quotes/public/${encodeURIComponent(
          token,
        )}/checkout`,
        {
          method: "POST",
        },
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ??
            "Unable to start payment.",
        );
      }

      if (!data.checkout_url) {
        throw new Error(
          "Checkout URL was not returned.",
        );
      }

      window.location.assign(
        data.checkout_url,
      );

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to start payment.",
      );

      setPaymentLoading(false);
    }
  }


  if (status === "accepted") {
    return (
      <div className="quote-action">
        <div className="quote-accepted">
          <span className="quote-status-dot" />

          <div>
            <strong>
              Quote accepted
            </strong>

            <p>
              Paradigm Ra has recorded
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


        {deposit?.deposit_paid ? (
          <div className="quote-accepted">
            <span className="quote-status-dot" />

            <div>
              <strong>
                Deposit received
              </strong>

              <p>
                {money(
                  deposit.amount_paid,
                )}{" "}
                project deposit received.
              </p>

              <small>
                {deposit.invoice_number}
                {" · "}
                Balance due on this
                invoice:{" "}
                {money(
                  deposit.balance_due,
                )}
              </small>
            </div>
          </div>
        ) : (
          <>
            <button
              className="button button-primary quote-accept-button"
              type="button"
              disabled={
                paymentLoading ||
                !deposit
              }
              onClick={
                handlePayment
              }
            >
              {paymentLoading
                ? "Opening secure checkout…"
                : deposit
                  ? `Pay ${money(
                      deposit.deposit_amount,
                    )} Project Deposit`
                  : "Loading payment…"}
            </button>

            <p className="quote-accept-copy">
              Secure payment is processed
              through Stripe. Your project
              begins after the deposit is
              confirmed.
            </p>
          </>
        )}


        {error ? (
          <p className="quote-error">
            {error}
          </p>
        ) : null}
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
