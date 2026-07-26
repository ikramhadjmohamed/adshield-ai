import sys
import os

BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BACKEND_ROOT)

from agents.text_agent import analyze_text

TEST_CASES = [
    {
        "name": "Legitimate Nike ad",
        "brand_name": "Nike",
        "headline": "New Air Max Collection",
        "description": "Discover our latest running shoes. Free shipping on orders over $50.",
        "expected": "low",
    },
    {
        "name": "Fake giveaway (urgency + unrealistic promise)",
        "brand_name": "Nike",
        "headline": "Congratulations!! You WON a FREE pair of Air Jordans!",
        "description": "Click NOW before this offer expires in 5 minutes! Only 2 left!",
        "expected": "high",
    },
    {
        "name": "Phishing-style ad",
        "brand_name": "Amazon",
        "headline": "Your account has been suspended",
        "description": "Verify your payment details now to restore access to your Amazon account.",
        "expected": "very_high",
    },
    {
        "name": "Real promotion with deadline (false positive check)",
        "brand_name": "Spotify",
        "headline": "Black Friday Sale",
        "description": "Get 3 months of Premium for $1. Offer ends Monday.",
        "expected": "low",
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
        result = analyze_text(case["brand_name"], case["headline"], case["description"])
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