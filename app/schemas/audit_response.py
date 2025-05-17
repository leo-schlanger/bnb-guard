
from pydantic import BaseModel
from typing import List, Optional, Dict

class ScoreDetail(BaseModel):
    value: int
    details: List[str]

class HoneypotAudit(BaseModel):
    buy_success: bool
    sell_success: bool
    slippage: float
    error_message: Optional[str]

class FeesAudit(BaseModel):
    buy: float
    sell: float
    buy_mutable: bool
    sell_mutable: bool

class LPLockAudit(BaseModel):
    locked: bool
    locked_percentage: float
    unlock_date: Optional[str]

class OwnerAudit(BaseModel):
    renounced: bool
    functions: List[str]

class CriticalFunction(BaseModel):
    name: str
    access: str
    description: str

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
    critical_functions: List[CriticalFunction]
    top_holders: TopHoldersAudit
    deployer: DeployerAudit
    risks: List[RiskDetail]
