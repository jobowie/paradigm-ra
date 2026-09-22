import {
  platformAdminFetch,
} from "@/lib/server/platformAdminApi";

export async function GET(
  _request: Request,
  context: {
    params: Promise<{
      organizationId: string;
    }>;
  },
) {
  const {
    organizationId,
  } = await context.params;

  return platformAdminFetch(
    `/admin/organizations/${organizationId}/contacts`,
  );
}

export async function POST(
  request: Request,
  context: {
    params: Promise<{
      organizationId: string;
    }>;
  },
) {
  const {
    organizationId,
  } = await context.params;

  return platformAdminFetch(
    `/admin/organizations/${organizationId}/contacts`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: await request.text(),
    },
  );
}
