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

  const token =
    cookieStore.get(
      SESSION_COOKIE
    )?.value;

  if (!token) {
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

  try {
    const response = await fetch(
      `${PLATFORM_API}/admin/organizations`,
      {
        headers: {
          Authorization:
            `Bearer ${token}`,
        },
        cache: "no-store",
      },
    );

    const contentType =
      response.headers.get(
        "content-type"
      ) ?? "";

    if (
      !contentType.includes(
        "application/json"
      )
    ) {
      return NextResponse.json(
        {
          detail:
            "Platform API unavailable.",
        },
        {
          status: 502,
        },
      );
    }

    const data =
      await response.json();

    return NextResponse.json(
      data,
      {
        status: response.status,
      },
    );

  } catch {
    return NextResponse.json(
      {
        detail:
          "Platform API unavailable.",
      },
      {
        status: 502,
      },
    );
  }
}
