"""Example demonstrating new AgentNet catalog agents: CodeReviewer, SentimentAnalyzer, TaskPlanner."""

from agentnet import (
    CodeReviewer,
    CodeReviewResult,
    PlanResult,
    SentimentAnalyzer,
    SentimentResult,
    TaskPlanner,
)
from agentnet.providers.adapters.fake import FakeProviderAdapter

print("=" * 60)
print("AgentNet Catalog Agents Demonstration")
print("=" * 60)

# 1. CodeReviewer
mock_code_adapter = FakeProviderAdapter(
    response_fn=lambda req: {
        "summary": "Detected SQL injection vulnerability and missing input sanitation.",
        "overall_score": 65,
        "issues": [
            {
                "severity": "critical",
                "category": "security",
                "line_number": 2,
                "description": "F-string directly inlines user input into SQL statement.",
                "recommendation": "Use parameterized queries or ORM models.",
            }
        ],
        "strengths": ["Clear and concise function structure"],
    }
)
reviewer = CodeReviewer(model="openai/gpt-4.1", provider_adapter=mock_code_adapter)
review_res = reviewer.run(code="def find_user(name):\n    return db.query(f'SELECT * FROM users WHERE name = {name}')")
review: CodeReviewResult = review_res.output
print(f"\n1. CodeReviewer Score: {review.overall_score}/100")
print(f"   Summary: {review.summary}")
for issue in review.issues:
    print(f"   [{issue.severity.upper()}] Line {issue.line_number}: {issue.description}")

# 2. SentimentAnalyzer
mock_sentiment_adapter = FakeProviderAdapter(
    response_fn=lambda req: {
        "sentiment": "positive",
        "polarity": 0.92,
        "confidence": 0.97,
        "key_aspects": ["fast responses", "helpful support"],
        "reasoning": "User expressed strong satisfaction with customer assistance.",
    }
)
analyzer = SentimentAnalyzer(model="openai/gpt-4.1", provider_adapter=mock_sentiment_adapter)
sentiment_res = analyzer.run(text="The customer support team resolved my issue in under 5 minutes!")
sentiment: SentimentResult = sentiment_res.output
print("\n2. SentimentAnalyzer Result:")
print(f"   Sentiment: {sentiment.sentiment.upper()} (Polarity: {sentiment.polarity:+.2f}, Confidence: {sentiment.confidence * 100:.0f}%)")
print(f"   Key Aspects: {', '.join(sentiment.key_aspects)}")

# 3. TaskPlanner
mock_planner_adapter = FakeProviderAdapter(
    response_fn=lambda req: {
        "goal": "Launch modern AI web portal",
        "summary": "Structured 3-phase rollout roadmap.",
        "tasks": [
            {
                "id": 1,
                "title": "Build Next.js Frontend",
                "description": "Setup UI with design system and responsive components.",
                "dependencies": [],
                "estimated_effort": "high",
                "exit_criteria": "Lighthouse performance score >= 90",
            },
            {
                "id": 2,
                "title": "Integrate AgentNet Python Backend",
                "description": "Connect FastAPI microservice to AgentNet workflow engine.",
                "dependencies": [1],
                "estimated_effort": "medium",
                "exit_criteria": "P95 latency < 500ms",
            },
        ],
        "risks": ["High API concurrency might trigger provider rate limits."],
    }
)
planner = TaskPlanner(model="gemini/gemini-2.5-flash", provider_adapter=mock_planner_adapter)
plan_res = planner.run(goal="Launch modern AI web portal")
plan: PlanResult = plan_res.output
print(f"\n3. TaskPlanner Plan: {plan.goal}")
print(f"   Summary: {plan.summary}")
for task in plan.tasks:
    dep_str = f" (deps: {task.dependencies})" if task.dependencies else ""
    print(f"   - Task {task.id}: {task.title}{dep_str} [Effort: {task.estimated_effort}]")
print("=" * 60)
