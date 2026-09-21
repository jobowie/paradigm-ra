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


export async function POST() {
  const cookieStore =
    await cookies();

  const sessionToken =
    cookieStore.get(
      SESSION_COOKIE,
    )?.value;

  if (sessionToken) {
    try {
      await fetch(
        `${PLATFORM_API}/auth/logout`,
        {
          method: "POST",
          headers: {
            Authorization:
              `Bearer ${sessionToken}`,
          },
          cache: "no-store",
        },
      );
    } catch {
      // Local session still clears even
      // if the upstream logout call fails.
    }
  }

  const response =
    NextResponse.json({
      logged_out: true,
    });

  response.cookies.delete(
    SESSION_COOKIE
  );

  return response;
}
