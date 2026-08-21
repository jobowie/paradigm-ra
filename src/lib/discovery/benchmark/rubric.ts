export const discoveryBenchmarkRubric = {
  businessUnderstanding: {
    weight: 20,
    description:
      "Understands the actual business problem instead of jumping to technology.",
  },

  nextQuestionQuality: {
    weight: 20,
    description:
      "Asks the single most valuable next question for discovery.",
  },

  discoveryEfficiency: {
    weight: 20,
    description:
      "Avoids repeated, irrelevant, excessive, or multi-part questioning.",
  },

  stateAccuracy: {
    weight: 15,
    description:
      "Correctly extracts and preserves known business facts.",
  },

  consultativeTone: {
    weight: 10,
    description:
      "Feels concise, capable, natural, and professional rather than bot-like.",
  },

  experienceContinuity: {
    weight: 10,
    description:
      "Clearly builds on what the prospect has already said.",
  },

  latency: {
    weight: 3,
    description:
      "Responds quickly enough to preserve a premium interactive experience.",
  },

  cost: {
    weight: 2,
    description:
      "Produces the result at sustainable inference cost.",
  },
} as const;

export const DISCOVERY_BENCHMARK_MAX_SCORE = 100;
