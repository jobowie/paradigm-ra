"use client";

import {
  FormEvent,
  useCallback,
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
  workstream: string | null;
  friction: string | null;
  operational_note: string | null;
  status: string;
  invoice_id: string | null;
}


const WORKSTREAM_OPTIONS = [
  ["accounts_payable", "Accounts Payable"],
  ["accounts_receivable", "Accounts Receivable"],
  ["reconciliation", "Reconciliation"],
  ["expenses", "Expenses"],
  ["reporting", "Reporting"],
  ["payroll", "Payroll"],
  ["bookkeeping", "Bookkeeping"],
  ["other", "Other"],
] as const;


const FRICTION_OPTIONS = [
  ["none_observed", "None observed"],
  ["manual_entry", "Manual entry"],
  ["missing_information", "Missing information"],
  ["duplicate_work", "Duplicate work"],
  ["approval_delay", "Approval delay"],
  ["system_issue", "System issue"],
  ["follow_up_required", "Follow-up required"],
  ["other", "Other"],
] as const;


interface EditableBillingTermsDraft {
  billing_type: string;
  billing_cadence: string;
  hourly_rate: string;
  expected_hours_min: string;
  expected_hours_max: string;
  payment_terms_days: string;
  effective_from: string;
}


interface EditableTimeDraft {
  work_date: string;
  hours: string;
  description: string;
  workstream: string;
  friction: string;
  operational_note: string;
}


type TimeDraftSaveState =
  | "idle"
  | "saving"
  | "saved"
  | "error";


function timeDraftFingerprint(
  draft: EditableTimeDraft,
) {
  return JSON.stringify({
    work_date: draft.work_date,
    hours: draft.hours,
    description:
      draft.description.trim(),
    workstream:
      draft.workstream || null,
    friction:
      draft.friction || null,
    operational_note:
      draft.operational_note.trim()
      || null,
  });
}


function validTimeDraft(
  draft: EditableTimeDraft,
) {
  return Boolean(
    draft.work_date
    && draft.description.trim()
    && Number(draft.hours) > 0
  );
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
  bill_to_address: string | null;

  notes: string | null;
  terms: string | null;

  subtotal: string;
  tax_amount: string;
  total: string;
  amount_paid: string;
  balance_due: string;
  line_items: InvoiceLine[];
}



interface EditableInvoiceDraft {
  issue_date: string;
  due_date: string;
  bill_to_name: string;
  bill_to_email: string;
  bill_to_address: string;
  notes: string;
  terms: string;
}


type InvoiceFlowStep =
  | "edit"
  | "review"
  | "confirm"
  | "delete"
  | null;


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


function addDaysToIso(
  value: string,
  days: number,
) {
  const date = new Date(
    `${value}T00:00:00Z`,
  );

  date.setUTCDate(
    date.getUTCDate() + days,
  );

  return date
    .toISOString()
    .slice(0, 10);
}


