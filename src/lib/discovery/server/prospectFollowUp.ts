import { Resend } from "resend";

import type {
  CompletedLead,
} from "@/lib/discovery/server/postDiscovery";


export interface ProspectFollowUpMessage {
  subject: string;
  text: string;
}


function cleanInline(
  value: string,
): string {
  return value
    .replace(
      
      /[\r\n]+/g,
      " ",
    )
    .trim();
}


function formatPrimaryProblem(
  value: unknown,
): string | null {
  if (typeof value !== "string") {
    return null;
  }

  const problem =
    value.trim();

  return problem || null;
}


export function buildProspectFollowUp(
  lead: CompletedLead,
): ProspectFollowUpMessage | null {
  if (
    lead.recommendedNextStep !==
    "book_discovery_call"
  ) {
    return null;
  }

  const firstName =
    cleanInline(
      lead.contact.firstName,
    );

  const company =
    cleanInline(
      lead.contact.company,
    );

  const primaryProblem =
    formatPrimaryProblem(
      lead.brief.primaryProblem,
    );

  const body = [
    `Hi ${firstName},`,
    "",
    `Thanks for taking the time to share what’s slowing things down at ${company}.`,
    "",
    "We’ve received your discovery and have enough context to review the workflow, priorities, and systems involved.",
    "",
    ...(primaryProblem
      ? [
          "What we heard:",
          primaryProblem,
          "",
        ]
      : []),
    "The next step is a short conversation with the Paradigm Ra team to look at the problem in more detail and determine the best path forward.",
    "",
    "We’ll follow up shortly to coordinate.",
    "",
    "Best,",
    "Paradigm Ra",
    "Software. Systems. Financial clarity.",
    "solutions@paradigmra.tech",
  ];

  return {
    subject:
      `Thanks, ${firstName} — Paradigm Ra Discovery`,

    text:
      body.join("\n"),
  };
}


export async function sendProspectFollowUp(
  lead: CompletedLead,
): Promise<void> {
  const message =
    buildProspectFollowUp(
      lead,
    );

  if (!message) {
    console.info(
      "RA POST-DISCOVERY — PROSPECT FOLLOW-UP SKIPPED",
      {
        leadId:
          lead.id,

        sessionId:
          lead.sessionId,

        recommendedNextStep:
          lead.recommendedNextStep,
      },
    );

    return;
  }

  const apiKey =
    process.env.RESEND_API_KEY;

  const from =
    process.env
      .RA_LEAD_NOTIFICATION_FROM;

  if (!apiKey || !from) {
    throw new Error(
      "Ra prospect follow-up email configuration is missing.",
    );
  }

  const resend =
    new Resend(
      apiKey,
    );

  const {
    data,
    error,
  } = await resend.emails.send(
    {
      from,

      to: [
        lead.contact.email,
      ],

      subject:
        message.subject,

      text:
        message.text,
    },
    {
      idempotencyKey:
        `ra-prospect-follow-up/${lead.id}`,
    },
  );

  if (error) {
    throw new Error(
      `Ra prospect follow-up failed: ${error.message}`,
    );
  }

  console.info(
    "RA POST-DISCOVERY — PROSPECT NOTIFIED",
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