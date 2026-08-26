import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import {
  getRaSession,
  saveRaSession,
} from "@/lib/discovery/server/sessionStore";

import {
  createCompletedLead,
} from "@/lib/discovery/server/postDiscovery";

import {
  notifyCompletedLead,
} from "@/lib/discovery/server/followUp";

import {
  sendProspectFollowUp,
} from "@/lib/discovery/server/prospectFollowUp";


const COOKIE_NAME = "ra_sid";


interface RaResponse {
  reply: string;

  stage: string;

  complete: boolean;

  recommended_next_step:
    | "continue_discovery"
    | "book_discovery_call"
    | "request_more_information"
    | "not_a_fit";

  state: Record<string, unknown>;
}


function cleanMessage(
  value: unknown,
): string {
  if (typeof value !== "string") {
    return "";
  }

  return value
    .trim()
    .slice(
      0,
      6000,
    );
}


export async function POST(
  request: Request,
) {
  const cookieStore =
    await cookies();

  const sessionId =
    cookieStore.get(
      COOKIE_NAME,
    )?.value;

  if (!sessionId) {
    return NextResponse.json(
      {
        error:
          "Discovery session not found.",
      },
      {
        status: 401,
      },
    );
  }

  const session =
    await getRaSession(
      sessionId,
    );

  if (!session) {
    return NextResponse.json(
      {
        error:
          "Discovery session expired.",
      },
      {
        status: 404,
      },
    );
  }

  if (session.complete) {
    return NextResponse.json(
      {
        error:
          "Discovery is already complete.",
      },
      {
        status: 409,
      },
    );
  }

  const body =
    (await request.json()) as {
      message?: unknown;
    };

  const message =
    cleanMessage(
      body.message,
    );

  if (!message) {
    return NextResponse.json(
      {
        error:
          "Please enter a message.",
      },
      {
        status: 400,
      },
    );
  }

  const raUrl =
    process.env
      .RA_DISCOVERY_URL;

  const raToken =
    process.env
      .RA_DISCOVERY_INTERNAL_TOKEN;

  if (!raUrl || !raToken) {
    console.error(
      "Ra Discovery server configuration missing.",
    );

    return NextResponse.json(
      {
        error:
          "Discovery is temporarily unavailable.",
      },
      {
        status: 503,
      },
    );
  }

  const raRequest = {
    contact: {
      first_name:
        session.contact.firstName,

      company:
        session.contact.company,

      email:
        session.contact.email,
    },

    history:
      session.history.slice(-20),

    latest_prospect_message:
      message,

    current_state:
      session.currentState,
  };

  const result =
    await fetch(
      `${raUrl}/v1/discovery/turn`,
      {
        method: "POST",

        headers: {
          "Content-Type":
            "application/json",

          Authorization:
            `Bearer ${raToken}`,
        },

        body: JSON.stringify(
          raRequest,
        ),

        cache: "no-store",
      },
    );

  if (!result.ok) {
    console.error(
      "Ra Discovery request failed:",
      result.status,
    );

    return NextResponse.json(
      {
        error:
          "Discovery is temporarily unavailable.",
      },
      {
        status: 502,
      },
    );
  }

  const ra =
    (await result.json()) as RaResponse;

  const questionCount =
    (ra.reply.match(/\?/g) ?? [])
      .length;

  session.history.push(
    {
      role: "prospect",
      content: message,
    },
    {
      role: "agent",
      content: ra.reply,
    },
  );

  session.currentState =
    ra.state;

  session.complete =
    ra.complete;

  session.recommendedNextStep =
    ra.recommended_next_step;

  session.discoveryQuestionCount +=
    questionCount;

  await saveRaSession(
    session,
  );

  if (ra.complete) {
    const {
      lead,
      created,
    } = await createCompletedLead(
      session,
    );

    if (created) {
      try {
        await notifyCompletedLead(
          lead,
        );
      } catch (error) {
        console.error(
          "Ra internal lead notification failed.",
          error instanceof Error
            ? error.name
            : "UnknownError",
        );
      }

      try {
        await sendProspectFollowUp(
          lead,
        );
      } catch (error) {
        console.error(
          "Ra prospect follow-up failed.",
          error instanceof Error
            ? error.name
            : "UnknownError",
        );
      }
    }
  }

  return NextResponse.json({
    reply:
      ra.reply,

    stage:
      ra.stage,

    complete:
      ra.complete,

    recommendedNextStep:
      ra.recommended_next_step,
  });
}