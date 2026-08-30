import type { Metadata } from "next";
import {
  ServicePage,
  type ServicePageContent,
} from "@/components/ServicePage";

export const metadata: Metadata = {
  title: "Business Systems & Technical Consulting | Paradigm Ra",
  description:
    "Paradigm Ra helps businesses evaluate systems, solve technical problems, improve implementation, and make clearer technology decisions.",
  alternates: {
    canonical: "/services/business-systems-technical-consulting",
  },
};

const content: ServicePageContent = {
  kicker: "BUSINESS SYSTEMS + TECHNICAL CONSULTING",

  title: "Make the system understandable before making the decision.",

  lede:
    "Technology decisions become expensive when requirements are unclear, systems are disconnected, ownership is ambiguous, or implementation begins before the problem is understood. Paradigm Ra helps businesses evaluate the operating environment, identify what is actually happening, and turn complexity into an actionable technical plan.",

  principleTitle:
    "Good consulting creates clarity before it creates activity.",

  principleBody:
    "Not every technical problem requires new software. Sometimes the issue is architecture, implementation, process ownership, configuration, data flow, documentation, or simply a mismatch between the business requirement and the current system. We help determine which problem is actually being solved before recommending the next move.",

  capabilities: [
    {
      title: "Systems Assessment",
      description:
        "Review the current technical environment, workflows, dependencies, constraints, and points of failure.",
    },
    {
      title: "Technical Strategy",
      description:
        "Translate business needs into practical technology priorities, architecture decisions, and implementation plans.",
    },
    {
      title: "Implementation Consulting",
      description:
        "Support software rollouts, configuration decisions, testing, integration planning, stakeholder alignment, and operational readiness.",
    },
    {
      title: "Architecture + Integration Review",
      description:
        "Evaluate how systems communicate, where responsibilities belong, and where coupling or fragile dependencies create risk.",
    },
    {
      title: "Troubleshooting + Root Cause Analysis",
      description:
        "Trace technical and operational failures through the system instead of treating surface symptoms as the root problem.",
    },
    {
      title: "Vendor + Platform Evaluation",
      description:
        "Compare technology choices against actual requirements rather than feature lists or sales presentations.",
    },
  ],

  exampleTitle: "From technical uncertainty to a decision you can explain.",

  exampleBody:
    "A business may know its current platform is creating friction but not know whether the answer is replacement, integration, configuration, process change, or custom development. We map the requirement against the current environment so the next investment has a defined reason behind it.",

  exampleFlow: [
    "Business need",
    "Current state",
    "Constraints",
    "Root cause",
    "Recommendation",
    "Execution plan",
  ],

  fitTitle: "For businesses facing a technical decision without enough clarity.",

  fitBody:
    "This service is designed for teams evaluating new platforms, struggling with implementations, dealing with recurring system failures, planning integrations, replacing legacy processes, preparing a technical project, or needing an experienced technical perspective before committing budget and resources.",

  steps: [
    {
      label: "DISCOVERY",
      title: "Understand",
      description:
        "Establish the business objective, technical environment, symptoms, stakeholders, and decision that needs to be made.",
    },
    {
      label: "ANALYSIS",
      title: "Trace",
      description:
        "Follow the process, systems, data, dependencies, and failure boundaries to identify the actual issue.",
    },
    {
      label: "DIRECTION",
      title: "Recommend",
      description:
        "Present a practical path forward with priorities, tradeoffs, technical considerations, and implementation implications.",
    },
    {
      label: "EXECUTION",
      title: "Support",
      description:
        "Help translate the recommendation into implementation, vendor coordination, testing, documentation, or delivery.",
    },
  ],
};

export default function BusinessSystemsTechnicalConsultingPage() {
  return <ServicePage content={content} />;
}
