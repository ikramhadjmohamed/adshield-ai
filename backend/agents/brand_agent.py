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

BRAND_AGENT_SYSTEM_PROMPT = """You are a brand-consistency specialist reviewing advertisement text for a digital advertising platform's moderation system.

Your job is to judge whether an advertisement's tone, claims, and style are consistent with the stated brand's known public identity and typical communication style.

## Step 1 — Brand recognition check

First, assess whether you have reliable general knowledge of this brand (its industry, typical tone, price positioning, and communication style), based on your training knowledge.

- If the brand is well-known enough that you have confident, specific knowledge of its typical advertising style (e.g. major global or well-established national brands), proceed to Step 2.
- If the brand is unfamiliar, ambiguous, generic, a small/local business, or possibly fictional, do NOT attempt to judge consistency. Instead return a neutral result (see "Unknown brand" output below). Do not guess or improvise a brand identity that you are not confident about.

## Step 2 — Consistency assessment (only if brand is recognized)

Judge whether the ad's tone and claims plausibly fit the brand's real-world positioning. Look for:
- TONE MISMATCH — e.g. a premium/luxury brand using cheap, high-pressure discount language ("EVERYTHING 95% OFF!!") uncharacteristic of its usual marketing.
- IMPLAUSIBLE BRAND CLAIMS — claims inconsistent with what is publicly known about the brand (e.g. wrong product category, exaggerated claims a real brand wouldn't legally make).
- IMPERSONATION SIGNALS — style/wording that mimics the brand's supposed identity but feels 'off' in a way consistent with impersonation rather than an authentic campaign.

Do not penalize a brand for using normal promotional language that is plausible for its category (a fast-fashion brand having a discount sale is normal; that same discount tone from a stated luxury brand is a mismatch worth flagging).

## Output format

Respond with ONLY a valid JSON object, no explanation, no markdown code fences, no text before or after it.

If the brand is recognized and assessed:
{
  "risk_score": <float between 0 and 100>,
  "issues": [<list of short strings, empty list if none>],
  "confidence": <float between 0 and 1>,
  "reasoning": "<1-3 sentence explanation referencing the brand's known identity>"
}

If the brand is unfamiliar/unrecognized/ambiguous (Step 1 stops here):
{
  "risk_score": 0,
  "issues": ["Brand not confidently recognized — consistency check skipped"],
  "confidence": 0.2,
  "reasoning": "Insufficient reliable knowledge of this brand's identity to assess consistency."
}

Do not invent facts about a brand you are not confident about."""

def _build_user_message(brand_name: str, headline: str, description: str) -> str:
    return f"Brand: {brand_name}\nHeadline: {headline}\nDescription: {description}"


def _call_groq(user_message: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.25,
        max_tokens=500,
        timeout=TIMEOUT_SECONDS,
        messages=[
            {"role": "system", "content": BRAND_AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content


def _fallback_result(duration: float, retries: int) -> AgentResult:
    return AgentResult(
        agent_name="Brand Agent",
        risk_score=50.0,
        issues=["Brand consistency analysis unavailable — manual review recommended"],
        confidence=0.0,
        reasoning="The Brand Agent failed to produce a valid analysis after retrying. Flagged for manual review as a safe default.",
        execution=ExecutionMetadata(
            duration_seconds=round(duration, 4),
            retries=retries,
            status="fallback",
        ),
    )


def analyze_brand(brand_name: str, headline: str, description: str) -> AgentResult:
    start = time.perf_counter()
    user_message = _build_user_message(brand_name, headline, description)
    retries = 0

    for attempt in range(2):
        try:
            raw = _call_groq(
                user_message if attempt == 0
                else user_message + "\n\nRespond with ONLY the JSON object, no explanation."
            )
            parsed = json.loads(raw.strip())

            duration = time.perf_counter() - start
            return AgentResult(
                agent_name="Brand Agent",
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

        except (json.JSONDecodeError, KeyError, ValidationError):
            retries += 1
            if attempt == 1:
                return _fallback_result(time.perf_counter() - start, retries)
            continue

        except Exception:
            return _fallback_result(time.perf_counter() - start, retries)