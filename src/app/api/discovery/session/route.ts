import { NextResponse } from "next/server";

import {
  createRaSession,
} from "@/lib/discovery/server/sessionStore";


const COOKIE_NAME = "ra_sid";


interface SessionRequest {
  firstName?: unknown;
  company?: unknown;
  email?: unknown;
}


function cleanText(
  value: unknown,
  maxLength: number,
): string {
  if (typeof value !== "string") {
    return "";
  }

  return value.trim().slice(
    0,
    maxLength,
  );
}


export async function POST(
  request: Request,
) {
  const body =
    (await request.json()) as SessionRequest;

  const firstName = cleanText(
    body.firstName,
    80,
  );

  const company = cleanText(
    body.company,
    160,
  );

  const email = cleanText(
    body.email,
    320,
  );

  if (
    !firstName ||
    !company ||
    !email ||
    !email.includes("@")
  ) {
    return NextResponse.json(
      {
        error:
          "Please provide your name, company, and email.",
      },
      {
        status: 400,
      },
    );
  }

  const session = await createRaSession({
    firstName,
    company,
    email,
  });

  const response = NextResponse.json(
    {
      ready: true,
    },
    {
      status: 201,
    },
  );

  response.cookies.set({
    name: COOKIE_NAME,
    value: session.id,

    httpOnly: true,
    secure:
      process.env.NODE_ENV ===
      "production",

    sameSite: "lax",
    path: "/",

    maxAge:
      60 * 60 * 24 * 14,
  });

  return response;
}
