import time
import json
from dotenv import load_dotenv
load_dotenv()

from groq import Groq
from pydantic import ValidationError
from models.schemas import AgentResult, ExecutionMetadata

client = Groq()

MODEL = "llama-3.3-70b-versatile"
TIMEOUT_SECONDS = 10

TEXT_AGENT_SYSTEM_PROMPT = """You are a fraud-detection specialist reviewing advertisement text for a digital advertising platform's moderation system.

Your job is to analyze the HEADLINE and DESCRIPTION of an advertisement and detect signs of scam, manipulation, or policy violations across exactly five categories:

1. URGENCY — artificial time pressure designed to prevent careful thinking (e.g. "Act now", "Offer expires in 10 minutes", countdown pressure unrelated to a real sale).
2. UNREALISTIC PROMISES — claims that are implausible or too good to be true (e.g. "Win a free iPhone", "Guaranteed 500% returns", "100% risk-free").
3. PHISHING LANGUAGE — wording designed to extract personal/financial information or credentials (e.g. "Verify your account now", "Confirm your payment details", "Claim your prize by logging in").
4. MANIPULATIVE WORDING — psychological pressure tactics beyond simple urgency (e.g. fake scarcity "Only 2 left!", fake social proof "5,000 people claimed this today", guilt-tripping, exaggerated exclamation/caps abuse).
5. MISLEADING CLAIMS — factual claims that are likely false, exaggerated, or unverifiable in a way that misrepresents the product/brand (e.g. fake medical claims, fake certifications, impersonating a known brand's tone without being that brand).

## What NOT to flag (to avoid false positives)

Legitimate advertising language should NOT be flagged on its own:
- Ordinary promotional words like "free", "sale", "discount", "new", "limited edition" when used in a normal commercial context (e.g. "Free shipping on orders over $50" is normal, "Claim your FREE prize NOW!!!" combined with urgency/caps is not).
- Real, verifiable time-bound promotions (e.g. "Black Friday sale ends Monday") — only flag urgency if it is vague, exaggerated, or paired with pressure tactics.
- Enthusiastic but plausible marketing tone (e.g. "Our best deal yet!") — this is normal advertising, not manipulation.
- A single exclamation mark or normal capitalization is not manipulative wording by itself. Look for patterns (excessive punctuation, ALL CAPS phrases, stacked pressure tactics), not isolated stylistic choices.

Only flag a category if there is a clear, specific textual signal — not a vague impression. If the ad text is plain, ordinary advertising copy, you should return a low risk score with an empty or near-empty issues list.

## Output format

Respond with ONLY a valid JSON object, with no explanation, no markdown code fences, and no text before or after it. The JSON must have exactly this structure:

{
  "risk_score": <float between 0 and 100>,
  "issues": [<list of short strings describing each specific issue found, empty list if none>],
  "confidence": <float between 0 and 1, how confident you are in this assessment>,
  "reasoning": "<1-3 sentence explanation of the overall assessment, referencing which categories were triggered and why, or why the ad appears legitimate>"
}

Do not include any category that was not triggered in the issues list. Do not invent issues that aren't supported by the actual text."""


def _build_user_message(brand_name: str, headline: str, description: str) -> str:
    return f"Brand: {brand_name}\nHeadline: {headline}\nDescription: {description}"


def _call_groq(user_message: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.25,
        max_tokens=500,
        timeout=TIMEOUT_SECONDS,
        messages=[
            {"role": "system", "content": TEXT_AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content


def _parse_response(raw_text: str) -> dict:
    # Defensive strip in case the model adds stray whitespace/newlines
    return json.loads(raw_text.strip())


def _fallback_result(duration: float, retries: int) -> AgentResult:
    return AgentResult(
        agent_name="Text Agent",
        risk_score=50.0,
        issues=["Text analysis unavailable — manual review recommended"],
        confidence=0.0,
        reasoning="The Text Agent failed to produce a valid analysis after retrying. Flagged for manual review as a safe default.",
        execution=ExecutionMetadata(
            duration_seconds=round(duration, 4),
            retries=retries,
            status="fallback",
        ),
    )


def analyze_text(brand_name: str, headline: str, description: str) -> AgentResult:
    start = time.perf_counter()
    user_message = _build_user_message(brand_name, headline, description)
    retries = 0

    for attempt in range(2):  # initial attempt + 1 retry
        try:
            raw = _call_groq(
                user_message if attempt == 0
                else user_message + "\n\nRespond with ONLY the JSON object, no explanation."
            )
            parsed = _parse_response(raw)

            duration = time.perf_counter() - start
            return AgentResult(
                agent_name="Text Agent",
                risk_score=parsed["risk_score"],
                issues=parsed["issues"],
                confidence=parsed["confidence"],
                reasoning=parsed.get("reasoning"),
                execution=ExecutionMetadata(
                    duration_seconds=round(duration, 4),
                    retries=retries,
                    status="success",
                ),
            )

        except (json.JSONDecodeError, KeyError, ValidationError) as e:
            retries += 1
            if attempt == 1:  # last attempt already failed
                duration = time.perf_counter() - start
                return _fallback_result(duration, retries)
            continue  # retry once

        except Exception as e:
            # Network/timeout/API errors — no point retrying immediately, go straight to fallback
            duration = time.perf_counter() - start
            return _fallback_result(duration, retries)