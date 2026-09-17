import {
  PublicQuoteClient,
} from "@/components/PublicQuoteClient";


export default async function QuotePage({
  params,
}: {
  params: Promise<{
    token: string;
  }>;
}) {
  const { token } =
    await params;

  return (
    <PublicQuoteClient
      token={token}
    />
  );
}
