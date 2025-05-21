from typing import Dict, Any, List, TypedDict, Optional, Literal

class TokenMetadata(TypedDict):
    """Metadados do token."""
    name: str
    symbol: str
    totalSupply: float
    SourceCode: str
    lp_info: Dict[str, Any]

class Alert(TypedDict):
    """Estrutura de um alerta de segurança."""
    type: str
    message: str
    severity: Literal['info', 'low', 'medium', 'high', 'critical']

class HoneypotInfo(TypedDict):
    """Informações sobre possível honeypot."""
    is_honeypot: bool
    buy_success: bool
    sell_success: bool
    high_tax: bool
    tax_discrepancy: bool
    error: Optional[str]

class FeesInfo(TypedDict):
    """Informações sobre taxas e slippage."""
    buy: float
    sell: float
    buy_slippage: float
    sell_slippage: float
    buy_mutable: bool
    sell_mutable: bool

class DynamicAnalysisResult(TypedDict):
    """Resultado da análise dinâmica."""
    honeypot: HoneypotInfo
    fees: FeesInfo
    error: Optional[str]

class AnalysisResult(TypedDict):
    """Resultado completo da análise do token."""
    token_address: str
    name: str
    symbol: str
    supply: float
    score: Dict[str, Any]
    honeypot: HoneypotInfo
    fees: FeesInfo
    lp_lock: Dict[str, bool]
    alerts: Dict[str, List[Alert]]