function localIsoDate(
  date = new Date(),
) {
  const year =
    date.getFullYear();

  const month =
    String(
      date.getMonth() + 1
    ).padStart(
      2,
      "0",
    );

  const day =
    String(
      date.getDate()
    ).padStart(
      2,
      "0",
    );

  return `${year}-${month}-${day}`;
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


function billingTermsForDate(
  terms: BillingTerms[],
  workDate: string,
): BillingTerms | null {
  return (
    [...terms]
      .filter(
        (item) =>
          item.effective_from
            <= workDate
          && (
            !item.effective_to
            || workDate
              <= item.effective_to
          ),
      )
      .sort(
        (left, right) =>
          right.effective_from
            .localeCompare(
              left.effective_from,
            ),
      )[0]
    ?? null
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
    editingBillingTerms,
    setEditingBillingTerms,
  ] = useState(false);

  const [
    billingTermsDraft,
    setBillingTermsDraft,
  ] = useState<
    EditableBillingTermsDraft
  >({
    billing_type: "hourly",
    billing_cadence: "weekly",
    hourly_rate: "0",
    expected_hours_min: "",
    expected_hours_max: "",
    payment_terms_days: "30",
    effective_from:
      localIsoDate(),
  });



  const [
    invoices,
    setInvoices,
  ] = useState<Invoice[]>([]);

  const [
    activeInvoice,
    setActiveInvoice,
  ] = useState<Invoice | null>(
    null,
  );

  const [
    invoiceFlowStep,
    setInvoiceFlowStep,
  ] = useState<InvoiceFlowStep>(
    null,
  );

  const [
    invoiceDraft,
    setInvoiceDraft,
  ] = useState<EditableInvoiceDraft | null>(
    null,
  );

  const [
    invoiceDraftSaving,
    setInvoiceDraftSaving,
  ] = useState(false);

  const [workDate, setWorkDate] =
    useState(
      localIsoDate(),
    );

  const [hours, setHours] =
    useState("");

  const [
    description,
    setDescription,
  ] = useState("");

  const [
    workstream,
    setWorkstream,
  ] = useState("");

  const [
    friction,
    setFriction,
  ] = useState("");

  const [
    operationalNote,
    setOperationalNote,
  ] = useState("");

  const [
    editingTimeEntryId,
    setEditingTimeEntryId,
  ] = useState<string | null>(
    null,
  );

  const [
    timeDraft,
    setTimeDraft,
  ] = useState<
    EditableTimeDraft | null
  >(null);

  const [
    timeDraftSaveState,
    setTimeDraftSaveState,
  ] = useState<TimeDraftSaveState>(
    "idle",
  );

  const [
    lastSavedTimeDraftFingerprint,
    setLastSavedTimeDraftFingerprint,
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


  const saveEditedTimeDraft =
    useCallback(
      async (
        entryId: string,
        draft: EditableTimeDraft,
      ): Promise<
        TimeEntry | null
      > => {
        const fingerprint =
          timeDraftFingerprint(
            draft,
          );

        setTimeDraftSaveState(
          "saving",
        );

        try {
          const response =
            await fetch(
              `/api/admin/time-entries/${entryId}`,
              {
                method: "PUT",
                headers: {
                  "Content-Type":
                    "application/json",
                },
                body: JSON.stringify({
                  work_date:
                    draft.work_date,
                  description:
                    draft.description
                      .trim(),
                  hours:
                    draft.hours,
                  workstream:
                    draft.workstream
                    || null,
                  friction:
                    draft.friction
                    || null,
                  operational_note:
                    draft
                      .operational_note
                      .trim()
                    || null,
                }),
              },
            );

          const data =
            await readApiResponse<
              TimeEntry
            >(
              response,
              "Save time draft",
            );

          setTimeEntries(
            (current) =>
              current.map(
                (item) =>
                  item.id
                  === data.id
                    ? data
                    : item,
              ),
          );

          setLastSavedTimeDraftFingerprint(
            fingerprint,
          );

          setTimeDraftSaveState(
            "saved",
          );

          setError("");

          return data;

        } catch (err) {
          setTimeDraftSaveState(
            "error",
          );

          setError(
            err instanceof Error
              ? err.message
              : "Unable to save time draft.",
          );

          return null;
        }
      },
      [],
    );


  useEffect(() => {
    if (
      !editingTimeEntryId
      || !timeDraft
    ) {
      return;
    }

    if (
      !validTimeDraft(
        timeDraft,
      )
    ) {
      setTimeDraftSaveState(
        "idle",
      );

      return;
    }

    const fingerprint =
      timeDraftFingerprint(
        timeDraft,
      );

    if (
      fingerprint
      === lastSavedTimeDraftFingerprint
    ) {
      setTimeDraftSaveState(
        "saved",
      );

      return;
    }

    setTimeDraftSaveState(
      "idle",
    );

    const timeout =
      window.setTimeout(
        () => {
          void saveEditedTimeDraft(
            editingTimeEntryId,
            timeDraft,
          );
        },
        800,
      );

    return () => {
      window.clearTimeout(
        timeout,
      );
    };
  }, [
    editingTimeEntryId,
    timeDraft,
    lastSavedTimeDraftFingerprint,
    saveEditedTimeDraft,
  ]);


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



const [
  selectedInvoiceEntryIds,
  setSelectedInvoiceEntryIds,
] = useState<string[]>([]);


const currentTerms =
    useMemo(
      () =>
        billingTermsForDate(
          billingTerms,
          localIsoDate(),
        ),
      [billingTerms],
    );


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


  const billableEntries =
    useMemo(
      () =>
        approvedEntries.flatMap(
          (entry) => {
            const terms =
              billingTermsForDate(
                billingTerms,
                entry.work_date,
              );

            if (
              !terms
              || terms.billing_type
                !== "hourly"
              || !terms.hourly_rate
              || Number(
                terms.hourly_rate,
              ) <= 0
            ) {
              return [];
            }

            return [
              {
                entry,
                terms,
              },
            ];
          },
        ),
      [
        approvedEntries,
        billingTerms,
      ],
    );



const selectedInvoiceEntries =
  useMemo(
    () =>
      approvedEntries.filter(
        (entry) =>
          selectedInvoiceEntryIds
            .includes(
              entry.id
            ),
      ),
    [
      approvedEntries,
      selectedInvoiceEntryIds,
    ],
  );


const selectedInvoiceHours =
  useMemo(
    () =>
      selectedInvoiceEntries.reduce(
        (total, entry) =>
          total
          + Number(
              entry.hours
            ),
        0,
      ),
    [selectedInvoiceEntries],
  );


const selectedInvoiceValue =
  useMemo(
    () =>
      selectedInvoiceEntries.reduce(
        (total, entry) => {
          const terms =
            billingTermsForDate(
              billingTerms,
              entry.work_date,
            );

          if (
            !terms
            || terms.billing_type
              !== "hourly"
            || !terms.hourly_rate
          ) {
            return total;
          }

          return (
            total
            + Number(entry.hours)
            * Number(
                terms.hourly_rate
              )
          );
        },
        0,
      ),
    [
      selectedInvoiceEntries,
      billingTerms,
    ],
  );


function toggleInvoiceEntry(
  entryId: string,
) {
  setSelectedInvoiceEntryIds(
    (current) =>
      current.includes(
        entryId
      )
        ? current.filter(
            (id) =>
              id !== entryId
          )
        : [
            ...current,
            entryId,
          ],
  );
}


function selectAllBillableEntries() {
  setSelectedInvoiceEntryIds(
    billableEntries.map(
      (item) =>
        item.entry.id
    ),
  );
}


const billingMismatchEntries =
    useMemo(
      () =>
        approvedEntries.filter(
          (entry) => {
            const terms =
              billingTermsForDate(
                billingTerms,
                entry.work_date,
              );

            return (
              !terms
              || terms.billing_type
                !== "hourly"
              || !terms.hourly_rate
              || Number(
                terms.hourly_rate,
              ) <= 0
            );
          },
        ),
      [
        approvedEntries,
        billingTerms,
      ],
    );


  const approvedHours =
    useMemo(
      () =>
        billableEntries.reduce(
          (total, item) =>
            total
            + Number(
                item.entry.hours,
              ),
          0,
        ),
      [billableEntries],
    );


  const approvedValue =
    useMemo(
      () =>
        billableEntries.reduce(
          (total, item) =>
            total
            + (
              Number(
                item.entry.hours,
              )
              * Number(
                  item.terms
                    .hourly_rate
                  ?? 0,
                )
            ),
          0,
        ),
      [billableEntries],
    );


  const billingMismatchHours =
    useMemo(
      () =>
        billingMismatchEntries.reduce(
          (total, entry) =>
            total
            + Number(
                entry.hours,
              ),
          0,
        ),
      [billingMismatchEntries],
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

    setSelectedInvoiceEntryIds(
      [],
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


  function beginBillingTermsEdit() {
    const today =
      localIsoDate();

    const effectiveFrom =
      currentTerms
        ? [
            today,
            addDaysToIso(
              currentTerms
                .effective_from,
              1,
            ),
          ].sort().at(-1)!
        : today;

    setBillingTermsDraft({
      billing_type:
        currentTerms
          ?.billing_type
        ?? "hourly",

      billing_cadence:
        currentTerms
          ?.billing_cadence
        ?? "weekly",

      hourly_rate:
        currentTerms
          ?.hourly_rate
        ?? "0",

      expected_hours_min:
        currentTerms
          ?.expected_hours_min
        ?? "",

      expected_hours_max:
        currentTerms
          ?.expected_hours_max
        ?? "",

      payment_terms_days:
        String(
          currentTerms
            ?.payment_terms_days
          ?? 30,
        ),

      effective_from:
        effectiveFrom,
    });

    setEditingBillingTerms(
      true,
    );

    setError("");
    setNotice("");
  }


  function updateBillingTermsDraft(
    field:
      keyof EditableBillingTermsDraft,
    value: string,
  ) {
    setBillingTermsDraft(
      (current) => ({
        ...current,
        [field]: value,
      }),
    );
  }


  async function handleSaveBillingTerms(
    event:
      FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!selectedEngagement) {
      return;
    }

    if (
      billingTermsDraft.billing_type
      === "hourly"
      && (
        !billingTermsDraft.hourly_rate
        || Number(
          billingTermsDraft.hourly_rate
        ) <= 0
      )
    ) {
      setError(
        "Hourly billing requires a positive hourly rate."
      );

      return;
    }

    if (
      billingTermsDraft.expected_hours_min
      && billingTermsDraft.expected_hours_max
      && Number(
        billingTermsDraft.expected_hours_max
      ) < Number(
        billingTermsDraft.expected_hours_min
      )
    ) {
      setError(
        "Expected maximum hours cannot be below minimum hours."
      );

      return;
    }

    setActionLoading(true);
    setError("");
    setNotice("");

    try {
      const response =
        await fetch(
          `/api/admin/engagements/${selectedEngagement.id}/billing-terms`,
          {
            method: "POST",
            headers: {
              "Content-Type":
                "application/json",
            },
            body: JSON.stringify({
              billing_type:
                billingTermsDraft
                  .billing_type,

              billing_cadence:
                billingTermsDraft
                  .billing_cadence,

              hourly_rate:
                billingTermsDraft
                  .hourly_rate
                || null,

              expected_hours_min:
                billingTermsDraft
                  .expected_hours_min
                || null,

              expected_hours_max:
                billingTermsDraft
                  .expected_hours_max
                || null,

              payment_terms_days:
                Number(
                  billingTermsDraft
                    .payment_terms_days,
                ),

              effective_from:
                billingTermsDraft
                  .effective_from,
            }),
          },
        );

      await readApiResponse<
        BillingTerms
      >(
        response,
        "Save billing terms",
      );

      await loadEngagementBilling(
        selectedEngagement,
      );

      setEditingBillingTerms(
        false,
      );

      setNotice(
        currentTerms
          ? "New billing terms are now effective."
          : "Billing terms added.",
      );

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to save billing terms.",
      );

    } finally {
      setActionLoading(false);
    }
  }


  async function handleEditTime(
    entry: TimeEntry,
  ) {
    if (
      entry.status === "invoiced"
    ) {
      return;
    }

    let editableEntry = entry;

    if (
      entry.status === "approved"
    ) {
      setActionLoading(true);
      setError("");
      setNotice("");

      try {
        const response =
          await fetch(
            `/api/admin/time-entries/${entry.id}/reopen`,
            {
              method: "POST",
            },
          );

        editableEntry =
          await readApiResponse<
            TimeEntry
          >(
            response,
            "Reopen time entry",
          );

        setTimeEntries(
          (current) =>
            current.map(
              (item) =>
                item.id
                === editableEntry.id
                  ? editableEntry
                  : item,
            ),
        );

        setNotice(
          "Approved time entry reopened as draft."
        );

      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Unable to reopen time entry.",
        );

        return;

      } finally {
        setActionLoading(false);
      }
    }

    if (
      editableEntry.status
      !== "draft"
    ) {
      return;
    }

    const draft: EditableTimeDraft = {
      work_date:
        editableEntry.work_date,
      hours:
        editableEntry.hours,
      description:
        editableEntry.description,
      workstream:
        editableEntry.workstream
        ?? "",
      friction:
        editableEntry.friction
        ?? "",
      operational_note:
        editableEntry.operational_note
        ?? "",
    };

    setEditingTimeEntryId(
      editableEntry.id,
    );

    setTimeDraft(
      draft,
    );

    setLastSavedTimeDraftFingerprint(
      timeDraftFingerprint(
        draft,
      ),
    );

    setTimeDraftSaveState(
      "saved",
    );

    setError("");
  }


  function updateTimeDraft(
    field: keyof EditableTimeDraft,
    value: string,
  ) {
    setTimeDraft(
      (current) =>
        current
          ? {
              ...current,
              [field]: value,
            }
          : current,
    );
  }


  async function handleRetryTimeDraft() {
    if (
      !editingTimeEntryId
      || !timeDraft
      || !validTimeDraft(
        timeDraft,
      )
    ) {
      return;
    }

    await saveEditedTimeDraft(
      editingTimeEntryId,
      timeDraft,
    );
  }


  async function handleDoneTimeEdit() {
    if (
      !editingTimeEntryId
      || !timeDraft
    ) {
      return;
    }

    if (
      !validTimeDraft(
        timeDraft,
      )
    ) {
      setError(
        "Work date, hours, and work performed are required."
      );

      return;
    }

    const fingerprint =
      timeDraftFingerprint(
        timeDraft,
      );

    if (
      fingerprint
      !== lastSavedTimeDraftFingerprint
    ) {
      const saved =
        await saveEditedTimeDraft(
          editingTimeEntryId,
          timeDraft,
        );

      if (!saved) {
        return;
      }
    }

    setEditingTimeEntryId(
      null,
    );

    setTimeDraft(null);

    setTimeDraftSaveState(
      "idle",
    );

    setLastSavedTimeDraftFingerprint(
      "",
    );

    setError("");
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
            workstream:
              workstream || null,
            friction:
              friction || null,
            operational_note:
              operationalNote.trim()
              || null,
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
      setWorkstream("");
      setFriction("");
      setOperationalNote("");

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



  function buildInvoiceDraft(
    invoice: Invoice,
  ): EditableInvoiceDraft {
    return {
      issue_date:
        invoice.issue_date
        ?? localIsoDate(),
      due_date:
        invoice.due_date
        ?? invoice.issue_date
        ?? localIsoDate(),
      bill_to_name:
        invoice.bill_to_name,
      bill_to_email:
        invoice.bill_to_email
        ?? "",
      bill_to_address:
        invoice.bill_to_address
        ?? "",
      notes:
        invoice.notes
        ?? "",
      terms:
        invoice.terms
        ?? "",
    };
  }


  function beginInvoiceEdit(
    invoice: Invoice,
  ) {
    if (invoice.status !== "draft") {
      return;
    }

    setActiveInvoice(
      invoice
    );

    setInvoiceDraft(
      buildInvoiceDraft(
        invoice
      )
    );

    setInvoiceFlowStep(
      "edit"
    );

    setError("");
  }


  function beginInvoiceReview(
    invoice: Invoice,
  ) {
    if (invoice.status !== "draft") {
      return;
    }

    setActiveInvoice(
      invoice
    );

    setInvoiceDraft(
      buildInvoiceDraft(
        invoice
      )
    );

    setInvoiceFlowStep(
      "review"
    );

    setError("");
  }


  function closeInvoiceFlow() {
    if (
      actionLoading
      || invoiceDraftSaving
    ) {
      return;
    }

    setInvoiceFlowStep(
      null
    );

    setActiveInvoice(
      null
    );

    setInvoiceDraft(
      null
    );
  }


  function updateInvoiceDraft(
    field: keyof EditableInvoiceDraft,
    value: string,
  ) {
    setInvoiceDraft(
      (current) =>
        current
          ? {
              ...current,
              [field]: value,
            }
          : current
    );
  }


  async function saveInvoiceDraft(
    nextStep: InvoiceFlowStep = "review",
  ) {
    if (
      !activeInvoice
      || !invoiceDraft
      || activeInvoice.status !== "draft"
    ) {
      return;
    }

    if (
      !invoiceDraft.bill_to_name.trim()
      || !invoiceDraft.bill_to_email.trim()
      || !invoiceDraft.issue_date
      || !invoiceDraft.due_date
    ) {
      setError(
        "Bill To, billing email, issue date, and due date are required."
      );
      return;
    }

    setInvoiceDraftSaving(true);
    setError("");
    setNotice("");

    try {
      const response = await fetch(
        `/api/admin/invoices/${activeInvoice.id}`,
        {
          method: "PUT",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            issue_date:
              invoiceDraft.issue_date,
            due_date:
              invoiceDraft.due_date,
            bill_to_name:
              invoiceDraft
                .bill_to_name
                .trim(),
            bill_to_email:
              invoiceDraft
                .bill_to_email
                .trim(),
            bill_to_address:
              invoiceDraft
                .bill_to_address
                .trim()
              || null,
            notes:
              invoiceDraft
                .notes
                .trim()
              || null,
            terms:
              invoiceDraft
                .terms
                .trim()
              || null,
          }),
        },
      );

      const updated =
        await readApiResponse<Invoice>(
          response,
          "Update invoice",
        );

      setInvoices(
        (current) =>
          current.map(
            (item) =>
              item.id === updated.id
                ? updated
                : item,
          ),
      );

      setActiveInvoice(
        updated
      );

      setInvoiceDraft(
        buildInvoiceDraft(
          updated
        )
      );

      setInvoiceFlowStep(
        nextStep
      );

      setNotice(
        `${updated.invoice_number} draft saved.`
      );

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to update invoice.",
      );

    } finally {
      setInvoiceDraftSaving(false);
    }
  }


  async function handleDeleteInvoiceDraft() {
    if (
      !activeInvoice
      || activeInvoice.status !== "draft"
    ) {
      return;
    }

    setActionLoading(true);
    setError("");
    setNotice("");

    try {
      const response = await fetch(
        `/api/admin/invoices/${activeInvoice.id}`,
        {
          method: "DELETE",
        },
      );

      const data =
        await readApiResponse<{
          invoice_number: string;
          released_time_entries: number;
        }>(
          response,
          "Delete invoice draft",
        );

      const deletedInvoiceId =
        activeInvoice.id;

      setInvoices(
        (current) =>
          current.filter(
            (invoice) =>
              invoice.id
              !== deletedInvoiceId,
          ),
      );

      setTimeEntries(
        (current) =>
          current.map(
            (entry) =>
              entry.invoice_id
              === deletedInvoiceId
                ? {
                    ...entry,
                    status: "approved",
                    invoice_id: null,
                  }
                : entry,
          ),
      );

      setInvoiceFlowStep(null);
      setActiveInvoice(null);
      setInvoiceDraft(null);

      setNotice(
        `${data.invoice_number} draft deleted. `
        + `${data.released_time_entries} `
        + (
          data.released_time_entries === 1
            ? "source entry returned"
            : "source entries returned"
        )
        + " to Ready to Bill."
      );

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to delete invoice draft.",
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

      setInvoiceFlowStep(
        null
      );

      setActiveInvoice(
        null
      );

      setInvoiceDraft(
        null
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

    if (
      selectedInvoiceEntryIds.length
      === 0
    ) {
      setError(
        "Select at least one Ready to Bill entry."
      );
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
              localIsoDate(),
            time_entry_ids:
              selectedInvoiceEntryIds,
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
          <section className="admin-platform-section admin-billing-terms-section">
            <div className="admin-section-heading">
              <div>
                <p className="kicker">
                  BILLING TERMS
                </p>

                <h3>
                  {selectedEngagement.name}
                </h3>
              </div>

              {!editingBillingTerms ? (
                <button
                  type="button"
                  className="admin-org-edit-button"
                  onClick={
                    beginBillingTermsEdit
                  }
                >
                  {currentTerms
                    ? "Update Terms"
                    : "+ Add Billing Terms"}
                </button>
              ) : null}
            </div>

            {editingBillingTerms ? (
              <form
                className="admin-billing-terms-form"
                onSubmit={
                  handleSaveBillingTerms
                }
              >
                <label>
                  <span>
                    Billing Type
                  </span>

                  <select
                    value={
                      billingTermsDraft
                        .billing_type
                    }
                    onChange={(event) =>
                      updateBillingTermsDraft(
                        "billing_type",
                        event.target.value,
                      )
                    }
                  >
                    <option value="hourly">
                      Hourly
                    </option>

                    <option value="fixed">
                      Fixed
                    </option>

                    <option value="retainer">
                      Retainer
                    </option>
                  </select>
                </label>

                <label>
                  <span>
                    Cadence
                  </span>

                  <select
                    value={
                      billingTermsDraft
                        .billing_cadence
                    }
                    onChange={(event) =>
                      updateBillingTermsDraft(
                        "billing_cadence",
                        event.target.value,
                      )
                    }
                  >
                    <option value="weekly">
                      Weekly
                    </option>

                    <option value="biweekly">
                      Biweekly
                    </option>

                    <option value="monthly">
                      Monthly
                    </option>

                    <option value="milestone">
                      Milestone
                    </option>
                  </select>
                </label>

                <label>
                  <span>
                    Hourly Rate
                  </span>

                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={
                      billingTermsDraft
                        .hourly_rate
                    }
                    onChange={(event) =>
                      updateBillingTermsDraft(
                        "hourly_rate",
                        event.target.value,
                      )
                    }
                    placeholder="0.00"
                  />
                </label>

                <label>
                  <span>
                    Payment Terms
                  </span>

                  <select
                    value={
                      billingTermsDraft
                        .payment_terms_days
                    }
                    onChange={(event) =>
                      updateBillingTermsDraft(
                        "payment_terms_days",
                        event.target.value,
                      )
                    }
                  >
                    <option value="0">
                      Due on receipt
                    </option>

                    <option value="7">
                      Net 7
                    </option>

                    <option value="15">
                      Net 15
                    </option>

                    <option value="30">
                      Net 30
                    </option>

                    <option value="45">
                      Net 45
                    </option>

                    <option value="60">
                      Net 60
                    </option>
                  </select>
                </label>

                <label>
                  <span>
                    Expected Hours Min
                  </span>

                  <input
                    type="number"
                    step="0.25"
                    min="0"
                    value={
                      billingTermsDraft
                        .expected_hours_min
                    }
                    onChange={(event) =>
                      updateBillingTermsDraft(
                        "expected_hours_min",
                        event.target.value,
                      )
                    }
                    placeholder="Enter minimum hours"
                  />
                </label>

                <label>
                  <span>
                    Expected Hours Max
                  </span>

                  <input
                    type="number"
                    step="0.25"
                    min="0"
                    value={
                      billingTermsDraft
                        .expected_hours_max
                    }
                    onChange={(event) =>
                      updateBillingTermsDraft(
                        "expected_hours_max",
                        event.target.value,
                      )
                    }
                    placeholder="Enter maximum hours"
                  />
                </label>

                <label>
                  <span>
                    Effective From
                  </span>

                  <input
                    type="date"
                    required
                    value={
                      billingTermsDraft
                        .effective_from
                    }
                    onChange={(event) =>
                      updateBillingTermsDraft(
                        "effective_from",
                        event.target.value,
                      )
                    }
                  />
                </label>

                <div className="admin-billing-terms-actions">
                  <button
                    type="button"
                    className="admin-cancel-button"
                    disabled={
                      actionLoading
                    }
                    onClick={() =>
                      setEditingBillingTerms(
                        false,
                      )
                    }
                  >
                    Cancel
                  </button>

                  <button
                    type="submit"
                    className="button button-primary"
                    disabled={
                      actionLoading
                    }
                  >
                    {actionLoading
                      ? "Saving…"
                      : "Save Billing Terms"}
                  </button>
                </div>
              </form>
            ) : currentTerms ? (
              <>
                <div className="admin-billing-grid">
                  <div>
                    <span>Billing</span>
                    <strong>
                      {formatStatus(
                        currentTerms
                          .billing_type,
                      )}
                    </strong>
                  </div>

                  <div>
                    <span>Cadence</span>
                    <strong>
                      {formatStatus(
                        currentTerms
                          .billing_cadence,
                      )}
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
                      {currentTerms
                        .expected_hours_min
                        ?? "—"}
                      {" – "}
                      {currentTerms
                        .expected_hours_max
                        ?? "—"}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Payment Terms
                    </span>

                    <strong>
                      {currentTerms
                        .payment_terms_days
                      === 0
                        ? "Due on receipt"
                        : `Net ${currentTerms.payment_terms_days}`}
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

                {billingTerms.length > 1 ? (
                  <p className="admin-billing-terms-history">
                    {billingTerms.length - 1}
                    {" "}
                    prior billing terms
                    {billingTerms.length - 1 === 1
                      ? " version"
                      : " versions"}
                    {" "}preserved.
                  </p>
                ) : null}
              </>
            ) : (
              <div className="admin-billing-terms-empty">
                <p className="admin-platform-empty">
                  No billing terms recorded.
                </p>

                <small>
                  Add billing terms before
                  generating an invoice.
                </small>
              </div>
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
                  Ready to Bill
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

                {billingMismatchEntries
                  .length > 0 ? (
                  <small className="admin-billing-mismatch">
                    {billingMismatchHours.toFixed(
                      2,
                    )}
                    {" "}
                    hrs require billing terms
                  </small>
                ) : null}
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

              <label>
                <span>
                  Workstream
                </span>

                <select
                  value={workstream}
                  onChange={(event) =>
                    setWorkstream(
                      event.target.value,
                    )
                  }
                >
                  <option value="">
                    Not classified
                  </option>

                  {WORKSTREAM_OPTIONS.map(
                    ([value, label]) => (
                      <option
                        key={value}
                        value={value}
                      >
                        {label}
                      </option>
                    ),
                  )}
                </select>
              </label>

              <label>
                <span>
                  Friction
                </span>

                <select
                  value={friction}
                  onChange={(event) =>
                    setFriction(
                      event.target.value,
                    )
                  }
                >
                  <option value="">
                    Not recorded
                  </option>

                  {FRICTION_OPTIONS.map(
                    ([value, label]) => (
                      <option
                        key={value}
                        value={value}
                      >
                        {label}
                      </option>
                    ),
                  )}
                </select>
              </label>

              <label className="admin-time-description">
                <span>
                  Operational Note
                </span>

                <input
                  value={operationalNote}
                  onChange={(event) =>
                    setOperationalNote(
                      event.target.value,
                    )
                  }
                  placeholder="Optional context about delay, rework, handoff, or system friction…"
                />
              </label>

              <button
                type="submit"
                className="button button-primary"
                disabled={
                  actionLoading
                }
              >
                Save Draft
              </button>
            </form>

            <div className="admin-time-list">
              {timeEntries.length ? (
                timeEntries.map(
                  (entry) => (
                    <article
                      key={entry.id}
                      className={
                        editingTimeEntryId
                        === entry.id
                          ? "admin-time-row is-editing"
                          : "admin-time-row"
                      }
                    >
                      {(
                        editingTimeEntryId
                        === entry.id
                        && timeDraft
                      ) ? (
                        <div className="admin-time-edit-panel">
                          <div className="admin-time-edit-heading">
                            <div>
                              <span>
                                Editing Draft
                              </span>

                              <strong>
                                {
                                  entry.description
                                }
                              </strong>
                            </div>

                            <span
                              className={
                                `admin-time-save-state is-${timeDraftSaveState}`
                              }
                            >
                              {
                                !validTimeDraft(
                                  timeDraft,
                                )
                                  ? "Complete required fields"
                                  : timeDraftSaveState
                                    === "saving"
                                    ? "Saving…"
                                    : timeDraftSaveState
                                      === "saved"
                                      ? "Saved ✓"
                                      : timeDraftSaveState
                                        === "error"
                                        ? "Save failed"
                                        : "Unsaved changes"
                              }
                            </span>
                          </div>

                          <div className="admin-time-edit-grid">
                            <label>
                              <span>
                                Work Date
                              </span>

                              <input
                                type="date"
                                value={
                                  timeDraft
                                    .work_date
                                }
                                onChange={
                                  (event) =>
                                    updateTimeDraft(
                                      "work_date",
                                      event
                                        .target
                                        .value,
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
                                value={
                                  timeDraft
                                    .hours
                                }
                                onChange={
                                  (event) =>
                                    updateTimeDraft(
                                      "hours",
                                      event
                                        .target
                                        .value,
                                    )
                                }
                              />
                            </label>

                            <label className="admin-time-edit-wide">
                              <span>
                                Work Performed
                              </span>

                              <input
                                value={
                                  timeDraft
                                    .description
                                }
                                onChange={
                                  (event) =>
                                    updateTimeDraft(
                                      "description",
                                      event
                                        .target
                                        .value,
                                    )
                                }
                              />
                            </label>

                            <label>
                              <span>
                                Workstream
                              </span>

                              <select
                                value={
                                  timeDraft
                                    .workstream
                                }
                                onChange={
                                  (event) =>
                                    updateTimeDraft(
                                      "workstream",
                                      event
                                        .target
                                        .value,
                                    )
                                }
                              >
                                <option value="">
                                  Not classified
                                </option>

                                {WORKSTREAM_OPTIONS.map(
                                  ([value, label]) => (
                                    <option
                                      key={value}
                                      value={value}
                                    >
                                      {label}
                                    </option>
                                  ),
                                )}
                              </select>
                            </label>

                            <label>
                              <span>
                                Friction
                              </span>

                              <select
                                value={
                                  timeDraft
                                    .friction
                                }
                                onChange={
                                  (event) =>
                                    updateTimeDraft(
                                      "friction",
                                      event
                                        .target
                                        .value,
                                    )
                                }
                              >
                                <option value="">
                                  Not recorded
                                </option>

                                {FRICTION_OPTIONS.map(
                                  ([value, label]) => (
                                    <option
                                      key={value}
                                      value={value}
                                    >
                                      {label}
                                    </option>
                                  ),
                                )}
                              </select>
                            </label>

                            <label className="admin-time-edit-wide">
                              <span>
                                Operational Note
                              </span>

                              <input
                                value={
                                  timeDraft
                                    .operational_note
                                }
                                onChange={
                                  (event) =>
                                    updateTimeDraft(
                                      "operational_note",
                                      event
                                        .target
                                        .value,
                                    )
                                }
                              />
                            </label>
                          </div>

                          <div className="admin-time-edit-actions">
                            {timeDraftSaveState
                            === "error" ? (
                              <button
                                type="button"
                                className="admin-time-edit-action"
                                onClick={
                                  handleRetryTimeDraft
                                }
                              >
                                Retry Save
                              </button>
                            ) : null}

                            <button
                              type="button"
                              className="admin-time-edit-action"
                              disabled={
                                timeDraftSaveState
                                === "saving"
                                || !validTimeDraft(
                                  timeDraft,
                                )
                              }
                              onClick={
                                handleDoneTimeEdit
                              }
                            >
                              Done
                            </button>
                          </div>
                        </div>
                      ) : (
                        <>
                          <div>
                            <span>
                              {
                                entry.work_date
                              }
                            </span>

                            <strong>
                              {
                                entry.description
                              }
                            </strong>

                            <div className="admin-time-signal-meta">
                              <span>
                                {
                                  entry.workstream
                                    ? formatStatus(
                                        entry.workstream,
                                      )
                                    : "Not classified"
                                }
                              </span>

                              <span
                                className="admin-time-signal-separator"
                                aria-hidden="true"
                              >
                                ·
                              </span>

                              <span>
                                {
                                  entry.friction
                                    ? formatStatus(
                                        entry.friction,
                                      )
                                    : "Not recorded"
                                }
                              </span>
                            </div>

                            {entry.operational_note ? (
                              <p className="admin-time-operational-note">
                                {
                                  entry.operational_note
                                }
                              </p>
                            ) : null}
                          </div>

                          <strong>
                            {Number(
                              entry.hours,
                            ).toFixed(2)}
                            {" "}hrs
                          </strong>

                          <div className="admin-time-status-stack">
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
                            === "approved" ? (
                              <button
                                type="button"
                                className="admin-time-approved-edit"
                                disabled={
                                  actionLoading
                                }
                                onClick={() =>
                                  handleEditTime(
                                    entry,
                                  )
                                }
                              >
                                Edit
                              </button>
                            ) : null}
                          </div>

                          {entry.status
                          === "draft" ? (
                            <div className="admin-time-row-actions">
                              <button
                                type="button"
                                className="admin-time-edit-action"
                                disabled={
                                  actionLoading
                                }
                                onClick={() =>
                                  handleEditTime(
                                    entry,
                                  )
                                }
                              >
                                Edit
                              </button>

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
                            </div>
                          ) : (
                            <span />
                          )}
                        </>
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
              <div className="admin-invoice-selection">
                <div className="admin-invoice-selection-head">
                  <div>
                    <span>
                      SELECT WORK
                    </span>

                    <strong>
                      {selectedInvoiceEntryIds.length}
                      {" "}
                      selected
                    </strong>
                  </div>

                  <button
                    type="button"
                    className="admin-invoice-selection-link"
                    onClick={
                      selectedInvoiceEntryIds.length
                      === billableEntries.length
                        ? () =>
                            setSelectedInvoiceEntryIds(
                              []
                            )
                        : selectAllBillableEntries
                    }
                    disabled={
                      billableEntries.length === 0
                    }
                  >
                    {selectedInvoiceEntryIds.length
                    === billableEntries.length
                    && billableEntries.length > 0
                      ? "Clear"
                      : "Select All"}
                  </button>
                </div>

                <div className="admin-invoice-selection-list">
                  {approvedEntries.map(
                    (entry) => {
                      const terms =
                        billingTermsForDate(
                          billingTerms,
                          entry.work_date,
                        );

                      const eligible =
                        Boolean(
                          terms
                          && terms.billing_type
                            === "hourly"
                          && terms.hourly_rate
                          && Number(
                            terms.hourly_rate
                          ) > 0
                        );

                      const amount =
                        eligible
                          ? Number(
                              entry.hours
                            )
                            * Number(
                                terms!
                                  .hourly_rate
                              )
                          : 0;

                      const selected =
                        selectedInvoiceEntryIds
                          .includes(
                            entry.id
                          );

                      return (
                        <label
                          key={entry.id}
                          className={
                            `admin-invoice-selection-row ${
                              selected
                                ? "is-selected"
                                : ""
                            } ${
                              !eligible
                                ? "is-disabled"
                                : ""
                            }`
                          }
                        >
                          <input
                            type="checkbox"
                            checked={
                              selected
                            }
                            disabled={
                              !eligible
                              || actionLoading
                            }
                            onChange={() =>
                              toggleInvoiceEntry(
                                entry.id
                              )
                            }
                          />

                          <div className="admin-invoice-selection-copy">
                            <strong>
                              {entry.description}
                            </strong>

                            <span>
                              {entry.work_date}
                              {" · "}
                              {Number(
                                entry.hours
                              ).toFixed(2)}
                              {" hrs"}

                              {eligible ? (
                                <>
                                  {" · "}
                                  {formatMoney(
                                    Number(
                                      terms!
                                        .hourly_rate
                                    )
                                  )}
                                  /hr
                                </>
                              ) : null}
                            </span>

                            {!eligible ? (
                              <small className="admin-billing-mismatch">
                                Billing terms required
                              </small>
                            ) : null}
                          </div>

                          <strong>
                            {eligible
                              ? formatMoney(
                                  amount
                                )
                              : "—"}
                          </strong>
                        </label>
                      );
                    },
                  )}
                </div>

                <div className="admin-invoice-selection-summary">
                  <span>
                    Selected for Invoice
                  </span>

                  <strong>
                    {formatMoney(
                      selectedInvoiceValue
                    )}
                  </strong>

                  <small>
                    {selectedInvoiceHours
                      .toFixed(2)}
                    {" "}
                    hours
                  </small>
                </div>
              </div>

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
                  || selectedInvoiceEntryIds
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
                          <div className="admin-invoice-draft-actions">
                            <button
                              type="button"
                              className="admin-cancel-button"
                              disabled={
                                actionLoading
                              }
                              onClick={() =>
                                beginInvoiceEdit(
                                  invoice
                                )
                              }
                            >
                              Edit Draft
                            </button>

                            <button
                              type="button"
                              className="button button-primary"
                              disabled={
                                actionLoading
                                || !invoice.bill_to_email
                              }
                              onClick={() =>
                                beginInvoiceReview(
                                  invoice
                                )
                              }
                            >
                              Review & Send
                            </button>
                          </div>
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

      {activeInvoice
      && invoiceDraft
      && invoiceFlowStep ? (
        <div
          className="admin-invoice-modal-backdrop"
          role="presentation"
        >
          <section
            className="admin-invoice-glass"
            role="dialog"
            aria-modal="true"
            aria-label={
              invoiceFlowStep === "edit"
                ? "Edit invoice draft"
                : invoiceFlowStep === "review"
                  ? "Review invoice"
                  : "Confirm invoice send"
            }
          >
            <div className="admin-invoice-glass-spectrum" />

            <header className="admin-invoice-modal-header">
              <div>
                <p className="kicker">
                  {invoiceFlowStep === "edit"
                    ? "EDIT DRAFT"
                    : invoiceFlowStep === "review"
                      ? "REVIEW INVOICE"
                      : "FINAL CONFIRMATION"}
                </p>

                <h3>
                  {activeInvoice.invoice_number}
                </h3>

                <p>
                  {activeInvoice.bill_to_name}
                </p>
              </div>

              <button
                type="button"
                className="admin-invoice-modal-close"
                onClick={
                  closeInvoiceFlow
                }
                disabled={
                  actionLoading
                  || invoiceDraftSaving
                }
                aria-label="Close invoice dialog"
              >
                ×
              </button>
            </header>

            {invoiceFlowStep === "edit" ? (
              <>
                <div className="admin-invoice-edit-grid">
                  <label>
                    <span>
                      Bill To
                    </span>

                    <input
                      value={
                        invoiceDraft.bill_to_name
                      }
                      onChange={(event) =>
                        updateInvoiceDraft(
                          "bill_to_name",
                          event.target.value,
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
                      value={
                        invoiceDraft.bill_to_email
                      }
                      onChange={(event) =>
                        updateInvoiceDraft(
                          "bill_to_email",
                          event.target.value,
                        )
                      }
                    />
                  </label>

                  <label>
                    <span>
                      Issue Date
                    </span>

                    <input
                      type="date"
                      value={
                        invoiceDraft.issue_date
                      }
                      onChange={(event) =>
                        updateInvoiceDraft(
                          "issue_date",
                          event.target.value,
                        )
                      }
                    />
                  </label>

                  <label>
                    <span>
                      Due Date
                    </span>

                    <input
                      type="date"
                      value={
                        invoiceDraft.due_date
                      }
                      onChange={(event) =>
                        updateInvoiceDraft(
                          "due_date",
                          event.target.value,
                        )
                      }
                    />
                  </label>

                  <label className="admin-invoice-modal-span">
                    <span>
                      Bill To Address
                    </span>

                    <textarea
                      rows={3}
                      value={
                        invoiceDraft.bill_to_address
                      }
                      onChange={(event) =>
                        updateInvoiceDraft(
                          "bill_to_address",
                          event.target.value,
                        )
                      }
                    />
                  </label>

                  <label className="admin-invoice-modal-span">
                    <span>
                      Terms
                    </span>

                    <input
                      value={
                        invoiceDraft.terms
                      }
                      onChange={(event) =>
                        updateInvoiceDraft(
                          "terms",
                          event.target.value,
                        )
                      }
                      placeholder="Net 15"
                    />
                  </label>

                  <label className="admin-invoice-modal-span">
                    <span>
                      Notes
                    </span>

                    <textarea
                      rows={3}
                      value={
                        invoiceDraft.notes
                      }
                      onChange={(event) =>
                        updateInvoiceDraft(
                          "notes",
                          event.target.value,
                        )
                      }
                    />
                  </label>
                </div>

                <div className="admin-invoice-modal-actions">
                  <button
                    type="button"
                    className="admin-invoice-delete-button"
                    onClick={() =>
                      setInvoiceFlowStep(
                        "delete"
                      )
                    }
                    disabled={
                      invoiceDraftSaving
                    }
                  >
                    Delete Draft
                  </button>

                  <button
                    type="button"
                    className="admin-cancel-button"
                    onClick={
                      closeInvoiceFlow
                    }
                    disabled={
                      invoiceDraftSaving
                    }
                  >
                    Cancel
                  </button>

                  <button
                    type="button"
                    className="button button-primary"
                    onClick={() =>
                      saveInvoiceDraft(
                        "review"
                      )
                    }
                    disabled={
                      invoiceDraftSaving
                    }
                  >
                    {invoiceDraftSaving
                      ? "Saving…"
                      : "Save & Review"}
                  </button>
                </div>
              </>
            ) : null}

            {invoiceFlowStep === "review" ? (
              <>
                <div className="admin-invoice-review-grid">
                  <div className="admin-invoice-review-panel">
                    <span>
                      BILL TO
                    </span>

                    <strong>
                      {activeInvoice.bill_to_name}
                    </strong>

                    <p>
                      {activeInvoice.bill_to_email}
                    </p>

                    {activeInvoice.bill_to_address ? (
                      <p className="admin-invoice-review-pre">
                        {activeInvoice.bill_to_address}
                      </p>
                    ) : null}
                  </div>

                  <div className="admin-invoice-review-panel">
                    <span>
                      INVOICE
                    </span>

                    <strong>
                      {activeInvoice.invoice_number}
                    </strong>

                    <p>
                      Issue{" "}
                      {activeInvoice.issue_date
                        ?? "—"}
                    </p>

                    <p>
                      Due{" "}
                      {activeInvoice.due_date
                        ?? "—"}
                    </p>
                  </div>
                </div>

                <div className="admin-invoice-review-lines">
                  {activeInvoice.line_items.map(
                    (line) => (
                      <div
                        key={line.id}
                        className="admin-invoice-review-line"
                      >
                        <div>
                          <strong>
                            {line.description}
                          </strong>

                          <span>
                            {line.quantity}
                            {" × "}
                            {formatMoney(
                              line.unit_rate
                            )}
                          </span>
                        </div>

                        <strong>
                          {formatMoney(
                            line.amount
                          )}
                        </strong>
                      </div>
                    ),
                  )}
                </div>

                <div className="admin-invoice-review-total">
                  <span>
                    TOTAL
                  </span>

                  <strong>
                    {formatMoney(
                      activeInvoice.total
                    )}
                  </strong>
                </div>

                {activeInvoice.terms ? (
                  <div className="admin-invoice-review-note">
                    <span>
                      TERMS
                    </span>

                    <p>
                      {activeInvoice.terms}
                    </p>
                  </div>
                ) : null}

                {activeInvoice.notes ? (
                  <div className="admin-invoice-review-note">
                    <span>
                      NOTES
                    </span>

                    <p>
                      {activeInvoice.notes}
                    </p>
                  </div>
                ) : null}

                <div className="admin-invoice-modal-actions">
                  <button
                    type="button"
                    className="admin-cancel-button"
                    onClick={() =>
                      setInvoiceFlowStep(
                        "edit"
                      )
                    }
                  >
                    Back to Edit
                  </button>

                  <button
                    type="button"
                    className="button button-primary"
                    onClick={() =>
                      setInvoiceFlowStep(
                        "confirm"
                      )
                    }
                  >
                    Continue to Send
                  </button>
                </div>
              </>
            ) : null}

            {invoiceFlowStep === "delete" ? (
              <>
                <div className="admin-invoice-confirm admin-invoice-confirm-danger">
                  <span className="admin-invoice-confirm-label">
                    DELETE DRAFT
                  </span>

                  <strong>
                    {activeInvoice.invoice_number}
                  </strong>

                  <p>
                    Delete this draft invoice?
                  </p>

                  <small>
                    Its source time entries
                    will return to Approved /
                    Ready to Bill. The invoice
                    number remains reserved
                    and will not be reused.
                  </small>
                </div>

                <div className="admin-invoice-modal-actions">
                  <button
                    type="button"
                    className="admin-cancel-button"
                    onClick={() =>
                      setInvoiceFlowStep(
                        "edit"
                      )
                    }
                    disabled={
                      actionLoading
                    }
                  >
                    Keep Draft
                  </button>

                  <button
                    type="button"
                    className="admin-invoice-delete-confirm"
                    onClick={
                      handleDeleteInvoiceDraft
                    }
                    disabled={
                      actionLoading
                    }
                  >
                    {actionLoading
                      ? "Deleting…"
                      : "Delete Draft"}
                  </button>
                </div>
              </>
            ) : null}

            {invoiceFlowStep === "confirm" ? (
              <>
                <div className="admin-invoice-confirm">
                  <span className="admin-invoice-confirm-label">
                    READY TO SEND
                  </span>

                  <strong>
                    {formatMoney(
                      activeInvoice.total
                    )}
                  </strong>

                  <p>
                    Send{" "}
                    {activeInvoice.invoice_number}
                    {" to "}
                    <b>
                      {activeInvoice.bill_to_email}
                    </b>
                    ?
                  </p>

                  <small>
                    Once delivery succeeds,
                    this invoice becomes part
                    of billing history and is
                    no longer editable.
                  </small>
                </div>

                <div className="admin-invoice-modal-actions">
                  <button
                    type="button"
                    className="admin-cancel-button"
                    onClick={() =>
                      setInvoiceFlowStep(
                        "review"
                      )
                    }
                    disabled={
                      actionLoading
                    }
                  >
                    Back
                  </button>

                  <button
                    type="button"
                    className="button button-primary"
                    disabled={
                      actionLoading
                    }
                    onClick={() =>
                      handleSendInvoice(
                        activeInvoice
                      )
                    }
                  >
                    {actionLoading
                      ? "Sending…"
                      : "Yes, Send Invoice"}
                  </button>
                </div>
              </>
            ) : null}
          </section>
        </div>
      ) : null}

    </div>
  );
}
