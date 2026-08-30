import type { Metadata } from "next";
import {
  ServicePage,
  type ServicePageContent,
} from "@/components/ServicePage";

export const metadata: Metadata = {
  title: "Business Automation & Integration | Paradigm Ra",
  description:
    "Paradigm Ra helps businesses reduce manual work, connect disconnected systems, and design practical automation around the way their operation actually works.",
  alternates: {
    canonical: "/services/business-automation",
  },
};

const content: ServicePageContent = {
  kicker: "BUSINESS AUTOMATION + INTEGRATION",

  title: "Make the work flow better. Then automate what earns it.",

  lede:
    "Manual handoffs, repetitive data entry, disconnected systems, and processes built around workarounds quietly consume time. Paradigm Ra helps businesses understand how work moves today, identify where friction occurs, and design practical automation around the actual operation.",

  principleTitle:
    "Automation should solve a business problem — not create another system to manage.",

  principleBody:
    "Many businesses know something in their workflow is inefficient but are not sure whether the answer is automation, integration, new software, process redesign, or simply removing unnecessary steps. We start with the process. Only after the operation is understood do we determine what technology belongs in the solution.",

  capabilities: [
    {
      title: "Workflow Automation",
      description:
        "Reduce repetitive manual tasks and create reliable flows between people, data, and systems.",
    },
    {
      title: "Systems Integration",
      description:
        "Connect applications, APIs, databases, forms, CRMs, accounting platforms, internal tools, and other business systems.",
    },
    {
      title: "Process Mapping + Optimization",
      description:
        "Understand the current workflow from start to finish, identify bottlenecks, and determine what should change before implementation begins.",
    },
    {
      title: "Data Movement + Synchronization",
      description:
        "Reduce duplicate entry and inconsistent information by improving how data moves between systems.",
    },
    {
      title: "Operational Automation",
      description:
        "Automate notifications, approvals, follow-ups, reporting, status updates, document movement, and recurring operational work.",
    },
    {
      title: "Custom Automation",
      description:
        "When an off-the-shelf connector is not enough, design custom software or integration logic around the actual requirement.",
    },
  ],

  exampleTitle: "From disconnected steps to one operating flow.",

  exampleBody:
    "A business may receive information through a form, copy it into a spreadsheet, email another employee, enter it again into accounting software, and later assemble reporting manually. The right solution might connect those steps — but the architecture should follow the business rather than the other way around.",

  exampleFlow: [
    "Input",
    "Validation",
    "System of record",
    "Accounting integration",
    "Notifications",
    "Reporting",
  ],

  fitTitle: "For businesses that know something should work better.",

  fitBody:
    "This service is designed for growing businesses dealing with repetitive data entry, spreadsheet-heavy operations, disconnected software, duplicated work, slow handoffs, inconsistent reporting, manual processes that no longer scale, or teams that know there is friction but are not yet sure which technology will actually solve it.",

  steps: [
    {
      label: "DISCOVERY",
      title: "Understand",
      description:
        "Establish what the business is trying to accomplish and what is happening today.",
    },
    {
      label: "ASSESSMENT",
      title: "Map",
      description:
        "Review the workflow, systems, constraints, bottlenecks, dependencies, and existing workarounds.",
    },
    {
      label: "DESIGN",
      title: "Recommend",
      description:
        "Define the automation, integration, process, or software approach that best fits the operation.",
    },
    {
      label: "DELIVERY",
      title: "Implement",
      description:
        "Build, configure, integrate, test, and support the resulting solution once the architecture is clear.",
    },
  ],
};

export default function BusinessAutomationPage() {
  return <ServicePage content={content} />;
}
