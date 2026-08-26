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

  return [
    "RA POST-DISCOVERY — LEAD READY",
    "--------------------------------",
    `Lead ID: ${lead.id}`,
    `Session ID: ${lead.sessionId}`,
    "",
    `Contact: ${contact.firstName}`,
    `Company: ${contact.company}`,
    `Email: ${contact.email}`,
    "",
    `Status: ${lead.status}`,
    `Recommended next step: ${formatRecommendedNextStep(
      lead.recommendedNextStep,
    )}`,
    "",
    `Business: ${formatValue(
      brief.businessDescription,
    )}`,
    `Primary problem: ${formatValue(
      brief.primaryProblem,
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
    `Business impact: ${formatValue(
      brief.businessImpact,
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
    `Requirements: ${formatValue(
      brief.requirements,
    )}`,
    `Urgency: ${formatValue(
      brief.urgency,
    )}`,
    `Timeline: ${formatValue(
      brief.timeline,
    )}`,
    `Budget context: ${formatValue(
      brief.budgetContext,
    )}`,
    `Decision process: ${formatValue(
      brief.decisionProcess,
    )}`,
    `Qualification score: ${formatValue(
      brief.qualificationScore,
    )}`,
    `Missing information: ${formatValue(
      brief.missingInformation,
    )}`,
    "",
    `Completed at: ${lead.completedAt}`,
  ].join("\n");
}


export async function notifyCompletedLead(
  lead: CompletedLead,
): Promise<void> {
  const brief =
    buildInternalLeadBrief(
      lead,
    );

  console.info(brief);
}