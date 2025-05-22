from typing import TypedDict, Literal, Optional, Dict, Any, List


class AuditError(TypedDict):
    type: str
    message: str


class AuditScoreBreakdown(TypedDict, total=False):
    base_score: int
    adjustments: List[Dict[str, Any]]
    final_score: int


class AuditAnalysis(TypedDict):
    static: Dict[str, Any]
    dynamic: Dict[str, Any]
    onchain: Dict[str, Any]


class AuditResult(TypedDict, total=False):
    status: Literal["completed", "error"]
    timestamp: str
    token_address: str
    lp_token_address: Optional[str]
    score: int
    grade: str
    risk_meter: str
    analysis: AuditAnalysis
    alerts: List[Dict[str, Any]]
    risks: List[Dict[str, Any]]
    score_breakdown: AuditScoreBreakdown
    error: Optional[AuditError]
