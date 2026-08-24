import { getStore } from "@netlify/blobs";
import { randomUUID } from "node:crypto";

import type {
  RaSession,
} from "@/lib/discovery/server/sessionStore";


export type LeadStatus =
  | "awaiting_review"
  | "reviewed"
  | "contacted"
  | "discovery_call"
  | "proposal"
  | "won"
  | "lost";


export interface DiscoveryBrief {
  primaryProblem: unknown;
  currentProcess: unknown;
  currentSystems: unknown;
  painPoints: unknown;
  desiredOutcomes: unknown;
  businessImpact: unknown;
  urgency: unknown;
  timeline: unknown;
  serviceCategory: unknown;
  integrationsNeeded: unknown;
  requirements: unknown;
  decisionProcess: unknown;
  missingInformation: unknown;
  qualificationScore: unknown;
}


export interface CompletedLead {
  id: string;
  sessionId: string;

  contact: {
    firstName: string;
    company: string;
    email: string;
  };

  status: LeadStatus;

  brief: DiscoveryBrief;

  completedAt: string;
  createdAt: string;
  updatedAt: string;
}


const STORE_NAME =
  "ra-discovery-completed-leads";


function store() {
  return getStore({
    name: STORE_NAME,
    consistency: "strong",
  });
}


function readState(
  state: Record<string, unknown>,
  key: string,
): unknown {
  return state[key] ?? null;
}


function buildBrief(
  state: Record<string, unknown>,
): DiscoveryBrief {
  return {
    primaryProblem:
      readState(state, "primary_problem"),

    currentProcess:
      readState(state, "current_process"),

    currentSystems:
      readState(state, "current_systems"),

    painPoints:
      readState(state, "pain_points"),

    desiredOutcomes:
      readState(state, "desired_outcomes"),

    businessImpact:
      readState(state, "business_impact"),

    urgency:
      readState(state, "urgency"),

    timeline:
      readState(state, "timeline"),

    serviceCategory:
      readState(state, "service_category"),

    integrationsNeeded:
      readState(
        state,
        "integrations_needed",
      ),

    requirements:
      readState(state, "requirements"),

    decisionProcess:
      readState(state, "decision_process"),

    missingInformation:
      readState(
        state,
        "missing_information",
      ),

    qualificationScore:
      readState(
        state,
        "qualification_score",
      ),
  };
}


export async function createCompletedLead(
  session: RaSession,
): Promise<CompletedLead> {
  const leadStore = store();

  const existing =
    await leadStore.get(
      session.id,
      {
        type: "json",
        consistency: "strong",
      },
    ) as CompletedLead | null;

  if (existing) {
    return existing;
  }

  const now =
    new Date().toISOString();

  const lead: CompletedLead = {
    id: randomUUID(),
    sessionId: session.id,

    contact: {
      ...session.contact,
    },

    status: "awaiting_review",

    brief: buildBrief(
      session.currentState,
    ),

    completedAt: now,
    createdAt: now,
    updatedAt: now,
  };

  await leadStore.setJSON(
    session.id,
    lead,
    {
      onlyIfNew: true,
    },
  );

  return lead;
}
