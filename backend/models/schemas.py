from typing import Literal
from pydantic import BaseModel, HttpUrl, Field
from uuid import uuid4


class Advertisement(BaseModel):
    ad_id: str = Field(default_factory=lambda: str(uuid4()))
    brand_name: str
    headline: str
    description: str
    landing_url: HttpUrl
    image_bytes: bytes | None = None


class ExecutionMetadata(BaseModel):
    duration_seconds: float = Field(ge=0.0)
    retries: int = Field(ge=0)
    status: Literal["success", "fallback", "error"]


class AgentResult(BaseModel):
    agent_name: str
    risk_score: float = Field(ge=0.0, le=100.0)
    issues: list[str]
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str | None = None
    execution: ExecutionMetadata


class TrustReport(BaseModel):
    ad_id: str
    overall_risk: float = Field(ge=0.0, le=100.0)
    recommendation: Literal["Approve", "Reject", "Manual Review"]
    confidence: float = Field(ge=0.0, le=1.0)
    agent_results: list[AgentResult]
    summary: str
    execution: ExecutionMetadata