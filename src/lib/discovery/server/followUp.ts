import { Resend } from "resend";

import type {
  CompletedLead,
} from "@/lib/discovery/server/postDiscovery";


function formatValue(
  value: unknown,
): string {
  if (
    value === null ||
    value === undefined
  ) {
    return "Unknown";
  }

  if (Array.isArray(value)) {
    return value.length > 0
      ? value.join(", ")
      : "None";
  }

  if (typeof value === "string") {
    return value.trim() || "Unknown";
  }

  if (
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return String(value);
  }

  return JSON.stringify(value);
}


function formatStatus(
  value: CompletedLead["status"],
): string {
  return value
    .split("_")
    .map(
      (part) =>
        part.charAt(0).toUpperCase() +
        part.slice(1),
    )
    .join(" ");
}


function formatRecommendedNextStep(
  value:
    CompletedLead["recommendedNextStep"],
): string {
  switch (value) {
    case "book_discovery_call":
      return "Book discovery call";

    case "request_more_information":
      return "Request more information";

    case "not_a_fit":
      return "Not a fit";

    case "continue_discovery":
      return "Continue discovery";

    default:
      return "Unknown";
  }
}


export function buildInternalLeadBrief(
  lead: CompletedLead,
): string {
  const {
    contact,
    brief,
  } = lead;

  const qualificationScore =
    typeof brief.qualificationScore === "number"
      ? `${brief.qualificationScore}/100`
      : formatValue(
          brief.qualificationScore,
        );

  return [
    "RA POST-DISCOVERY — LEAD READY",
    "--------------------------------",
    "",
    contact.company,
    `${contact.firstName} — ${contact.email}`,
    "",
    `Recommended next step: ${formatRecommendedNextStep(
      lead.recommendedNextStep,
    )}`,
    `Qualification score: ${qualificationScore}`,
    `Status: ${formatStatus(
      lead.status,
    )}`,
    "",
    "PRIMARY NEED",
    formatValue(
      brief.primaryProblem,
    ),
    "",
    "BUSINESS IMPACT",
    formatValue(
      brief.businessImpact,
    ),
    "",
    "DISCOVERY DETAILS",
    `Business: ${formatValue(
      brief.businessDescription,
    )}`,
    `Current process: ${formatValue(
      brief.currentProcess,
    )}`,
    `Current systems: ${formatValue(
      brief.currentSystems,
    )}`,
    `Pain points: ${formatValue(
      brief.painPoints,
    )}`,
    `Desired outcomes: ${formatValue(
      brief.desiredOutcomes,
    )}`,
    `Teams affected: ${formatValue(
      brief.usersOrTeamsAffected,
    )}`,
    `Service category: ${formatValue(
      brief.serviceCategory,
    )}`,
    `Integrations needed: ${formatValue(
      brief.integrationsNeeded,
    )}`,
    `Urgency: ${formatValue(
      brief.urgency,
    )}`,
    `Timeline: ${formatValue(
      brief.timeline,
    )}`,
    `Decision process: ${formatValue(
      brief.decisionProcess,
    )}`,
    "",
    "OPEN ITEMS",
    `Budget context: ${formatValue(
      brief.budgetContext,
    )}`,
    `Requirements: ${formatValue(
      brief.requirements,
    )}`,
    `Missing information: ${formatValue(
      brief.missingInformation,
    )}`,
    "",
    `Lead ID: ${lead.id}`,
    `Session ID: ${lead.sessionId}`,
    `Completed at: ${lead.completedAt}`,
  ].join("\n");
}


export async function notifyCompletedLead(
  lead: CompletedLead,
): Promise<void> {
  const apiKey =
    process.env.RESEND_API_KEY;

  const from =
    process.env
      .RA_LEAD_NOTIFICATION_FROM;

  const to =
    process.env
      .RA_LEAD_NOTIFICATION_TO;

  if (!apiKey || !from || !to) {
    throw new Error(
      "Ra lead notification email configuration is missing.",
    );
  }

  const resend =
    new Resend(
      apiKey,
    );

  const brief =
    buildInternalLeadBrief(
      lead,
    );

  const {
    data,
    error,
  } = await resend.emails.send(
    {
      from,
      to: [to],

      subject:
        `Ra Lead — ${lead.contact.company}`,

      text: brief,
    },
    {
      idempotencyKey:
        `ra-completed-lead/${lead.id}`,
    },
  );

  if (error) {
    throw new Error(
      `Ra lead notification failed: ${error.message}`,
    );
  }

  console.info(
    "RA POST-DISCOVERY — LEAD NOTIFIED",
    {
      leadId:
        lead.id,

      sessionId:
        lead.sessionId,

      emailId:
        data?.id ?? null,
    },
  );
}