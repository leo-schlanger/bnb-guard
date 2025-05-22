from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any
from datetime import datetime, timezone


class Alert(BaseModel):
    type: str
    message: str
    severity: Literal['info', 'low', 'medium', 'high', 'critical']
    details: Optional[Dict[str, Any]] = None


class RiskDetail(BaseModel):
    type: str
    description: str
    severity: Literal['low', 'medium', 'high', 'critical']
    impact: Optional[str] = None
    recommendation: Optional[str] = None
    owner_address: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class ScoreBreakdown(BaseModel):
    base_score: int
    adjustments: List[Dict[str, Any]]
    final_score: int


class AnalysisSection(BaseModel):
    static: Dict[str, Any]
    dynamic: Dict[str, Any]
    onchain: Dict[str, Any]


class AuditError(BaseModel):
    type: str
    message: str


class AuditResponse(BaseModel):
    status: Literal["completed", "error"]
    timestamp: str
    token_address: str
    lp_token_address: Optional[str] = None
    score: int
    grade: str
    risk_meter: str
    analysis: AnalysisSection
    alerts: List[Alert] = Field(default_factory=list)
    risks: List[RiskDetail] = Field(default_factory=list)
    score_breakdown: ScoreBreakdown
    error: Optional[AuditError] = None

    @classmethod
    def create_error_response(cls, token_address: str, error_message: str, lp_token_address: str = None):
        return cls(
            timestamp=datetime.now(timezone.utc).isoformat(),
            status="error",
            token_address=token_address,
            lp_token_address=lp_token_address,
            score=0,
            grade="F",
            risk_meter="🔴 Critical risk",
            analysis=AnalysisSection(
                static={},
                dynamic={},
                onchain={}
            ),
            alerts=[],
            risks=[
                RiskDetail(
                    type="critical",
                    description=error_message,
                    severity="critical"
                )
            ],
            score_breakdown=ScoreBreakdown(
                base_score=0,
                adjustments=[],
                final_score=0
            ),
            error=AuditError(
                type="VerificationError",
                message=error_message
            )
        )