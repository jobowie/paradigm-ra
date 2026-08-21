from discovery.benchmark.models import (
    BenchmarkExpectation,
    DiscoveryBenchmarkScenario,
)
from discovery.models import DiscoveryContact, DiscoveryMessage


DISCOVERY_BENCHMARK_SCENARIOS = [
    DiscoveryBenchmarkScenario(
        id="web-001",
        title="Outdated Safety Supply Website",
        stage="problem",
        contact=DiscoveryContact(
            first_name="Marcus",
            company="Apex Safety Supply",
            email="marcus@example.com",
        ),
        history=[],
        latest_prospect_message=(
            "Our website is outdated and customers have trouble "
            "figuring out what products we carry. Most people end "
            "up calling us."
        ),
        current_state={},
        expected=BenchmarkExpectation(
            service_category="web",
            complete=False,
            must_capture=[
                "primary_problem",
                "pain_points",
                "service_category",
            ],
            preferred_question_topics=[
                "current customer journey",
                "product catalog",
                "desired website outcome",
            ],
            avoid_question_topics=[
                "budget immediately",
                "API architecture",
                "database technology",
            ],
            notes=(
                "Recognize a web opportunity without overengineering "
                "the conversation."
            ),
        ),
    ),

    DiscoveryBenchmarkScenario(
        id="automation-001",
        title="Phone Orders Into QuickBooks",
        stage="current_process",
        contact=DiscoveryContact(
            first_name="Dana",
            company="Westline Industrial",
            email="dana@example.com",
        ),
        history=[],
        latest_prospect_message=(
            "Customers call in orders, our staff writes everything "
            "down, and somebody enters the same order into QuickBooks "
            "afterward. We want to cut down on all that manual work."
        ),
        current_state={},
        expected=BenchmarkExpectation(
            service_category="mixed",
            acceptable_service_categories=["mixed", "automation"],
            complete=False,
            must_capture=[
                "primary_problem",
                "current_process",
                "current_systems",
                "pain_points",
                "desired_outcomes",
            ],
            preferred_question_topics=[
                "order volume",
                "QuickBooks version",
                "where orders originate",
            ],
            avoid_question_topics=[
                "website colors",
                "marketing strategy",
                "repeat description of current process",
            ],
            notes=(
                "Identify automation/integration potential without "
                "immediately prescribing a solution."
            ),
        ),
    ),

    DiscoveryBenchmarkScenario(
        id="software-001",
        title="Legacy SQL Application",
        stage="systems",
        contact=DiscoveryContact(
            first_name="Priya",
            company="Northstar Logistics",
            email="priya@example.com",
        ),
        history=[],
        latest_prospect_message=(
            "We have an internal application that's about 12 years "
            "old. It talks to SQL Server and several departments "
            "depend on it every day. We need to modernize it without "
            "disrupting operations."
        ),
        current_state={},
        expected=BenchmarkExpectation(
            service_category="custom_software",
            complete=False,
            must_capture=[
                "primary_problem",
                "current_systems",
                "users_or_teams_affected",
                "requirements",
            ],
            preferred_question_topics=[
                "critical workflows",
                "current application responsibilities",
                "operational dependencies",
            ],
            avoid_question_topics=[
                "rewrite language recommendation",
                "cloud provider recommendation",
                "budget immediately",
            ],
            notes=(
                "Discover system responsibilities before prescribing "
                "a rewrite."
            ),
        ),
    ),

    DiscoveryBenchmarkScenario(
        id="accounting-001",
        title="Month-End Spreadsheet Consolidation",
        stage="current_process",
        contact=DiscoveryContact(
            first_name="Nicole",
            company="Beacon Services Group",
            email="nicole@example.com",
        ),
        history=[],
        latest_prospect_message=(
            "Each location sends accounting a spreadsheet at month "
            "end. Accounting combines them manually before entering "
            "totals into our accounting system."
        ),
        current_state={},
        expected=BenchmarkExpectation(
            service_category="mixed",
            acceptable_service_categories=["mixed", "automation"],
            complete=False,
            must_capture=[
                "current_process",
                "pain_points",
                "users_or_teams_affected",
            ],
            preferred_question_topics=[
                "accounting system",
                "number of locations",
                "spreadsheet consistency",
            ],
            avoid_question_topics=[
                "website redesign",
                "branding",
                "unrelated CRM questions",
            ],
            notes=(
                "Recognize accounting-process automation and "
                "integration potential."
            ),
        ),
    ),

    DiscoveryBenchmarkScenario(
        id="efficiency-001",
        title="Do Not Repeat the Timeline Question",
        stage="impact",
        contact=DiscoveryContact(
            first_name="Chris",
            company="Summit Fabrication",
            email="chris@example.com",
        ),
        history=[
            DiscoveryMessage(
                role="agent",
                content="What would you most like to improve?",
            ),
            DiscoveryMessage(
                role="prospect",
                content="Our quoting process takes too long.",
            ),
            DiscoveryMessage(
                role="agent",
                content=(
                    "Is there a particular timeline you're working toward?"
                ),
            ),
            DiscoveryMessage(
                role="prospect",
                content=(
                    "Yes, we'd like something in place before January."
                ),
            ),
        ],
        latest_prospect_message=(
            "Right now sales emails job details to estimating, then "
            "estimating builds every quote manually in Excel."
        ),
        current_state={
            "primary_problem": "The quoting process takes too long.",
            "timeline": "Before January.",
            "current_systems": ["Email", "Excel"],
        },
        expected=BenchmarkExpectation(
            service_category="automation",
            complete=False,
            must_capture=[
                "current_process",
                "current_systems",
                "timeline",
            ],
            preferred_question_topics=[
                "quote volume",
                "manual estimating steps",
                "business impact",
            ],
            avoid_question_topics=[
                "timeline",
                "asking what the problem is again",
            ],
            notes=(
                "Test memory and whether the model avoids asking for "
                "known information."
            ),
        ),
    ),

    DiscoveryBenchmarkScenario(
        id="efficiency-002",
        title="Rich First Answer",
        stage="scope",
        contact=DiscoveryContact(
            first_name="Alex",
            company="Metro Distribution",
            email="alex@example.com",
        ),
        history=[],
        latest_prospect_message=(
            "We have four locations. Customers place orders by phone "
            "or email, employees enter them into QuickBooks Enterprise, "
            "and inventory gets updated manually. We process around "
            "150 orders a day. We want customers to order online and "
            "have those orders flow into our existing systems. We'd "
            "like to start this quarter."
        ),
        current_state={},
        expected=BenchmarkExpectation(
            service_category="mixed",
            complete=False,
            must_capture=[
                "current_process",
                "current_systems",
                "desired_outcomes",
                "integrations_needed",
                "timeline",
                "pain_points",
            ],
            preferred_question_topics=[
                "inventory system",
                "critical integration details",
                "desired customer ordering experience",
            ],
            avoid_question_topics=[
                "number of locations",
                "order volume",
                "timeline",
                "asking what they want to accomplish",
            ],
            notes=(
                "Extract multiple facts from one answer instead of "
                "asking for them again."
            ),
        ),
    ),

    DiscoveryBenchmarkScenario(
        id="completion-001",
        title="Know When to Stop",
        stage="decision_process",
        contact=DiscoveryContact(
            first_name="Taylor",
            company="Crestview Manufacturing",
            email="taylor@example.com",
        ),
        history=[],
        latest_prospect_message=(
            "We want to replace a manual production reporting process. "
            "Supervisors currently fill out spreadsheets, operations "
            "consolidates them every morning, and leadership doesn't "
            "see yesterday's numbers until noon. About 40 supervisors "
            "are involved. We use Microsoft 365 and SQL Server. We'd "
            "like near-real-time reporting, ideally within the next "
            "three months. I'm leading the project and our COO will "
            "approve the final budget."
        ),
        current_state={},
        expected=BenchmarkExpectation(
            service_category="mixed",
            complete=True,
            recommended_next_step="book_discovery_call",
            must_capture=[
                "primary_problem",
                "current_process",
                "current_systems",
                "users_or_teams_affected",
                "business_impact",
                "desired_outcomes",
                "timeline",
                "decision_process",
            ],
            preferred_question_topics=[],
            avoid_question_topics=[
                "additional unnecessary discovery",
                "budget interrogation",
                "repeating known information",
            ],
            notes=(
                "Recognize when enough information exists for a "
                "productive human discovery call."
            ),
        ),
    ),

    DiscoveryBenchmarkScenario(
        id="fit-001",
        title="Clearly Outside Core Services",
        stage="problem",
        contact=DiscoveryContact(
            first_name="Jordan",
            company="Jordan Lane Photography",
            email="jordan@example.com",
        ),
        history=[],
        latest_prospect_message=(
            "I'm looking for someone to design a new logo and create "
            "illustrations for a children's book. I don't need a "
            "website or software."
        ),
        current_state={},
        expected=BenchmarkExpectation(
            service_category="unknown",
            complete=True,
            recommended_next_step="not_a_fit",
            must_capture=[
                "primary_problem",
                "service_category",
            ],
            preferred_question_topics=[],
            avoid_question_topics=[
                "forcing a website sale",
                "inventing software needs",
            ],
            notes=(
                "Respectfully avoid forcing an irrelevant "
                "Paradigm Ra engagement."
            ),
        ),
    ),

    DiscoveryBenchmarkScenario(
        id="integration-001",
        title="System Integration Without Enough Context",
        stage="systems",
        contact=DiscoveryContact(
            first_name="Morgan",
            company="Evergreen Health Products",
            email="morgan@example.com",
        ),
        history=[],
        latest_prospect_message=(
            "We need our CRM and accounting platform to communicate "
            "with each other because people are entering the same "
            "customer information twice."
        ),
        current_state={},
        expected=BenchmarkExpectation(
            service_category="integrations",
            complete=False,
            must_capture=[
                "primary_problem",
                "pain_points",
                "desired_outcomes",
                "service_category",
            ],
            preferred_question_topics=[
                "CRM name",
                "accounting platform name",
                "data that needs synchronization",
            ],
            avoid_question_topics=[
                "programming language",
                "hosting architecture",
            ],
            notes=(
                "Ask targeted clarification instead of prematurely "
                "designing the architecture."
            ),
        ),
    ),

    DiscoveryBenchmarkScenario(
        id="advisory-001",
        title="We Know Something Is Broken",
        stage="problem",
        contact=DiscoveryContact(
            first_name="Renee",
            company="Harbor Property Group",
            email="renee@example.com",
        ),
        history=[],
        latest_prospect_message=(
            "We've grown pretty fast and our systems are a mess. "
            "Different teams use different tools and we're not even "
            "sure what should be replaced versus connected."
        ),
        current_state={},
        expected=BenchmarkExpectation(
            service_category="advisory",
            complete=False,
            must_capture=[
                "primary_problem",
                "pain_points",
                "service_category",
            ],
            preferred_question_topics=[
                "most painful workflow",
                "teams affected",
                "current systems",
            ],
            avoid_question_topics=[
                "immediate product recommendation",
                "full technical inventory in one question",
                "budget immediately",
            ],
            notes=(
                "Test consultative discovery when the client cannot "
                "yet articulate the solution."
            ),
        ),
    ),
]
