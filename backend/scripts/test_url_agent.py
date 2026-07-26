import sys
import os

BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BACKEND_ROOT)

from agents.url_agent import analyze_url

TEST_CASES = [
    {
        "name": "Legitimate Nike ad",
        "brand_name": "Nike",
        "landing_url": "https://nike.com",
        "expected": "low",
    },
    {
        "name": "Typosquat + scam keywords",
        "brand_name": "Nike",
        "landing_url": "https://nike-free-winner.xyz",
        "expected": "high",
    },
    {
        "name": "Typosquat impersonating Amazon (login phishing)",
        "brand_name": "Amazon",
        "landing_url": "http://arnazon-login.top",
        "expected": "very_high",
    },
    {
        "name": "Legitimate ad with 'free' keyword (false positive check)",
        "brand_name": "Spotify",
        "landing_url": "https://spotify.com/free-trial",
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
        result = analyze_url(case["brand_name"], case["landing_url"])
        actual = classify(result.risk_score)
        status = "✅ PASS" if actual == case["expected"] or (
            case["expected"] in ("high", "very_high") and actual in ("high", "very_high")
        ) else "❌ FAIL"

        print(f"{status} — {case['name']}")
        print(f"  URL: {case['landing_url']}")
        print(f"  Risk score: {result.risk_score} (expected: {case['expected']}, got: {actual})")
        print(f"  Issues: {result.issues}")
        print("-" * 60)


if __name__ == "__main__":
    run_tests()
