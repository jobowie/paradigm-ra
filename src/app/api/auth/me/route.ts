import {
  cookies,
} from "next/headers";

import {
  NextResponse,
} from "next/server";

const PLATFORM_API =
  process.env.RA_PLATFORM_API_URL ??
  "https://ra-platform-api.onrender.com";

const SESSION_COOKIE =
  "paradigm_ra_session";


export async function GET() {
  const cookieStore =
    await cookies();

  const sessionToken =
    cookieStore.get(
      SESSION_COOKIE,
    )?.value;

  if (!sessionToken) {
    return NextResponse.json(
      {
        detail:
          "Authentication required.",
      },
      {
        status: 401,
      },
    );
  }

  const response = await fetch(
    `${PLATFORM_API}/auth/me`,
    {
      method: "GET",
      headers: {
        Authorization:
          `Bearer ${sessionToken}`,
      },
      cache: "no-store",
    },
  );

  const data =
    await response.json();

  const nextResponse =
    NextResponse.json(
      data,
      {
        status: response.status,
      },
    );

  if (response.status === 401) {
    nextResponse.cookies.delete(
      SESSION_COOKIE
    );
  }

  return nextResponse;
}
