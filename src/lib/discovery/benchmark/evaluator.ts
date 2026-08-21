import type {
  DiscoveryState,
} from "../types";

import type {
  DiscoveryProviderResult,
} from "../providers/provider";

import type {
  DiscoveryBenchmarkScenario,
} from "./types";

import type {
  AutomaticScore,
} from "./results";

const STOPWORDS = new Set([
  "the",
  "and",
  "for",
  "with",
  "that",
  "this",
  "their",
  "what",
  "from",
  "into",
  "immediately",
  "again",
  "asking",
  "full",
  "one",
]);

function normalize(value: string): string {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function fieldIsCaptured(
  state: DiscoveryState,
  field: keyof DiscoveryState,
): boolean {
  const value = state[field];

  if (Array.isArray(value)) {
    return value.length > 0;
  }

  if (typeof value === "string") {
    return value.trim().length > 0;
  }

  if (typeof value === "number") {
    return Number.isFinite(value);
  }

  return value !== null && value !== undefined;
}

function topicTokens(topic: string): string[] {
  return normalize(topic)
    .split(" ")
    .filter(
      (token) =>
        token.length >= 3 &&
        !STOPWORDS.has(token),
    );
}

function mentionsTopic(
  text: string,
  topic: string,
): boolean {
  const normalizedText = normalize(text);
  const tokens = topicTokens(topic);

  if (tokens.length === 0) {
    return false;
  }

  const hits = tokens.filter((token) =>
    normalizedText.includes(token),
  ).length;

  return hits >= Math.max(
    1,
    Math.ceil(tokens.length * 0.5),
  );
}

function scoreBusinessUnderstanding(
  scenario: DiscoveryBenchmarkScenario,
  result: DiscoveryProviderResult,
  notes: string[],
): number {
  let score = 0;

  if (
    result.response.state.serviceCategory ===
    scenario.expected.serviceCategory
  ) {
    score += 10;
  } else {
    notes.push(
      `Service mismatch: expected ${scenario.expected.serviceCategory}, received ${result.response.state.serviceCategory}.`,
    );
  }

  const requiredFields =
    scenario.expected.mustCapture.filter(
      (field) => field !== "serviceCategory",
    );

  if (requiredFields.length === 0) {
    return score + 10;
  }

  const captured = requiredFields.filter(
    (field) =>
      fieldIsCaptured(
        result.response.state,
        field,
      ),
  ).length;

  score +=
    (captured / requiredFields.length) * 10;

  if (captured < requiredFields.length) {
    notes.push(
      `Captured ${captured}/${requiredFields.length} expected discovery fields.`,
    );
  }

  return score;
}

function scoreDiscoveryEfficiency(
  scenario: DiscoveryBenchmarkScenario,
  result: DiscoveryProviderResult,
  notes: string[],
): number {
  let score = 0;

  const reply = result.response.reply;
  const questionCount =
    (reply.match(/\?/g) ?? []).length;

  if (scenario.expected.complete) {
    if (questionCount === 0) {
      score += 10;
    } else {
      notes.push(
        `Expected discovery to stop, but response asked ${questionCount} question(s).`,
      );
    }
  } else if (questionCount <= 1) {
    score += 10;
  } else if (questionCount === 2) {
    score += 5;
    notes.push(
      "Response asked two questions; Paradigm preference is one primary question per turn.",
    );
  } else {
    notes.push(
      `Response asked ${questionCount} questions in one turn.`,
    );
  }

  const violations =
    scenario.expected.avoidQuestionTopics.filter(
      (topic) =>
        mentionsTopic(reply, topic),
    );

  if (violations.length === 0) {
    score += 10;
  } else if (violations.length === 1) {
    score += 5;
    notes.push(
      `Potential unnecessary topic: ${violations[0]}.`,
    );
  } else {
    notes.push(
      `Multiple unnecessary topics detected: ${violations.join(", ")}.`,
    );
  }

  return score;
}

function valuesPreserved(
  expected: unknown,
  actual: unknown,
): boolean {
  if (Array.isArray(expected)) {
    if (!Array.isArray(actual)) {
      return false;
    }

    const normalizedActual =
      actual.map((item) =>
        typeof item === "string"
          ? normalize(item)
          : item,
      );

    return expected.every((item) => {
      const normalizedExpected =
        typeof item === "string"
          ? normalize(item)
          : item;

      return normalizedActual.includes(
        normalizedExpected,
      );
    });
  }

  if (
    typeof expected === "string" &&
    typeof actual === "string"
  ) {
    const a = normalize(expected);
    const b = normalize(actual);

    return a === b || a.includes(b) || b.includes(a);
  }

  return expected === actual;
}

function scoreStateAccuracy(
  scenario: DiscoveryBenchmarkScenario,
  result: DiscoveryProviderResult,
  notes: string[],
): number {
  let score = 0;

  if (
    result.response.complete ===
    scenario.expected.complete
  ) {
    score += 5;
  } else {
    notes.push(
      `Completion mismatch: expected ${scenario.expected.complete}, received ${result.response.complete}.`,
    );
  }

  if (
    scenario.expected.recommendedNextStep
  ) {
    if (
      result.response.recommendedNextStep ===
      scenario.expected.recommendedNextStep
    ) {
      score += 5;
    } else {
      notes.push(
        `Next-step mismatch: expected ${scenario.expected.recommendedNextStep}, received ${result.response.recommendedNextStep}.`,
      );
    }
  } else {
    score += 5;
  }

  const knownEntries =
    Object.entries(scenario.currentState);

  if (knownEntries.length === 0) {
    score += 5;
    return score;
  }

  const outputState =
    result.response.state as unknown as Record<
      string,
      unknown
    >;

  const preserved = knownEntries.filter(
    ([key, value]) =>
      valuesPreserved(
        value,
        outputState[key],
      ),
  ).length;

  score +=
    (preserved / knownEntries.length) * 5;

  if (preserved < knownEntries.length) {
    notes.push(
      `Preserved ${preserved}/${knownEntries.length} previously established state fields.`,
    );
  }

  return score;
}

function scoreLatency(
  latencyMs: number,
): number {
  if (latencyMs <= 2500) return 3;
  if (latencyMs <= 5000) return 2;
  if (latencyMs <= 8000) return 1;

  return 0;
}

function scoreCost(
  estimatedCostUsd?: number,
): number {
  if (
    estimatedCostUsd === undefined ||
    estimatedCostUsd === null
  ) {
    return 0;
  }

  if (estimatedCostUsd <= 0.01) return 2;
  if (estimatedCostUsd <= 0.03) return 1.5;
  if (estimatedCostUsd <= 0.10) return 1;

  return 0.5;
}

export function evaluateAutomatically(
  scenario: DiscoveryBenchmarkScenario,
  result: DiscoveryProviderResult,
): AutomaticScore {
  const notes: string[] = [];

  const businessUnderstanding =
    scoreBusinessUnderstanding(
      scenario,
      result,
      notes,
    );

  const discoveryEfficiency =
    scoreDiscoveryEfficiency(
      scenario,
      result,
      notes,
    );

  const stateAccuracy =
    scoreStateAccuracy(
      scenario,
      result,
      notes,
    );

  const latency = scoreLatency(
    result.latencyMs,
  );

  const cost = scoreCost(
    result.estimatedCostUsd,
  );

  const total =
    businessUnderstanding +
    discoveryEfficiency +
    stateAccuracy +
    latency +
    cost;

  return {
    businessUnderstanding,
    discoveryEfficiency,
    stateAccuracy,
    latency,
    cost,
    total,
    maxScore: 60,
    notes,
  };
}
