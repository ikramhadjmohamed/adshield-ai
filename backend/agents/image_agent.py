import time
import json
from dotenv import load_dotenv
load_dotenv()

import numpy as np
from PIL import Image
import io

import easyocr
from groq import Groq
from pydantic import ValidationError
from models.schemas import AgentResult, ExecutionMetadata

client = Groq()
MODEL = "llama-3.3-70b-versatile"
TIMEOUT_SECONDS = 10

# Loaded once at module import — avoids reloading the OCR model on every call
_ocr_reader = easyocr.Reader(["en"], gpu=False)

IMAGE_AGENT_SYSTEM_PROMPT = """You are a fraud-detection specialist reviewing text extracted via OCR from an advertisement's image, for a digital advertising platform's moderation system.

The text you receive was extracted automatically from an image and may contain minor OCR errors (misread characters, missing spaces, broken words). Use reasonable judgment to interpret likely intent despite small recognition noise — do not flag OCR artifacts themselves as suspicious.

Analyze the extracted text for signs of scam, manipulation, or policy violations across exactly five categories:

1. URGENCY — artificial time pressure designed to prevent careful thinking (e.g. "Act now", "Offer expires in 10 minutes", countdown pressure unrelated to a real sale).
2. UNREALISTIC PROMISES — claims that are implausible or too good to be true (e.g. "Win a free iPhone", "Guaranteed 500% returns", "100% risk-free").
3. PHISHING LANGUAGE — wording designed to extract personal/financial information or credentials (e.g. "Verify your account now", "Confirm your payment details", "Claim your prize by logging in").
4. MANIPULATIVE WORDING — psychological pressure tactics beyond simple urgency (e.g. fake scarcity "Only 2 left!", fake social proof "5,000 people claimed this today", guilt-tripping, exaggerated exclamation/caps abuse).
5. MISLEADING CLAIMS — factual claims that are likely false, exaggerated, or unverifiable in a way that misrepresents the product/brand.

## What NOT to flag

- Ordinary promotional words ("free", "sale", "discount") in a normal commercial context.
- Real, verifiable time-bound promotions.
- Enthusiastic but plausible marketing tone.
- Minor OCR noise (broken words, stray characters) — interpret intent, don't flag the noise itself.

Only flag a category if there is a clear, specific textual signal. If the extracted text is plain, ordinary advertising copy, or too short/fragmented to assess meaningfully, return a low risk score with an empty or near-empty issues list and a lower confidence value.

## Output format

Respond with ONLY a valid JSON object, no explanation, no markdown code fences, no text before or after it:

{
  "risk_score": <float between 0 and 100>,
  "issues": [<list of short strings, empty list if none>],
  "confidence": <float between 0 and 1>,
  "reasoning": "<1-3 sentence explanation>"
}

Do not invent issues that aren't supported by the actual extracted text."""


def _neutral_result(reason: str, duration: float) -> AgentResult:
    return AgentResult(
        agent_name="Image Agent",
        risk_score=0.0,
        issues=[reason],
        confidence=0.5,
        reasoning="No sufficient visual/text signal to assess — treated as neutral, not a failure.",
        execution=ExecutionMetadata(
            duration_seconds=round(duration, 4),
            retries=0,
            status="success",
        ),
    )


def _fallback_result(duration: float, retries: int) -> AgentResult:
    return AgentResult(
        agent_name="Image Agent",
        risk_score=50.0,
        issues=["Image text analysis unavailable — manual review recommended"],
        confidence=0.0,
        reasoning="The Image Agent failed to produce a valid analysis after retrying. Flagged for manual review as a safe default.",
        execution=ExecutionMetadata(
            duration_seconds=round(duration, 4),
            retries=retries,
            status="fallback",
        ),
    )


def _extract_text(image_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_array = np.array(image)
    results = _ocr_reader.readtext(image_array, detail=0)
    return " ".join(results).strip()


def _call_groq(ocr_text: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.25,
        max_tokens=500,
        timeout=TIMEOUT_SECONDS,
        messages=[
            {"role": "system", "content": IMAGE_AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": f"Extracted text from ad image:\n{ocr_text}"},
        ],
    )
    return response.choices[0].message.content


def analyze_image(image_bytes: bytes | None) -> AgentResult:
    start = time.perf_counter()

    if image_bytes is None:
        return _neutral_result("No image provided", time.perf_counter() - start)

    ocr_text = _extract_text(image_bytes)

    if not ocr_text:
        return _neutral_result("No text detected in image", time.perf_counter() - start)

    retries = 0
    for attempt in range(2):
        try:
            raw = _call_groq(
                ocr_text if attempt == 0
                else ocr_text + "\n\n(Respond with ONLY the JSON object, no explanation.)"
            )
            parsed = json.loads(raw.strip())

            duration = time.perf_counter() - start
            return AgentResult(
                agent_name="Image Agent",
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