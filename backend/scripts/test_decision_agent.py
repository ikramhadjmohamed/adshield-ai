import sys
import os

BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BACKEND_ROOT)

from agents.decision_agent import make_decision
from models.schemas import AgentResult, ExecutionMetadata


def make_result(agent_name, risk_score, issues, confidence, reasoning, status="success"):
    return AgentResult(
        agent_name=agent_name,
        risk_score=risk_score,
        issues=issues,
        confidence=confidence,
        reasoning=reasoning,
        execution=ExecutionMetadata(duration_seconds=0.5, retries=0, status=status),
    )


SCENARIOS = [
    {
        "name": "All agents low risk — should Approve",
        "results": [
            make_result("URL Agent", 0, ["No suspicious URL patterns detected"], 0.9, "Clean domain."),
            make_result("Text Agent", 0, [], 0.9, "Legitimate promotional copy."),
            make_result("Image Agent", 0, ["No image provided"], 0.5, "No image to assess."),
            make_result("Brand Agent", 0, [], 0.9, "Consistent with brand tone."),
        ],
        "expected": "Approve",
    },
    {
        "name": "One strong signal (explicit phishing) despite others low — should Reject",
        "results": [
            make_result("URL Agent", 10, ["No suspicious URL patterns detected"], 0.9, "Domain looks fine."),
            make_result("Text Agent", 95, ["PHISHING LANGUAGE"], 0.95, "Explicit request to verify payment details, classic phishing pattern."),
            make_result("Image Agent", 0, ["No image provided"], 0.5, "No image to assess."),
            make_result("Brand Agent", 5, [], 0.8, "No major tone mismatch detected."),
        ],
        "expected": "Reject",
    },
    {
        "name": "Mixed moderate signals — should be Manual Review",
        "results": [
            make_result("URL Agent", 45, ["Suspicious keyword(s) in URL: free"], 0.7, "Minor suspicious keyword only."),
            make_result("Text Agent", 40, ["MANIPULATIVE WORDING"], 0.6, "Mild pressure tactics, not conclusive."),
            make_result("Image Agent", 0, ["No image provided"], 0.5, "No image to assess."),
            make_result("Brand Agent", 35, ["Tone mismatch"], 0.5, "Slightly off-tone but not clearly impersonation."),
        ],
        "expected": "Manual Review",
    },
]


def run_tests():
    print("=" * 60)
    for scenario in SCENARIOS:
        report = make_decision("test-ad-id", scenario["results"])
        status = "✅ PASS" if report.recommendation == scenario["expected"] else "❌ FAIL"

        print(f"{status} — {scenario['name']}")
        print(f"  Recommendation: {report.recommendation} (expected: {scenario['expected']})")
        print(f"  Overall risk: {report.overall_risk}")
        print(f"  Summary: {report.summary}")
        print(f"  Execution: {report.execution}")
        print("-" * 60)


if __name__ == "__main__":
    run_tests()