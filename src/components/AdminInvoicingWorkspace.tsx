"use client";

import {
  FormEvent,
  useEffect,
  useMemo,
  useState,
} from "react";


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


interface BillingTerms {
  id: string;
  engagement_id: string;
  billing_type: string;
  billing_cadence: string;
  hourly_rate: string | null;
  expected_hours_min: string | null;
  expected_hours_max: string | null;
  payment_terms_days: number;
  effective_from: string;
  effective_to: string | null;
}


interface TimeEntry {
  id: string;
  engagement_id: string;
  work_date: string;
  description: string;
  hours: string;
  status: string;
  invoice_id: string | null;
}


interface InvoiceLine {
  id: string;
  engagement_id: string;
  description: string;
  quantity: string;
  unit_rate: string;
  amount: string;
}


interface Invoice {
  id: string;
  invoice_number: string;
  status: string;
  issue_date: string | null;
  due_date: string | null;
  sent_at: string | null;
  bill_to_name: string;
  bill_to_email: string | null;
  subtotal: string;
  tax_amount: string;
  total: string;
  amount_paid: string;
  balance_due: string;
  line_items: InvoiceLine[];
}


async function readApiResponse<T>(
  response: Response,
  label: string,
): Promise<T> {
  const body =
    await response.text();

  if (!body.trim()) {
    throw new Error(
      `${label} returned an empty response (${response.status}).`
    );
  }

  let data;

  try {
    data = JSON.parse(body);

  } catch {
    throw new Error(
      `${label} returned a non-JSON response (${response.status}).`
    );
  }

  if (!response.ok) {
    throw new Error(
      data?.detail
      ?? `${label} failed (${response.status}).`
    );
  }

  return data as T;
}


function formatMoney(
  value: string | number,
) {
  return new Intl.NumberFormat(
    "en-US",
    {
      style: "currency",
      currency: "USD",
    },
  ).format(
    Number(value),
  );
}


