
from pydantic import BaseModel
from typing import List, Literal, Optional, Dict

class Alert(BaseModel):
    """Estrutura de um alerta de segurança."""
    type: str
    message: str
    severity: Literal['info', 'low', 'medium', 'high', 'critical']

class ScoreDetail(BaseModel):
    value: int
    details: List[str]

class HoneypotAudit(BaseModel):
    """Informações sobre possível honeypot."""
    is_honeypot: bool
    buy_success: bool
    sell_success: bool
    high_tax: bool
    tax_discrepancy: bool
    error: Optional[str]

class FeesAudit(BaseModel):
    """Informações sobre taxas e slippage."""
    buy: float
    sell: float
    buy_slippage: float
    sell_slippage: float
    buy_mutable: bool
    sell_mutable: bool

class LPLockAudit(BaseModel):
    locked: bool
    locked_percentage: float
    unlock_date: Optional[str]

class OwnerAudit(BaseModel):
    renounced: bool
    functions: List[str]

class Holder(BaseModel):
    address: str
    percent: float

class TopHoldersAudit(BaseModel):
    top_1_percent: float
    top_10_percent: float
    top_50_percent: float
    holders: List[Holder]

class TokenHistory(BaseModel):
    address: str
    creation_date: str
    score: int

class DeployerAudit(BaseModel):
    address: str
    token_history: List[TokenHistory]

class RiskDetail(BaseModel):
    type: str
    description: str
    severity: str

class AuditResponse(BaseModel):
    token_address: str
    name: str
    symbol: str
    supply: float
    score: ScoreDetail
    honeypot: HoneypotAudit
    fees: FeesAudit
    lp_lock: LPLockAudit
    owner: OwnerAudit
    critical_functions: List[Alert] = []
    top_holders: TopHoldersAudit
    deployer: DeployerAudit
    risks: List[RiskDetail]
