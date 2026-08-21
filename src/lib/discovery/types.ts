export type DiscoveryService =
  | "web"
  | "automation"
  | "integrations"
  | "accounting_solutions"
  | "custom_software"
  | "advisory"
  | "mixed"
  | "unknown";

export type DiscoveryStage =
  | "problem"
  | "business_context"
  | "current_process"
  | "systems"
  | "impact"
  | "desired_outcome"
  | "scope"
  | "timeline"
  | "budget"
  | "decision_process"
  | "complete";

export type DiscoveryNextStep =
  | "continue_discovery"
  | "book_discovery_call"
  | "request_more_information"
  | "not_a_fit";

export interface DiscoveryContact {
  firstName: string;
  company: string;
  email: string;
  phone?: string | null;
}

export interface DiscoveryState {
  companyName: string | null;
  contactName: string | null;
  website: string | null;

  businessDescription: string | null;
  primaryProblem: string | null;
  currentProcess: string | null;

  currentSystems: string[];
  painPoints: string[];
  desiredOutcomes: string[];

  serviceCategory: DiscoveryService;

  usersOrTeamsAffected: string[];
  integrationsNeeded: string[];
  requirements: string[];

  businessImpact: string | null;
  urgency: string | null;
  timeline: string | null;
  budgetContext: string | null;
  decisionProcess: string | null;

  qualificationScore: number;
  missingInformation: string[];
}

export interface DiscoveryAgentResponse {
  reply: string;
  stage: DiscoveryStage;
  complete: boolean;
  recommendedNextStep: DiscoveryNextStep;
  state: DiscoveryState;
}
