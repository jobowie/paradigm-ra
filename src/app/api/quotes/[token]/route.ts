import { NextResponse } from "next/server";

const PLATFORM_API =
  process.env.RA_PLATFORM_API_URL ??
  "https://ra-platform-api.onrender.com";

export async function GET(
  _request: Request,
  context: {
    params: Promise<{
      token: string;
    }>;
  },
) {
  try {
    const { token } = await context.params;

    const response = await fetch(
      `${PLATFORM_API}/quotes/public/${encodeURIComponent(
        token,
      )}`,
      {
        cache: "no-store",
      },
    );

    const raw = await response.text();

    return new NextResponse(raw, {
      status: response.status,
      headers: {
        "Content-Type":
          response.headers.get(
            "content-type",
          ) ?? "application/json",
      },
    });
  } catch (error) {
    console.error(
      "Quote proxy GET failed:",
      error,
    );

    return NextResponse.json(
      {
        detail:
          error instanceof Error
            ? error.message
            : "Quote proxy failed.",
      },
      {
        status: 500,
      },
    );
  }
}
