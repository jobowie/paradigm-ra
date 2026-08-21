import type {
  DiscoveryProvider,
} from "../providers/provider";

import {
  discoveryBenchmarkScenarios,
} from "./scenarios";

import {
  evaluateAutomatically,
} from "./evaluator";

import type {
  BenchmarkCaseResult,
  BenchmarkRunResult,
} from "./results";

export async function runDiscoveryBenchmark(
  provider: DiscoveryProvider,
): Promise<BenchmarkRunResult> {
  const startedAt = new Date().toISOString();

  const cases: BenchmarkCaseResult[] = [];

  for (
    const scenario
    of discoveryBenchmarkScenarios
  ) {
    try {
      const result =
        await provider.discover({
          contact: scenario.contact,
          history: scenario.history,
          latestProspectMessage:
            scenario.latestProspectMessage,
          currentState:
            scenario.currentState,
        });

      const automaticScore =
        evaluateAutomatically(
          scenario,
          result,
        );

      cases.push({
        scenarioId: scenario.id,
        scenarioTitle: scenario.title,

        provider: result.provider,
        model: result.model,

        response: result.response,

        latencyMs: result.latencyMs,
        estimatedCostUsd:
          result.estimatedCostUsd ?? null,

        automaticScore,

        humanScore: {
          nextQuestionQuality: null,
          consultativeTone: null,
          experienceContinuity: null,
          total: null,
          maxScore: 40,
        },

        finalScore: null,
      });
    } catch (error) {
      cases.push({
        scenarioId: scenario.id,
        scenarioTitle: scenario.title,

        provider: provider.provider,
        model: provider.model,

        response: null,

        latencyMs: null,
        estimatedCostUsd: null,

        automaticScore: null,

        humanScore: {
          nextQuestionQuality: null,
          consultativeTone: null,
          experienceContinuity: null,
          total: null,
          maxScore: 40,
        },

        finalScore: null,

        error:
          error instanceof Error
            ? error.message
            : "Unknown benchmark error.",
      });
    }
  }

  const successful =
    cases.filter(
      (item) => item.automaticScore,
    );

  const automaticAverage =
    successful.length === 0
      ? 0
      : successful.reduce(
          (total, item) =>
            total +
            (item.automaticScore?.total ?? 0),
          0,
        ) / successful.length;

  return {
    provider: provider.provider,
    model: provider.model,

    startedAt,
    completedAt:
      new Date().toISOString(),

    cases,

    automaticAverage,
    reviewedAverage: null,
  };
}
