import {
  platformAdminFetch,
} from "@/lib/server/platformAdminApi";

interface RouteContext {
  params: Promise<{
    invoiceId: string;
  }>;
}

export async function PUT(
  request: Request,
  context: RouteContext,
) {
  const { invoiceId } =
    await context.params;

  const body =
    await request.text();

  return platformAdminFetch(
    `/admin/invoices/${encodeURIComponent(
      invoiceId
    )}`,
    {
      method: "PUT",
      headers: {
        "Content-Type":
          "application/json",
      },
      body,
    },
  );
}

export async function DELETE(
  _request: Request,
  context: RouteContext,
) {
  const { invoiceId } =
    await context.params;

  return platformAdminFetch(
    `/admin/invoices/${encodeURIComponent(
      invoiceId
    )}`,
    {
      method: "DELETE",
    },
  );
}
