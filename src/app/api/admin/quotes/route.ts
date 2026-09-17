import { NextResponse } from "next/server";

const PLATFORM_API =
  process.env.RA_PLATFORM_API_URL ??
  "http://127.0.0.1:8000";

export async function POST(
  request: Request,
) {
  const adminKey =
    request.headers.get(
      "x-ra-admin-key",
    );

  if (!adminKey) {
    return NextResponse.json(
      {
        detail:
          "Admin key is required.",
      },
      {
        status: 401,
      },
    );
  }

  const body =
    await request.json();

  const response = await fetch(
    `${PLATFORM_API}/admin/quotes`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
        "X-RA-Admin-Key":
          adminKey,
      },
      body: JSON.stringify(body),
      cache: "no-store",
    },
  );

  const data =
    await response.json();

  return NextResponse.json(
    data,
    {
      status: response.status,
    },
  );
}
