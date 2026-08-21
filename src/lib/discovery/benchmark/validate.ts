import {
  discoveryBenchmarkRubric,
} from "./rubric";

import {
  discoveryBenchmarkScenarios,
} from "./scenarios";

import {
  getFollowUpLimit,
} from "../policies/followUp";

function assert(
  condition: boolean,
  message: string,
): void {
  if (!condition) {
    throw new Error(message);
  }
}

const totalWeight =
  Object.values(
    discoveryBenchmarkRubric,
  ).reduce(
    (total, item) =>
      total + item.weight,
    0,
  );

assert(
  totalWeight === 100,
  `Rubric must total 100. Current total: ${totalWeight}`,
);

const ids =
  discoveryBenchmarkScenarios.map(
    (scenario) => scenario.id,
  );

assert(
  new Set(ids).size === ids.length,
  "Benchmark scenario IDs must be unique.",
);

assert(
  discoveryBenchmarkScenarios.length >= 10,
  "Benchmark should contain at least 10 initial scenarios.",
);

assert(
  getFollowUpLimit(0) === 0,
  "0 answered questions should produce 0 follow-ups.",
);

assert(
  getFollowUpLimit(1) === 1,
  "1 answered question should produce 1 follow-up.",
);

assert(
  getFollowUpLimit(2) === 1,
  "2 answered questions should produce 1 follow-up.",
);

assert(
  getFollowUpLimit(3) === 2,
  "3 answered questions should produce 2 follow-ups.",
);

assert(
  getFollowUpLimit(5) === 2,
  "5 answered questions should produce 2 follow-ups.",
);

assert(
  getFollowUpLimit(10) === 2,
  "Follow-ups must never exceed 2.",
);

console.log("");
console.log("RA DISCOVERY BENCHMARK");
console.log("----------------------");
console.log(
  `Scenarios: ${discoveryBenchmarkScenarios.length}`,
);
console.log(
  `Rubric weight: ${totalWeight}/100`,
);
console.log(
  "Automatic scoring: 60 points",
);
console.log(
  "Blinded human review: 40 points",
);
console.log(
  "Follow-up policy: validated",
);
console.log("");
console.log(
  "Benchmark integrity check: PASS ✓",
);
console.log("");
