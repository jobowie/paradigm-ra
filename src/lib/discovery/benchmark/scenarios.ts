import type {
  DiscoveryBenchmarkScenario,
} from "./types";

export const discoveryBenchmarkScenarios: DiscoveryBenchmarkScenario[] = [
  {
    id: "web-001",
    title: "Outdated Safety Supply Website",
    stage: "problem",

    contact: {
      firstName: "Marcus",
      company: "Apex Safety Supply",
      email: "marcus@example.com",
    },

    history: [],

    latestProspectMessage:
      "Our website is outdated and customers have trouble figuring out what products we carry. Most people end up calling us.",

    currentState: {},

    expected: {
      serviceCategory: "web",
      complete: false,

      mustCapture: [
        "primaryProblem",
        "painPoints",
        "serviceCategory",
      ],

      preferredQuestionTopics: [
        "current customer journey",
        "product catalog",
        "desired website outcome",
      ],

      avoidQuestionTopics: [
        "budget immediately",
        "API architecture",
        "database technology",
      ],

      notes:
        "The agent should recognize a web opportunity without overengineering the conversation.",
    },
  },

  {
    id: "automation-001",
    title: "Phone Orders Into QuickBooks",
    stage: "current_process",

    contact: {
      firstName: "Dana",
      company: "Westline Industrial",
      email: "dana@example.com",
    },

    history: [],

    latestProspectMessage:
      "Customers call in orders, our staff writes everything down, and somebody enters the same order into QuickBooks afterward. We want to cut down on all that manual work.",

    currentState: {},

    expected: {
      serviceCategory: "mixed",
      complete: false,

      mustCapture: [
        "primaryProblem",
        "currentProcess",
        "currentSystems",
        "painPoints",
        "desiredOutcomes",
      ],

      preferredQuestionTopics: [
        "order volume",
        "QuickBooks version",
        "where orders originate",
      ],

      avoidQuestionTopics: [
        "website colors",
        "marketing strategy",
        "repeat description of current process",
      ],

      notes:
        "Should identify automation/integration potential without immediately prescribing a solution.",
    },
  },

  {
    id: "software-001",
    title: "Legacy SQL Application",
    stage: "systems",

    contact: {
      firstName: "Priya",
      company: "Northstar Logistics",
      email: "priya@example.com",
    },

    history: [],

    latestProspectMessage:
      "We have an internal application that's about 12 years old. It talks to SQL Server and several departments depend on it every day. We need to modernize it without disrupting operations.",

    currentState: {},

    expected: {
      serviceCategory: "custom_software",
      complete: false,

      mustCapture: [
        "primaryProblem",
        "currentSystems",
        "usersOrTeamsAffected",
        "requirements",
      ],

      preferredQuestionTopics: [
        "critical workflows",
        "current application responsibilities",
        "operational dependencies",
      ],

      avoidQuestionTopics: [
        "rewrite language recommendation",
        "cloud provider recommendation",
        "budget immediately",
      ],

      notes:
        "Tests whether the model discovers system responsibilities before prescribing a rewrite.",
    },
  },

  {
    id: "accounting-001",
    title: "Month-End Spreadsheet Consolidation",
    stage: "current_process",

    contact: {
      firstName: "Nicole",
      company: "Beacon Services Group",
      email: "nicole@example.com",
    },

    history: [],

    latestProspectMessage:
      "Each location sends accounting a spreadsheet at month end. Accounting combines them manually before entering totals into our accounting system.",

    currentState: {},

    expected: {
      serviceCategory: "mixed",
      complete: false,

      mustCapture: [
        "currentProcess",
        "painPoints",
        "usersOrTeamsAffected",
      ],

      preferredQuestionTopics: [
        "accounting system",
        "number of locations",
        "spreadsheet consistency",
      ],

      avoidQuestionTopics: [
        "website redesign",
        "branding",
        "unrelated CRM questions",
      ],

      notes:
        "Should recognize accounting-process automation and integration potential.",
    },
  },

  {
    id: "efficiency-001",
    title: "Do Not Repeat the Timeline Question",
    stage: "impact",

    contact: {
      firstName: "Chris",
      company: "Summit Fabrication",
      email: "chris@example.com",
    },

    history: [
      {
        role: "agent",
        content:
          "What would you most like to improve?",
      },
      {
        role: "prospect",
        content:
          "Our quoting process takes too long.",
      },
      {
        role: "agent",
        content:
          "Is there a particular timeline you're working toward?",
      },
      {
        role: "prospect",
        content:
          "Yes, we'd like something in place before January.",
      },
    ],

    latestProspectMessage:
      "Right now sales emails job details to estimating, then estimating builds every quote manually in Excel.",

    currentState: {
      primaryProblem:
        "The quoting process takes too long.",
      timeline:
        "Before January.",
      currentSystems: ["Email", "Excel"],
    },

    expected: {
      serviceCategory: "automation",
      complete: false,

      mustCapture: [
        "currentProcess",
        "currentSystems",
        "timeline",
      ],

      preferredQuestionTopics: [
        "quote volume",
        "manual estimating steps",
        "business impact",
      ],

      avoidQuestionTopics: [
        "timeline",
        "asking what the problem is again",
      ],

      notes:
        "Explicitly tests memory and whether the model avoids asking for known information.",
    },
  },

  {
    id: "efficiency-002",
    title: "Rich First Answer",
    stage: "scope",

    contact: {
      firstName: "Alex",
      company: "Metro Distribution",
      email: "alex@example.com",
    },

    history: [],

    latestProspectMessage:
      "We have four locations. Customers place orders by phone or email, employees enter them into QuickBooks Enterprise, and inventory gets updated manually. We process around 150 orders a day. We want customers to order online and have those orders flow into our existing systems. We'd like to start this quarter.",

    currentState: {},

    expected: {
      serviceCategory: "mixed",
      complete: false,

      mustCapture: [
        "currentProcess",
        "currentSystems",
        "desiredOutcomes",
        "integrationsNeeded",
        "timeline",
        "painPoints",
      ],

      preferredQuestionTopics: [
        "inventory system",
        "critical integration details",
        "desired customer ordering experience",
      ],

      avoidQuestionTopics: [
        "number of locations",
        "order volume",
        "timeline",
        "asking what they want to accomplish",
      ],

      notes:
        "Tests whether a model can extract several facts from one answer instead of asking for them again.",
    },
  },

  {
    id: "completion-001",
    title: "Know When to Stop",
    stage: "decision_process",

    contact: {
      firstName: "Taylor",
      company: "Crestview Manufacturing",
      email: "taylor@example.com",
    },

    history: [],

    latestProspectMessage:
      "We want to replace a manual production reporting process. Supervisors currently fill out spreadsheets, operations consolidates them every morning, and leadership doesn't see yesterday's numbers until noon. About 40 supervisors are involved. We use Microsoft 365 and SQL Server. We'd like near-real-time reporting, ideally within the next three months. I'm leading the project and our COO will approve the final budget.",

    currentState: {},

    expected: {
      serviceCategory: "mixed",
      complete: true,
      recommendedNextStep: "book_discovery_call",

      mustCapture: [
        "primaryProblem",
        "currentProcess",
        "currentSystems",
        "usersOrTeamsAffected",
        "businessImpact",
        "desiredOutcomes",
        "timeline",
        "decisionProcess",
      ],

      preferredQuestionTopics: [],

      avoidQuestionTopics: [
        "additional unnecessary discovery",
        "budget interrogation",
        "repeating known information",
      ],

      notes:
        "The model should recognize that enough exists for a productive human discovery call.",
    },
  },

  {
    id: "fit-001",
    title: "Clearly Outside Core Services",
    stage: "problem",

    contact: {
      firstName: "Jordan",
      company: "Jordan Lane Photography",
      email: "jordan@example.com",
    },

    history: [],

    latestProspectMessage:
      "I'm looking for someone to design a new logo and create illustrations for a children's book. I don't need a website or software.",

    currentState: {},

    expected: {
      serviceCategory: "unknown",
      complete: true,
      recommendedNextStep: "not_a_fit",

      mustCapture: [
        "primaryProblem",
        "serviceCategory",
      ],

      preferredQuestionTopics: [],

      avoidQuestionTopics: [
        "forcing a website sale",
        "inventing software needs",
      ],

      notes:
        "Tests whether the model can respectfully avoid forcing an irrelevant Paradigm Ra engagement.",
    },
  },

  {
    id: "integration-001",
    title: "System Integration Without Enough Context",
    stage: "systems",

    contact: {
      firstName: "Morgan",
      company: "Evergreen Health Products",
      email: "morgan@example.com",
    },

    history: [],

    latestProspectMessage:
      "We need our CRM and accounting platform to communicate with each other because people are entering the same customer information twice.",

    currentState: {},

    expected: {
      serviceCategory: "integrations",
      complete: false,

      mustCapture: [
        "primaryProblem",
        "painPoints",
        "desiredOutcomes",
        "serviceCategory",
      ],

      preferredQuestionTopics: [
        "CRM name",
        "accounting platform name",
        "data that needs synchronization",
      ],

      avoidQuestionTopics: [
        "programming language",
        "hosting architecture",
      ],

      notes:
        "The correct response is targeted clarification, not premature technical architecture.",
    },
  },

  {
    id: "advisory-001",
    title: "We Know Something Is Broken",
    stage: "problem",

    contact: {
      firstName: "Renee",
      company: "Harbor Property Group",
      email: "renee@example.com",
    },

    history: [],

    latestProspectMessage:
      "We've grown pretty fast and our systems are a mess. Different teams use different tools and we're not even sure what should be replaced versus connected.",

    currentState: {},

    expected: {
      serviceCategory: "advisory",
      complete: false,

      mustCapture: [
        "primaryProblem",
        "painPoints",
        "serviceCategory",
      ],

      preferredQuestionTopics: [
        "most painful workflow",
        "teams affected",
        "current systems",
      ],

      avoidQuestionTopics: [
        "immediate product recommendation",
        "full technical inventory in one question",
        "budget immediately",
      ],

      notes:
        "Tests consultative discovery when the client cannot yet articulate the solution.",
    },
  },
];
