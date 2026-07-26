from urllib.parse import urlparse
from difflib import SequenceMatcher
import tldextract
from models.schemas import AgentResult
import time
from models.schemas import AgentResult, ExecutionMetadata

SUSPICIOUS_TLDS = {"xyz", "top", "click", "tk", "ml", "ga", "cf", "gq", "loan", "win"}
SUSPICIOUS_KEYWORDS = ["giveaway", "free", "winner", "claim", "bonus", "gift", "prize", "urgent"]

WEIGHTS = {
    "typosquatting": 40,
    "suspicious_tld": 20,
    "no_https": 5,
    "keyword": 10,  # per keyword, capped below
}

TYPOSQUAT_SIMILARITY_THRESHOLD = 0.6  # below this = looks unrelated to brand, not typosquat


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def analyze_url(brand_name: str, landing_url: str) -> AgentResult:
    start = time.perf_counter()
    issues: list[str] = []
    score = 0.0

    parsed = urlparse(str(landing_url))
    ext = tldextract.extract(str(landing_url))
    domain = ext.domain
    tld = ext.suffix

    brand_clean = brand_name.lower().replace(" ", "")
    domain_tokens = [t for t in domain.split("-") if t]

    # 1. Typosquatting — check substring first, then per-token similarity
    if brand_clean in domain and domain != brand_clean:
        issues.append(f"Domain contains brand name '{brand_name}' plus extra text — possible typosquatting")
        score += WEIGHTS["typosquatting"]
    else:
        best_sim = max((_similarity(brand_clean, tok) for tok in domain_tokens), default=0.0)
        if TYPOSQUAT_SIMILARITY_THRESHOLD < best_sim < 1.0:
            issues.append(f"Domain segment closely resembles brand name '{brand_name}' — possible typosquatting")
            score += WEIGHTS["typosquatting"]

    # 2. Suspicious TLD
    if tld.split(".")[-1] in SUSPICIOUS_TLDS:
        issues.append(f"Suspicious top-level domain: .{tld}")
        score += WEIGHTS["suspicious_tld"]

    # 3. HTTPS check
    if parsed.scheme != "https":
        issues.append("Landing page does not use HTTPS")
        score += WEIGHTS["no_https"]

    # 4. Suspicious keywords
    url_lower = str(landing_url).lower()
    found_keywords = [kw for kw in SUSPICIOUS_KEYWORDS if kw in url_lower]
    if found_keywords:
        issues.append(f"Suspicious keyword(s) in URL: {', '.join(found_keywords)}")
        score += min(len(found_keywords) * WEIGHTS["keyword"], 30)

    risk_score = min(score, 100.0)
    confidence = 0.9 if issues else 0.7

    duration = time.perf_counter() - start

    return AgentResult(
        agent_name="URL Agent",
        risk_score=risk_score,
        issues=issues if issues else ["No suspicious URL patterns detected"],
        confidence=confidence,
        reasoning=(
            "Weighted heuristic risk score computed from explainable signals "
            "(typosquatting, TLD reputation, HTTPS, keyword matches). "
            "Weights are expert-defined baseline values, not learned from data."
        ),
        execution=ExecutionMetadata(
            duration_seconds=round(duration, 4),
            retries=0,
            status="success",
        ),
    )
