import { getStore } from "@netlify/blobs";
import { randomUUID } from "node:crypto";

export interface RaSessionMessage {
  role: "prospect" | "agent";
  content: string;
}

export interface RaSession {
  id: string;

  contact: {
    firstName: string;
    company: string;
    email: string;
  };

  history: RaSessionMessage[];

  currentState: Record<string, unknown>;

  complete: boolean;
  recommendedNextStep:
    | "continue_discovery"
    | "book_discovery_call"
    | "request_more_information"
    | "not_a_fit"
    | null;

  discoveryQuestionCount: number;

  createdAt: string;
  updatedAt: string;
}

const STORE_NAME = "ra-discovery-sessions";

function store() {
  return getStore({
    name: STORE_NAME,
    consistency: "strong",
  });
}

export function createSessionId(): string {
  return randomUUID();
}

export async function createRaSession(
  input: Pick<
    RaSession["contact"],
    "firstName" | "company" | "email"
  >,
): Promise<RaSession> {
  const now = new Date().toISOString();

  const session: RaSession = {
    id: createSessionId(),

    contact: {
      firstName: input.firstName,
      company: input.company,
      email: input.email,
    },

    history: [],
    currentState: {},

    complete: false,
    recommendedNextStep: null,

    discoveryQuestionCount: 0,

    createdAt: now,
    updatedAt: now,
  };

  await store().setJSON(
    session.id,
    session,
    {
      onlyIfNew: true,
    },
  );

  return session;
}

export async function getRaSession(
  id: string,
): Promise<RaSession | null> {
  return store().get(
    id,
    {
      type: "json",
      consistency: "strong",
    },
  ) as Promise<RaSession | null>;
}

export async function saveRaSession(
  session: RaSession,
): Promise<void> {
  const next: RaSession = {
    ...session,
    updatedAt: new Date().toISOString(),
  };

  await store().setJSON(
    session.id,
    next,
  );
}
