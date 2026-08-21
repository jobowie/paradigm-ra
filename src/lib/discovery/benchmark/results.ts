import type {
  DiscoveryAgentResponse,
} from "../types";

export interface AutomaticScore {
  businessUnderstanding: number;
  discoveryEfficiency: number;
  stateAccuracy: number;
  latency: number;
  cost: number;

  total: number;
  maxScore: 60;

  notes: string[];
}

export interface HumanScore {
  nextQuestionQuality: number | null;
  consultativeTone: number | null;
  experienceContinuity: number | null;

  total: number | null;
  maxScore: 40;
}

export interface BenchmarkCaseResult {
  scenarioId: string;
  scenarioTitle: string;

  provider: string;
  model: string;

  response: DiscoveryAgentResponse | null;

  latencyMs: number | null;
  estimatedCostUsd: number | null;

  automaticScore: AutomaticScore | null;
  humanScore: HumanScore;

  finalScore: number | null;

  error?: string;
}

export interface BenchmarkRunResult {
  provider: string;
  model: string;

  startedAt: string;
  completedAt: string;

  cases: BenchmarkCaseResult[];

  automaticAverage: number;
  reviewedAverage: number | null;
}
