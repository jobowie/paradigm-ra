"use client";

import {
  useEffect,
  useState,
} from "react";

import {
  QuoteAcceptance,
} from "@/components/QuoteAcceptance";


const PLATFORM_API =
  "https://ra-platform-api.onrender.com";


interface PublicQuoteLine {
  description: string;
  quantity: string;
  unit_rate: string;
  amount: string;
}


interface PublicQuote {
  quote_number: string;
  status: string;

  issue_date: string | null;
  expiration_date: string | null;

  bill_to_name: string;

  line_items: PublicQuoteLine[];

  subtotal: string;
  tax_amount: string;
  total: string;

  notes: string | null;
  terms: string | null;

  sent_at: string | null;
  accepted_at: string | null;
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


function dateLabel(
  value: string | null,
): string {
  if (!value) {
    return "—";
  }

  return new Intl.DateTimeFormat(
    "en-US",
    {
      month: "short",
      day: "numeric",
      year: "numeric",
      timeZone: "UTC",
    },
  ).format(
    new Date(
      `${value}T00:00:00Z`,
    ),
  );
}


export function PublicQuoteClient({
  token,
}: {
  token: string;
}) {
  const [quote, setQuote] =
    useState<PublicQuote | null>(
      null,
    );

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  useEffect(() => {
    const controller =
      new AbortController();

    async function loadQuote() {
      try {
        const response =
          await fetch(
            `${PLATFORM_API}/quotes/public/${encodeURIComponent(
              token,
            )}`,
            {
              cache: "no-store",
              signal:
                controller.signal,
            },
          );

        if (!response.ok) {
          throw new Error(
            response.status === 404
              ? "Quote not found."
              : "Unable to load quote.",
          );
        }

        const data =
          (await response.json()) as PublicQuote;

        setQuote(data);
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
            : "Unable to load quote.",
        );
      } finally {
        setLoading(false);
      }
    }

    loadQuote();

    return () => {
      controller.abort();
    };
  }, [token]);


  if (loading) {
    return (
      <main className="quote-page">
        <div className="shell quote-shell">
          <p className="kicker">
            PARADIGM RA
          </p>

          <h1>
            Loading quote…
          </h1>
        </div>
      </main>
    );
  }


  if (error || !quote) {
    return (
      <main className="quote-page">
        <div className="shell quote-shell">
          <p className="kicker">
            PARADIGM RA
          </p>

          <h1>
            Quote unavailable
          </h1>

          <p className="quote-client">
            {error ||
              "Unable to load this quote."}
          </p>
        </div>
      </main>
    );
  }


  return (
    <main className="quote-page">
      <header className="quote-header shell">
        <a
          className="brand"
          href="/"
          aria-label="Paradigm Ra home"
        >
          <img
            className="brand-logo"
            src="/work/RALogo.png"
            alt=""
            aria-hidden="true"
          />

          <span className="brand-name">
            PARADIGM RA
          </span>
        </a>

        <span className="quote-header-label">
          CLIENT QUOTE
        </span>
      </header>


      <section className="quote-shell shell">
        <div className="quote-heading">
          <div>
            <p className="kicker">
              {quote.quote_number}
            </p>

            <h1>
              Website Design
              <br />
              <span>
                &amp; Development
              </span>
            </h1>

            <p className="quote-client">
              Prepared for{" "}
              <strong>
                {quote.bill_to_name}
              </strong>
            </p>
          </div>


          <div className="quote-total-card">
            <span>
              PROJECT TOTAL
            </span>

            <strong>
              {money(
                quote.total,
              )}
            </strong>

            <div className="quote-status">
              {quote.status}
            </div>
          </div>
        </div>


        <div className="quote-meta">
          <div>
            <span>Issued</span>

            <strong>
              {dateLabel(
                quote.issue_date,
              )}
            </strong>
          </div>

          <div>
            <span>
              Valid through
            </span>

            <strong>
              {dateLabel(
                quote.expiration_date,
              )}
            </strong>
          </div>

          <div>
            <span>
              Project Deposit
            </span>

            <strong>
              {money(
                quote.line_items[0]
                  ?.amount ??
                  "0",
              )}
            </strong>
          </div>
        </div>


        {quote.notes ? (
          <section className="quote-section">
            <p className="kicker">
              PROJECTED WORK
            </p>

            <div className="quote-copy quote-scope-copy">
              {quote.notes}
            </div>
          </section>
        ) : null}


        <section className="quote-section">
          <p className="kicker">
            PAYMENT SCHEDULE
          </p>

          <div className="quote-lines">
            {quote.line_items.map(
              (
                line,
                index,
              ) => (
                <div
                  className="quote-line"
                  key={`${line.description}-${index}`}
                >
                  <div>
                    <strong>
                      {
                        line.description
                      }
                    </strong>
                  </div>

                  <span>
                    {money(
                      line.amount,
                    )}
                  </span>
                </div>
              ),
            )}
          </div>
        </section>


        {quote.terms ? (
          <section className="quote-section">
            <p className="kicker">
              TERMS &amp; DELIVERY
            </p>

            <div className="quote-copy">
              {quote.terms}
            </div>
          </section>
        ) : null}


        <section className="quote-summary">
          <div>
            <span>
              Subtotal
            </span>

            <strong>
              {money(
                quote.subtotal,
              )}
            </strong>
          </div>

          {Number(
            quote.tax_amount,
          ) > 0 ? (
            <div>
              <span>Tax</span>

              <strong>
                {money(
                  quote.tax_amount,
                )}
              </strong>
            </div>
          ) : null}

          <div className="quote-summary-total">
            <span>Total</span>

            <strong>
              {money(
                quote.total,
              )}
            </strong>
          </div>
        </section>


        <QuoteAcceptance
          token={token}
          initialStatus={
            quote.status
          }
          acceptedAt={
            quote.accepted_at
          }
        />


        <footer className="quote-footer">
          <span>
            PARADIGM RA
          </span>

          <span>
            SOFTWARE · SYSTEMS ·
            FINANCIAL CLARITY
          </span>
        </footer>
      </section>
    </main>
  );
}
