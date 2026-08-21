import type {
  DiscoveryAgentResponse,
  DiscoveryContact,
  DiscoveryState,
} from "../types";

export interface DiscoveryMessage {
  role: "prospect" | "agent";
  content: string;
}

export interface DiscoveryTurnInput {
  contact: DiscoveryContact;
  history: DiscoveryMessage[];
  latestProspectMessage: string;
  currentState: Partial<DiscoveryState>;
}

export interface DiscoveryProviderResult {
  provider: string;
  model: string;
  response: DiscoveryAgentResponse;
  latencyMs: number;
  inputTokens?: number;
  outputTokens?: number;
  estimatedCostUsd?: number;
}

export interface DiscoveryProvider {
  readonly provider: string;
  readonly model: string;

  discover(
    input: DiscoveryTurnInput,
  ): Promise<DiscoveryProviderResult>;
}
