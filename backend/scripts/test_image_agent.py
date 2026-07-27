import sys
import os

BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BACKEND_ROOT)

from agents.image_agent import analyze_image


def load_image(filename: str) -> bytes:
    path = os.path.join(os.path.dirname(__file__), "test_images", filename)
    with open(path, "rb") as f:
        return f.read()


TEST_CASES = [
    {
        "name": "Legitimate ad",
        "filename": "legit_ad.png",
        "expected": "low",
    },
    {
        "name": "Scam giveaway ad",
        "filename": "scam_giveaway.png",
        "expected": "high",
    },
    {   "name": "Scam giveaway ad (real, TEMU-style)",
        "filename": "scam_temu_giveaway.png", 
        "expected": "very_high"},
    {
        "name": "Phishing-style ad",
        "filename": "phishing_ad.png",
        "expected": "very_high",
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
        image_bytes = load_image(case["filename"])
        result = analyze_image(image_bytes)
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


def test_no_image():
    print("Testing with no image...")
    result = analyze_image(None)
    print(f"  Risk score: {result.risk_score}")
    print(f"  Issues: {result.issues}")
    print("-" * 60)


if __name__ == "__main__":
    run_tests()
    test_no_image()