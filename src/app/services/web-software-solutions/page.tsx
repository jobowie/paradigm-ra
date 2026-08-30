import type { Metadata } from "next";
import {
  ServicePage,
  type ServicePageContent,
} from "@/components/ServicePage";

export const metadata: Metadata = {
  title: "Web & Software Solutions | Paradigm Ra",
  description:
    "Paradigm Ra designs and builds websites, internal tools, software applications, and digital systems around real business requirements.",
  alternates: {
    canonical: "/services/web-software-solutions",
  },
};

const content: ServicePageContent = {
  kicker: "WEB + SOFTWARE SOLUTIONS",

  title: "Software should fit the business — not force the business to fit the software.",

  lede:
    "Paradigm Ra designs websites, internal tools, software applications, and connected digital systems around the way a business actually operates. We focus on clear requirements, maintainable architecture, usable interfaces, and technology that earns its place in the workflow.",

  principleTitle:
    "Start with the requirement. Choose the technology second.",

  principleBody:
    "A website, portal, dashboard, internal application, or custom software system should exist because it solves a defined business problem. We begin by understanding the people, process, data, constraints, and desired outcome before deciding what should be built.",

  capabilities: [
    {
      title: "Business Websites",
      description:
        "Design and develop responsive, professional websites that communicate clearly, support customer action, and reflect the actual business.",
    },
    {
      title: "Custom Software",
      description:
        "Build focused applications and tools when generic platforms cannot adequately support the requirement.",
    },
    {
      title: "Internal Tools",
      description:
        "Create dashboards, operational interfaces, portals, and utilities that make recurring business work easier to manage.",
    },
    {
      title: "Frontend Experiences",
      description:
        "Develop responsive user interfaces with clear hierarchy, purposeful interaction, and strong usability across devices.",
    },
    {
      title: "Backend + Data Systems",
      description:
        "Design APIs, data flows, application logic, integrations, and supporting services behind the user experience.",
    },
    {
      title: "Modernization + Improvement",
      description:
        "Improve existing websites and software by addressing usability, performance, architecture, workflow, or integration problems.",
    },
  ],

  exampleTitle: "From business requirement to working system.",

  exampleBody:
    "A company may need customers to submit information, employees to review it, data to be validated and stored, notifications to be triggered, and management to see current status. Instead of assembling disconnected tools, the solution can be designed as one coherent operating experience.",

  exampleFlow: [
    "Requirement",
    "Experience design",
    "Application logic",
    "Data",
    "Integration",
    "Deployment",
  ],

  fitTitle: "For businesses that need technology built around a real requirement.",

  fitBody:
    "This service is designed for businesses launching or improving a digital presence, replacing spreadsheet-heavy processes, creating internal tools, connecting frontend and backend systems, modernizing aging applications, or reaching the point where an off-the-shelf product no longer fits the operation.",

  steps: [
    {
      label: "DISCOVERY",
      title: "Understand",
      description:
        "Define the business requirement, users, desired outcome, existing environment, and constraints.",
    },
    {
      label: "ARCHITECTURE",
      title: "Design",
      description:
        "Determine the experience, data flow, application structure, integrations, and technical boundaries.",
    },
    {
      label: "BUILD",
      title: "Implement",
      description:
        "Develop the system incrementally with clear contracts, testing, and visible progress.",
    },
    {
      label: "DELIVERY",
      title: "Launch",
      description:
        "Validate the production experience, deploy the solution, document the system, and support the transition.",
    },
  ],
};

export default function WebSoftwareSolutionsPage() {
  return <ServicePage content={content} />;
}
