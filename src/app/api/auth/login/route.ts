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
  const body = await request.json();

  const response = await fetch(
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

  const data =
    await response.json();

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
      expiresAt
    ),
  });

  return nextResponse;
}
