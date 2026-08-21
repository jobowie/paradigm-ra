import type {
  DiscoveryContact,
  DiscoveryNextStep,
  DiscoveryService,
  DiscoveryStage,
  DiscoveryState,
} from "../types";

import type {
  DiscoveryMessage,
} from "../providers/provider";

export interface BenchmarkExpectation {
  serviceCategory: DiscoveryService;
  complete: boolean;
  recommendedNextStep?: DiscoveryNextStep;

  mustCapture: Array<keyof DiscoveryState>;

  preferredQuestionTopics: string[];
  avoidQuestionTopics: string[];

  notes: string;
}

export interface DiscoveryBenchmarkScenario {
  id: string;
  title: string;
  stage: DiscoveryStage;

  contact: DiscoveryContact;

  history: DiscoveryMessage[];
  latestProspectMessage: string;

  currentState: Partial<DiscoveryState>;

  expected: BenchmarkExpectation;
}
