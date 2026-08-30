import type { Metadata } from "next";
import {
  ServicePage,
  type ServicePageContent,
} from "@/components/ServicePage";

export const metadata: Metadata = {
  title: "Accounting & Operational Solutions | Paradigm Ra",
  description:
    "Paradigm Ra helps businesses improve bookkeeping, financial workflows, reporting, accounting systems, and the operational processes surrounding financial data.",
  alternates: {
    canonical: "/services/accounting-operational-solutions",
  },
};

const content: ServicePageContent = {
  kicker: "ACCOUNTING + OPERATIONAL SOLUTIONS",

  title: "Financial clarity begins with reliable operating systems.",

  lede:
    "Books, reporting, payments, reconciliations, expenses, and financial decisions all depend on information moving correctly through the business. Paradigm Ra helps improve both the accounting work itself and the systems and processes surrounding it.",

  principleTitle:
    "Accounting is more useful when the operation behind the numbers is clear.",

  principleBody:
    "Financial problems are not always accounting problems. Duplicate entry, inconsistent categorization, disconnected software, missing documentation, manual handoffs, and unclear processes can all affect the quality of financial information. We look at the books and the operating system producing them.",

  capabilities: [
    {
      title: "Bookkeeping Support",
      description:
        "Organize and maintain financial records so the business has a clearer and more reliable view of activity.",
    },
    {
      title: "Reconciliation + Cleanup",
      description:
        "Identify inconsistencies, reconcile accounts, address historical issues, and improve the reliability of financial records.",
    },
    {
      title: "Accounting Workflow Design",
      description:
        "Improve how transactions, receipts, approvals, expenses, invoices, payments, and supporting information move through the business.",
    },
    {
      title: "Financial Reporting",
      description:
        "Structure recurring reporting around information owners can actually use to understand performance and make decisions.",
    },
    {
      title: "Accounting Systems Integration",
      description:
        "Connect accounting platforms with operational systems to reduce duplicate work and improve consistency between business and financial data.",
    },
    {
      title: "Operational Financial Support",
      description:
        "Improve the processes surrounding billing, expenses, documentation, categorization, data entry, and recurring financial administration.",
    },
  ],

  exampleTitle: "From scattered financial activity to a repeatable operating process.",

  exampleBody:
    "A business may receive expenses through email, track approvals manually, enter transactions later, reconcile information from multiple sources, and build reports by hand. Improving the accounting system may mean improving how the information reaches accounting in the first place.",

  exampleFlow: [
    "Transaction",
    "Documentation",
    "Classification",
    "Accounting system",
    "Reconciliation",
    "Reporting",
  ],

  fitTitle: "For businesses that want more confidence in the numbers and the process behind them.",

  fitBody:
    "This service is designed for businesses dealing with inconsistent books, manual financial workflows, unclear reporting, disconnected accounting software, reconciliation problems, growing transaction volume, recurring administrative work, or owners who need stronger financial visibility without adding unnecessary complexity.",

  steps: [
    {
      label: "DISCOVERY",
      title: "Understand",
      description:
        "Review the financial workflow, current systems, reporting needs, responsibilities, and areas creating uncertainty.",
    },
    {
      label: "ASSESSMENT",
      title: "Review",
      description:
        "Evaluate records, processes, system connections, handoffs, documentation, and recurring financial tasks.",
    },
    {
      label: "STRUCTURE",
      title: "Improve",
      description:
        "Create clearer accounting practices, workflows, reporting structures, and supporting system improvements.",
    },
    {
      label: "OPERATIONS",
      title: "Maintain",
      description:
        "Support the recurring process with bookkeeping, reconciliation, reporting, implementation, or ongoing operational assistance.",
    },
  ],
};

export default function AccountingOperationalSolutionsPage() {
  return <ServicePage content={content} />;
}
