import sys
import os

BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BACKEND_ROOT)

from agents.brand_agent import analyze_brand


TEST_CASES = [
    {
        "name": "Apple - consistent tone",
        "brand_name": "Apple",
        "headline": "iPhone 16 Pro",
        "description": "The most advanced iPhone yet. Available starting today.",
        "expected": "low",
    },
    {
        "name": "Apple - tone mismatch (discount language)",
        "brand_name": "Apple",
        "headline": "EVERYTHING 95% OFF TODAY ONLY!!",
        "description": "Insane clearance sale, click now before it's gone!",
        "expected": "high",
    },
    {
        "name": "Unknown/fictional brand",
        "brand_name": "Zorblex Dynamics",
        "headline": "New product launch",
        "description": "Check out our latest offering.",
        "expected": "low",  # neutral, not flagged as risky
    },
]


def classify(score: float) -> str:
    if score < 20:
        return "low"
    elif score < 50:
        return "medium"
    elif score < 75:
        return "high"
    else:
        return "very_high"


def run_tests():
    print("=" * 60)
    for case in TEST_CASES:
        result = analyze_brand(case["brand_name"], case["headline"], case["description"])
        actual = classify(result.risk_score)
        status = "✅ PASS" if actual == case["expected"] or (
            case["expected"] in ("high", "very_high") and actual in ("high", "very_high")
        ) else "❌ FAIL"

        print(f"{status} — {case['name']}")
        print(f"  Risk score: {result.risk_score} (expected: {case['expected']}, got: {actual})")
        print(f"  Issues: {result.issues}")
        print(f"  Reasoning: {result.reasoning}")
        print(f"  Execution: {result.execution}")
        print("-" * 60)


if __name__ == "__main__":
    run_tests()