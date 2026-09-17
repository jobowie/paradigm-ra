import { notFound } from "next/navigation";

import { QuoteAcceptance } from "@/components/QuoteAcceptance";

const PLATFORM_API =
  process.env.RA_PLATFORM_API_URL ??
  "http://127.0.0.1:8000";

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
    new Date(`${value}T00:00:00Z`),
  );
}

export default async function QuotePage({
  params,
}: {
  params: Promise<{
    token: string;
  }>;
}) {
  const { token } = await params;

  const response = await fetch(
    `${PLATFORM_API}/quotes/public/${encodeURIComponent(
      token,
    )}`,
    {
      cache: "no-store",
    },
  );

  if (response.status === 404) {
    notFound();
  }

  if (!response.ok) {
    throw new Error(
      "Unable to load quote.",
    );
  }

  const quote =
    (await response.json()) as PublicQuote;

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
              <span>&amp; Development</span>
            </h1>

            <p className="quote-client">
              Prepared for{" "}
              <strong>
                {quote.bill_to_name}
              </strong>
            </p>
          </div>

          <div className="quote-total-card">
            <span>PROJECT TOTAL</span>
            <strong>
              {money(quote.total)}
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
            <span>Valid through</span>
            <strong>
              {dateLabel(
                quote.expiration_date,
              )}
            </strong>
          </div>

          <div>
            <span>Deposit</span>
            <strong>
              {money(
                (
                  Number(
                    quote.total,
                  ) / 2
                ).toFixed(2),
              )}
            </strong>
          </div>
        </div>

        <section className="quote-section">
          <p className="kicker">
            PAYMENT SCHEDULE
          </p>

          <div className="quote-lines">
            {quote.line_items.map(
              (line, index) => (
                <div
                  className="quote-line"
                  key={`${line.description}-${index}`}
                >
                  <div>
                    <strong>
                      {line.description}
                    </strong>
                  </div>

                  <span>
                    {money(line.amount)}
                  </span>
                </div>
              ),
            )}
          </div>
        </section>

        {quote.notes ? (
          <section className="quote-section">
            <p className="kicker">
              SCOPE
            </p>

            <div className="quote-copy quote-scope-copy">
              {quote.notes}
            </div>
          </section>
        ) : null}

        {quote.terms ? (
          <section className="quote-section">
            <p className="kicker">
              TERMS
            </p>

            <div className="quote-copy">
              {quote.terms}
            </div>
          </section>
        ) : null}

        <section className="quote-summary">
          <div>
            <span>Subtotal</span>
            <strong>
              {money(quote.subtotal)}
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
              {money(quote.total)}
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
