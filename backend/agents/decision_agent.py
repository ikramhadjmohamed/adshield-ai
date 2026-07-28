import time
import json
from dotenv import load_dotenv
load_dotenv()

from groq import Groq
from pydantic import ValidationError
from models.schemas import AgentResult, TrustReport, ExecutionMetadata

client = Groq()
MODEL = "llama-3.3-70b-versatile"
TIMEOUT_SECONDS = 10

DECISION_AGENT_SYSTEM_PROMPT = """You are the final decision-maker in an advertisement moderation pipeline, for a digital advertising platform.

You receive the complete findings from four specialized review agents (URL, Text, Image, Brand), each of which analyzed one aspect of the advertisement and reported a risk score, specific issues found, and their reasoning.

Your job is NOT to average their scores. Your job is to REASON over the combined evidence and produce a final judgment, the way a senior human moderator would after reading four specialist reports.

## How to weigh evidence

- A single strong, specific, high-confidence finding (e.g. explicit phishing language, a confirmed typosquatted domain) can justify a high overall risk even if other agents found nothing — some signals are individually disqualifying regardless of what other agents report.
- Multiple weak/moderate findings across different agents (e.g. a slightly suspicious keyword + a minor tone mismatch) can combine into a higher overall concern than any single one alone.
- A low-confidence or fallback result from one agent (check the execution status) should be weighted less than a high-confidence success result — do not treat a fallback's neutral score as strong evidence of safety.
- An agent reporting "no signal" (e.g. Brand Agent skipping an unrecognized brand) is neutral, not reassuring — do not treat it as reducing risk.
- Consider whether findings corroborate each other (e.g. a suspicious URL AND urgent scam language together are much stronger evidence than either alone).

## Recommendation categories

- "Approve" — no meaningful evidence of risk; ad appears legitimate.
- "Reject" — clear, strong evidence of scam, phishing, impersonation, or policy violation.
- "Manual Review" — mixed, ambiguous, or moderate evidence that a human should judge; also use this when agent failures (fallback/error statuses) leave the picture too incomplete for an automatic Approve or Reject.

## Output format

Respond with ONLY a valid JSON object, no explanation, no markdown code fences, no text before or after it:

{
  "overall_risk": <float between 0 and 100>,
  "recommendation": "Approve" | "Reject" | "Manual Review",
  "confidence": <float between 0 and 1>,
  "summary": "<2-4 sentence explanation referencing the specific evidence that drove this decision>"
}

Base your summary only on the evidence actually provided. Do not invent findings beyond what the four agent reports contain."""

def _build_user_message(ad_id: str, agent_results: list[AgentResult]) -> str:
    lines = [f"Advertisement ID: {ad_id}", "", "Agent reports:"]
    for result in agent_results:
        lines.append(f"\n--- {result.agent_name} ---")
        lines.append(f"Risk score: {result.risk_score}")
        lines.append(f"Confidence: {result.confidence}")
        lines.append(f"Issues: {result.issues}")
        lines.append(f"Reasoning: {result.reasoning}")
        lines.append(f"Execution status: {result.execution.status}")
    return "\n".join(lines)


def _call_groq(user_message: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.25,
        max_tokens=600,
        timeout=TIMEOUT_SECONDS,
        messages=[
            {"role": "system", "content": DECISION_AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content


def _fallback_report(ad_id: str, agent_results: list[AgentResult], duration: float, retries: int) -> TrustReport:
    return TrustReport(
        ad_id=ad_id,
        overall_risk=50.0,
        recommendation="Manual Review",
        confidence=0.0,
        agent_results=agent_results,
        summary=(
            "The Decision Agent failed to produce a valid final analysis after retrying. "
            "Flagged for manual review as a safe default."
        ),
        execution=ExecutionMetadata(
            duration_seconds=round(duration, 4),
            retries=retries,
            status="fallback",
        ),
    )


def make_decision(ad_id: str, agent_results: list[AgentResult]) -> TrustReport:
    start = time.perf_counter()
    user_message = _build_user_message(ad_id, agent_results)
    retries = 0

    for attempt in range(2):
        try:
            raw = _call_groq(
                user_message if attempt == 0
                else user_message + "\n\nRespond with ONLY the JSON object, no explanation."
            )
            parsed = json.loads(raw.strip())

            duration = time.perf_counter() - start
            return TrustReport(
                ad_id=ad_id,
                overall_risk=parsed["overall_risk"],
                recommendation=parsed["recommendation"],
                confidence=parsed["confidence"],
                agent_results=agent_results,
                summary=parsed["summary"],
                execution=ExecutionMetadata(
                    duration_seconds=round(duration, 4),
                    retries=retries,
                    status="success",
                ),
            )

        except (json.JSONDecodeError, KeyError, ValidationError):
            retries += 1
            if attempt == 1:
                return _fallback_report(ad_id, agent_results, time.perf_counter() - start, retries)
            continue

        except Exception:
            return _fallback_report(ad_id, agent_results, time.perf_counter() - start, retries)