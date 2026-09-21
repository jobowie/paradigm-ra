import {
  NextResponse,
} from "next/server";

const PLATFORM_API =
  process.env.RA_PLATFORM_API_URL ??
  "https://ra-platform-api.onrender.com";

const SESSION_COOKIE =
  "paradigm_ra_session";

export async function POST(
  request: Request,
) {
  let body: unknown;

  try {
    body = await request.json();
  } catch {
    return NextResponse.json(
      {
        detail:
          "Invalid login request.",
      },
      {
        status: 400,
      },
    );
  }

  let response: Response;

  try {
    response = await fetch(
      `${PLATFORM_API}/auth/login`,
      {
        method: "POST",
        headers: {
          "Content-Type":
            "application/json",
        },
        body: JSON.stringify(body),
        cache: "no-store",
      },
    );
  } catch {
    return NextResponse.json(
      {
        detail:
          "Authentication service is unavailable.",
      },
      {
        status: 502,
      },
    );
  }

  const responseText =
    await response.text();

  let data: Record<string, unknown>;

  try {
    data = responseText
      ? JSON.parse(responseText)
      : {};
  } catch {
    return NextResponse.json(
      {
        detail:
          "Authentication service returned an invalid response.",
      },
      {
        status: 502,
      },
    );
  }

  if (!response.ok) {
    return NextResponse.json(
      data,
      {
        status: response.status,
      },
    );
  }

  const sessionToken =
    data.session_token;

  const expiresAt =
    data.expires_at;

  if (
    typeof sessionToken !== "string"
    || typeof expiresAt !== "string"
  ) {
    return NextResponse.json(
      {
        detail:
          "Authentication response was invalid.",
      },
      {
        status: 502,
      },
    );
  }

  const {
    session_token: _sessionToken,
    ...publicData
  } = data;

  const nextResponse =
    NextResponse.json(
      publicData,
      {
        status: 200,
      },
    );

  nextResponse.cookies.set({
    name: SESSION_COOKIE,
    value: sessionToken,
    httpOnly: true,
    secure:
      process.env.NODE_ENV ===
      "production",
    sameSite: "lax",
    path: "/",
    expires: new Date(
      expiresAt,
    ),
  });

  return nextResponse;
}