function formatStatus(
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


export function AdminInvoicingWorkspace() {
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
    selectedEngagement,
    setSelectedEngagement,
  ] = useState<Engagement | null>(
    null,
  );

  const [
    billingTerms,
    setBillingTerms,
  ] = useState<BillingTerms[]>([]);

  const [
    timeEntries,
    setTimeEntries,
  ] = useState<TimeEntry[]>([]);

  const [
    invoices,
    setInvoices,
  ] = useState<Invoice[]>([]);

  const [workDate, setWorkDate] =
    useState(
      new Date()
        .toISOString()
        .slice(0, 10),
    );

  const [hours, setHours] =
    useState("");

  const [
    description,
    setDescription,
  ] = useState("");

  const [
    billToEmail,
    setBillToEmail,
  ] = useState("");

  const [loading, setLoading] =
    useState(true);

  const [
    actionLoading,
    setActionLoading,
  ] = useState(false);

  const [error, setError] =
    useState("");

  const [notice, setNotice] =
    useState("");


  useEffect(() => {
    async function loadOrganizations() {
      try {
        const response = await fetch(
          "/api/admin/organizations",
          {
            cache: "no-store",
          },
        );

        const data =
          await response.json();

        if (!response.ok) {
          throw new Error(
            data?.detail ??
              "Unable to load organizations.",
          );
        }

        setOrganizations(data);
        setError("");

      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Unable to load organizations.",
        );

      } finally {
        setLoading(false);
      }
    }

    loadOrganizations();
  }, []);


  const currentTerms =
    billingTerms[0] ?? null;

  const approvedEntries =
    useMemo(
      () =>
        timeEntries.filter(
          (entry) =>
            entry.status
              === "approved"
            && !entry.invoice_id,
        ),
      [timeEntries],
    );

  const approvedHours =
    useMemo(
      () =>
        approvedEntries.reduce(
          (total, entry) =>
            total
            + Number(
                entry.hours,
              ),
          0,
        ),
      [approvedEntries],
    );

  const approvedValue =
    approvedHours
    * Number(
      currentTerms
        ?.hourly_rate
      ?? 0,
    );


  async function loadEngagementBilling(
    engagement: Engagement,
  ) {
    const [
      termsResponse,
      timeResponse,
      invoiceResponse,
    ] = await Promise.all([
      fetch(
        `/api/admin/engagements/${engagement.id}/billing-terms`,
        {
          cache: "no-store",
        },
      ),

      fetch(
        `/api/admin/engagements/${engagement.id}/time-entries`,
        {
          cache: "no-store",
        },
      ),

      fetch(
        `/api/admin/engagements/${engagement.id}/invoices`,
        {
          cache: "no-store",
        },
      ),
    ]);

    const termsData =
      await readApiResponse<
        BillingTerms[]
      >(
        termsResponse,
        "Billing terms",
      );

    const timeData =
      await readApiResponse<
        TimeEntry[]
      >(
        timeResponse,
        "Time entries",
      );

    const invoiceData =
      await readApiResponse<
        Invoice[]
      >(
        invoiceResponse,
        "Invoices",
      );

    setBillingTerms(
      termsData,
    );

    setTimeEntries(
      timeData,
    );

    setInvoices(
      invoiceData,
    );
  }


  async function openOrganization(
    organization: Organization,
  ) {
    setSelectedOrganization(
      organization,
    );

    setSelectedEngagement(null);
    setBillingTerms([]);
    setTimeEntries([]);
    setInvoices([]);
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
          "Unable to load engagements.",
      );
      return;
    }

    setEngagements(data);
  }


  async function openEngagement(
    engagement: Engagement,
  ) {
    setSelectedEngagement(
      engagement,
    );

    setError("");
    setNotice("");

    try {
      await loadEngagementBilling(
        engagement,
      );

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to load billing.",
      );
    }
  }


  async function handleAddTime(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!selectedEngagement) {
      return;
    }

    setActionLoading(true);
    setError("");
    setNotice("");

    try {
      const response = await fetch(
        `/api/admin/engagements/${selectedEngagement.id}/time-entries`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            work_date:
              workDate,
            description,
            hours,
          }),
        },
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ??
            "Unable to add time.",
        );
      }

      setTimeEntries(
        (current) => [
          data,
          ...current,
        ],
      );

      setHours("");
      setDescription("");

      setNotice(
        "Time entry added as draft.",
      );

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to add time.",
      );

    } finally {
      setActionLoading(false);
    }
  }


  async function handleApprove(
    entry: TimeEntry,
  ) {
    setActionLoading(true);
    setError("");
    setNotice("");

    try {
      const response = await fetch(
        `/api/admin/time-entries/${entry.id}/approve`,
        {
          method: "POST",
        },
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ??
            "Unable to approve time.",
        );
      }

      setTimeEntries(
        (current) =>
          current.map(
            (item) =>
              item.id === data.id
                ? data
                : item,
          ),
      );

      setNotice(
        "Time entry approved.",
      );

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to approve time.",
      );

    } finally {
      setActionLoading(false);
    }
  }


  async function handleSendInvoice(
    invoice: Invoice,
  ) {
    if (
      invoice.status !== "draft"
    ) {
      return;
    }

    if (!invoice.bill_to_email) {
      setError(
        "A billing email is required before sending."
      );
      return;
    }

    setActionLoading(true);
    setError("");
    setNotice("");

    try {
      const response = await fetch(
        `/api/admin/invoices/${invoice.id}/send`,
        {
          method: "POST",
        },
      );

      const data =
        await readApiResponse<{
          invoice: Invoice;
          provider_message_id: string;
          pdf_sha256: string;
        }>(
          response,
          "Send invoice",
        );

      setInvoices(
        (current) =>
          current.map(
            (item) =>
              item.id === data.invoice.id
                ? data.invoice
                : item,
          ),
      );

      setNotice(
        `${data.invoice.invoice_number} sent to ${data.invoice.bill_to_email}.`,
      );

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to send invoice.",
      );

    } finally {
      setActionLoading(false);
    }
  }


  async function handleGenerateInvoice() {
    if (!selectedEngagement) {
      return;
    }

    setActionLoading(true);
    setError("");
    setNotice("");

    try {
      const response = await fetch(
        `/api/admin/engagements/${selectedEngagement.id}/invoices/generate`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            issue_date:
              new Date()
                .toISOString()
                .slice(0, 10),
            bill_to_email:
              billToEmail || null,
          }),
        },
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ??
            "Unable to generate invoice.",
        );
      }

      setInvoices(
        (current) => [
          data,
          ...current,
        ],
      );

      if (selectedEngagement) {
        await loadEngagementBilling(
          selectedEngagement,
        );
      }

      setNotice(
        `${data.invoice_number} generated.`,
      );

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to generate invoice.",
      );

    } finally {
      setActionLoading(false);
    }
  }


  if (loading) {
    return (
      <p className="admin-platform-empty">
        Loading organizations…
      </p>
    );
  }


  return (
    <div className="admin-invoice-layout">
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

      <section className="admin-platform-section">
        <p className="kicker">
          ORGANIZATIONS
        </p>

        <div className="admin-record-list">
          {organizations.map(
            (organization) => (
              <button
                key={organization.id}
                type="button"
                className={
                  selectedOrganization?.id
                  === organization.id
                    ? "admin-record-card is-active"
                    : "admin-record-card"
                }
                onClick={() =>
                  openOrganization(
                    organization,
                  )
                }
              >
                <span>
                  Client Organization
                </span>

                <strong>
                  {organization.name}
                </strong>

                <small>
                  {organization.status}
                </small>
              </button>
            ),
          )}
        </div>
      </section>

      {selectedOrganization ? (
        <section className="admin-platform-section">
          <p className="kicker">
            ENGAGEMENTS
          </p>

          <h3>
            {selectedOrganization.name}
          </h3>

          <div className="admin-record-list">
            {engagements.map(
              (engagement) => (
                <button
                  key={engagement.id}
                  type="button"
                  className={
                    selectedEngagement?.id
                    === engagement.id
                      ? "admin-record-card is-active"
                      : "admin-record-card"
                  }
                  onClick={() =>
                    openEngagement(
                      engagement,
                    )
                  }
                >
                  <span>
                    {
                      engagement.service_type
                    }
                  </span>

                  <strong>
                    {engagement.name}
                  </strong>

                  <small>
                    {engagement.status}
                    {" · "}
                    {engagement.source}
                  </small>
                </button>
              ),
            )}
          </div>
        </section>
      ) : null}

      {selectedEngagement ? (
        <>
          <section className="admin-platform-section">
            <p className="kicker">
              BILLING TERMS
            </p>

            <h3>
              {selectedEngagement.name}
            </h3>

            {currentTerms ? (
              <div className="admin-billing-grid">
                <div>
                  <span>Billing</span>
                  <strong>
                    {
                      currentTerms
                        .billing_type
                    }
                  </strong>
                </div>

                <div>
                  <span>Cadence</span>
                  <strong>
                    {
                      currentTerms
                        .billing_cadence
                    }
                  </strong>
                </div>

                <div>
                  <span>Rate</span>
                  <strong>
                    {currentTerms
                      .hourly_rate
                      ? `${formatMoney(
                          currentTerms
                            .hourly_rate,
                        )}/hr`
                      : "—"}
                  </strong>
                </div>

                <div>
                  <span>
                    Expected Hours
                  </span>

                  <strong>
                    {
                      currentTerms
                        .expected_hours_min
                    }
                    {" – "}
                    {
                      currentTerms
                        .expected_hours_max
                    }
                  </strong>
                </div>

                <div>
                  <span>
                    Payment Terms
                  </span>

                  <strong>
                    Net{" "}
                    {
                      currentTerms
                        .payment_terms_days
                    }
                  </strong>
                </div>

                <div>
                  <span>Effective</span>
                  <strong>
                    {
                      currentTerms
                        .effective_from
                    }
                  </strong>
                </div>
              </div>
            ) : (
              <p className="admin-platform-empty">
                No billing terms recorded.
              </p>
            )}
          </section>

          <section className="admin-platform-section admin-time-section">
            <div className="admin-section-heading">
              <div>
                <p className="kicker">
                  TIME
                </p>

                <h3>
                  Time entries
                </h3>
              </div>

              <div className="admin-billable-summary">
                <span>
                  Approved / Uninvoiced
                </span>

                <strong>
                  {approvedHours.toFixed(
                    2,
                  )}{" "}
                  hrs
                </strong>

                <small>
                  {formatMoney(
                    approvedValue,
                  )}
                </small>
              </div>
            </div>

            <form
              className="admin-time-form"
              onSubmit={
                handleAddTime
              }
            >
              <label>
                <span>
                  Work Date
                </span>

                <input
                  type="date"
                  required
                  value={workDate}
                  onChange={(event) =>
                    setWorkDate(
                      event.target.value,
                    )
                  }
                />
              </label>

              <label>
                <span>
                  Hours
                </span>

                <input
                  type="number"
                  step="0.25"
                  min="0.25"
                  required
                  value={hours}
                  onChange={(event) =>
                    setHours(
                      event.target.value,
                    )
                  }
                  placeholder="0.00"
                />
              </label>

              <label className="admin-time-description">
                <span>
                  Work Performed
                </span>

                <input
                  required
                  value={description}
                  onChange={(event) =>
                    setDescription(
                      event.target.value,
                    )
                  }
                  placeholder="Bank reconciliation, AP review…"
                />
              </label>

              <button
                type="submit"
                className="button button-primary"
                disabled={
                  actionLoading
                }
              >
                Add Time
              </button>
            </form>

            <div className="admin-time-list">
              {timeEntries.length ? (
                timeEntries.map(
                  (entry) => (
                    <article
                      key={entry.id}
                      className="admin-time-row"
                    >
                      <div>
                        <span>
                          {entry.work_date}
                        </span>

                        <strong>
                          {
                            entry.description
                          }
                        </strong>
                      </div>

                      <strong>
                        {Number(
                          entry.hours,
                        ).toFixed(2)}
                        {" "}hrs
                      </strong>

                      <span
                        className={
                          `admin-status-pill admin-status-${entry.status}`
                        }
                      >
                        {formatStatus(
                          entry.status,
                        )}
                      </span>

                      {entry.status
                        === "draft" ? (
                        <button
                          type="button"
                          className="admin-inline-action"
                          disabled={
                            actionLoading
                          }
                          onClick={() =>
                            handleApprove(
                              entry,
                            )
                          }
                        >
                          Approve
                        </button>
                      ) : (
                        <span />
                      )}
                    </article>
                  ),
                )
              ) : (
                <p className="admin-platform-empty">
                  No time entries yet.
                </p>
              )}
            </div>
          </section>

          <section className="admin-platform-section">
            <div className="admin-section-heading">
              <div>
                <p className="kicker">
                  INVOICING
                </p>

                <h3>
                  Generate invoice
                </h3>
              </div>

              <div className="admin-billable-summary">
                <span>
                  Ready to Bill
                </span>

                <strong>
                  {formatMoney(
                    approvedValue,
                  )}
                </strong>

                <small>
                  {approvedHours.toFixed(
                    2,
                  )}{" "}
                  approved hours
                </small>
              </div>
            </div>

            <div className="admin-generate-invoice">
              <label>
                <span>
                  Bill-To Email
                </span>

                <input
                  type="email"
                  value={
                    billToEmail
                  }
                  onChange={(event) =>
                    setBillToEmail(
                      event.target.value,
                    )
                  }
                  placeholder="accounting@client.com"
                />
              </label>

              <button
                type="button"
                className="button button-primary"
                disabled={
                  actionLoading
                  || approvedEntries
                    .length === 0
                }
                onClick={
                  handleGenerateInvoice
                }
              >
                Generate Invoice
              </button>
            </div>
          </section>

          <section className="admin-platform-section">
            <p className="kicker">
              INVOICE HISTORY
            </p>

            <h3>
              Invoices
            </h3>

            <div className="admin-invoice-list">
              {invoices.length ? (
                invoices.map(
                  (invoice) => (
                    <article
                      key={invoice.id}
                      className="admin-invoice-card"
                    >
                      <div className="admin-invoice-card-head">
                        <div>
                          <span>
                            {
                              invoice
                                .invoice_number
                            }
                          </span>

                          <strong>
                            {
                              invoice
                                .bill_to_name
                            }
                          </strong>
                        </div>

                        <span
                          className={
                            `admin-status-pill admin-status-${invoice.status}`
                          }
                        >
                          {formatStatus(
                            invoice.status,
                          )}
                        </span>
                      </div>

                      <div className="admin-invoice-metrics">
                        <div>
                          <span>
                            Total
                          </span>
                          <strong>
                            {formatMoney(
                              invoice.total,
                            )}
                          </strong>
                        </div>

                        <div>
                          <span>
                            Paid
                          </span>
                          <strong>
                            {formatMoney(
                              invoice
                                .amount_paid,
                            )}
                          </strong>
                        </div>

                        <div>
                          <span>
                            Balance
                          </span>
                          <strong>
                            {formatMoney(
                              invoice
                                .balance_due,
                            )}
                          </strong>
                        </div>

                        <div>
                          <span>
                            Due
                          </span>
                          <strong>
                            {invoice.due_date
                              ?? "—"}
                          </strong>
                        </div>
                      </div>

                      <div className="admin-invoice-lines">
                        {invoice.line_items.map(
                          (line) => (
                            <div
                              key={line.id}
                            >
                              <span>
                                {
                                  line.description
                                }
                              </span>

                              <strong>
                                {formatMoney(
                                  line.amount,
                                )}
                              </strong>
                            </div>
                          ),
                        )}
                      </div>

                      <div className="admin-invoice-actions">
                        <div>
                          {invoice.sent_at ? (
                            <small>
                              Sent{" "}
                              {new Date(
                                invoice.sent_at,
                              ).toLocaleString()}
                            </small>
                          ) : (
                            <small>
                              {invoice.bill_to_email
                                ? invoice.bill_to_email
                                : "Billing email required"}
                            </small>
                          )}
                        </div>

                        {invoice.status === "draft" ? (
                          <button
                            type="button"
                            className="button button-primary"
                            disabled={
                              actionLoading
                              || !invoice.bill_to_email
                            }
                            onClick={() =>
                              handleSendInvoice(
                                invoice,
                              )
                            }
                          >
                            {actionLoading
                              ? "Sending…"
                              : "Send Invoice"}
                          </button>
                        ) : null}
                      </div>
                    </article>
                  ),
                )
              ) : (
                <p className="admin-platform-empty">
                  No invoices generated.
                </p>
              )}
            </div>
          </section>
        </>
      ) : null}
    </div>
  );
}
