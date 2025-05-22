from typing import Dict, Any, List, TypedDict, Optional, Literal


class TokenMetadata(TypedDict):
    """Token metadata."""
    name: str
    symbol: str
    totalSupply: float
    SourceCode: str
    lp_info: Dict[str, Any]


class Alert(TypedDict):
    """Structure for technical alerts or warning messages."""
    type: str
    message: str
    severity: Literal['info', 'low', 'medium', 'high', 'critical']
    details: Optional[Dict[str, Any]]


class Risk(TypedDict):
    """Descriptive structure for identified risks."""
    type: str
    description: str
    severity: Literal["low", "medium", "high", "critical"]
    impact: Optional[str]
    recommendation: Optional[str]
    owner_address: Optional[str]
    details: Optional[Dict[str, Any]]


class HoneypotInfo(TypedDict):
    """Information about potential honeypot behavior."""
    is_honeypot: bool
    buy_success: Optional[bool]
    sell_success: Optional[bool]
    high_tax: Optional[bool]
    tax_discrepancy: Optional[bool]
    error: Optional[str]


class FeesInfo(TypedDict):
    """Information about buy/sell fees and slippage."""
    buy: float
    sell: float
    buy_slippage: float
    sell_slippage: float
    buy_mutable: bool
    sell_mutable: bool


class DynamicAnalysisResult(TypedDict):
    """Dynamic analysis result."""
    honeypot: HoneypotInfo
    fees: FeesInfo
    error: Optional[str]


class AnalysisResult(TypedDict):
    """Final result of the token analysis."""
    token_address: str
    name: str
    symbol: str
    supply: float
    score: Dict[str, Any]
    honeypot: HoneypotInfo
    fees: FeesInfo
    lp_lock: Dict[str, Any]
    owner: Dict[str, Any]
    top_holders: List[Dict[str, Any]]
    alerts: List[Alert]
    risks: List[Risk]
    debug_info: Optional[Dict[str, Any]]
