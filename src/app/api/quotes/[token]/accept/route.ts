import { NextResponse } from "next/server";

const PLATFORM_API =
  process.env.RA_PLATFORM_API_URL ??
  "http://127.0.0.1:8000";

export async function POST(
  _request: Request,
  context: {
    params: Promise<{
      token: string;
    }>;
  },
) {
  const { token } = await context.params;

  const response = await fetch(
    `${PLATFORM_API}/quotes/public/${encodeURIComponent(
      token,
    )}/accept`,
    {
      method: "POST",
      cache: "no-store",
    },
  );

  const body = await response.json();

  return NextResponse.json(
    body,
    {
      status: response.status,
    },
  );
}
