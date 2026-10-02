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


export async function GET(
  _request: Request,
  context: {
    params: Promise<{
      invoiceId: string;
    }>;
  },
) {
  const {
    invoiceId,
  } = await context.params;

  const cookieStore =
    await cookies();

  const token =
    cookieStore.get(
      SESSION_COOKIE,
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
      `${PLATFORM_API}/admin/invoices/${invoiceId}/preview`,
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
        "content-type",
      ) ?? "";

    if (!response.ok) {
      const data =
        contentType.includes(
          "application/json"
        )
          ? await response.json()
          : {
              detail:
                "Unable to preview invoice.",
            };

      return NextResponse.json(
        data,
        {
          status: response.status,
        },
      );
    }

    const pdf =
      await response.arrayBuffer();

    return new NextResponse(
      pdf,
      {
        status: 200,
        headers: {
          "Content-Type":
            "application/pdf",
          "Content-Disposition":
            response.headers.get(
              "content-disposition",
            )
            ?? "inline",
          "Cache-Control":
            "private, no-store",
          "Pragma":
            "no-cache",
          "X-Content-Type-Options":
            "nosniff",
        },
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
