from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Risk(BaseModel):
    severity: Severity
    title: str
    description: str

class Holder(BaseModel):
    address: str
    percent: float = 0.0

class Score(BaseModel):
    value: int = 0
    label: str = "Unknown"

class Honeypot(BaseModel):
    is_honeypot: bool = False
    buy_success: Optional[bool] = None
    sell_success: Optional[bool] = None
    high_tax: Optional[bool] = None
    tax_discrepancy: Optional[bool] = None
    error: Optional[str] = None

class Fees(BaseModel):
    buy: float = 0.0
    sell: float = 0.0
    buy_slippage: float = 0.0
    sell_slippage: float = 0.0
    buy_mutable: bool = False
    sell_mutable: bool = False

class LPLock(BaseModel):
    locked: bool = False
    percent_locked: Optional[float] = None

class Owner(BaseModel):
    renounced: bool = False
    address: Optional[str] = None

class AnalyzeResponse(BaseModel):
    success: bool = True
    error: Optional[str] = None
    token_address: str
    name: Optional[str] = "Unknown"
    symbol: Optional[str] = "UNKNOWN"
    supply: float = 0.0
    score: Score = Field(default_factory=Score)
    honeypot: Honeypot = Field(default_factory=Honeypot)
    fees: Fees = Field(default_factory=Fees)
    lp_lock: LPLock = Field(default_factory=LPLock)
    owner: Owner = Field(default_factory=Owner)
    top_holders: List[Holder] = Field(default_factory=list)
    risks: List[Risk] = Field(default_factory=list)
    
    @classmethod
    def create_error_response(cls, token_address: str, error: str) -> 'AnalyzeResponse':
        return cls(
            success=False,
            error=error,
            token_address=token_address,
            score=Score(value=0, label="Error"),
            risks=[
                Risk(
                    severity=Severity.CRITICAL,
                    title="Analysis Failed",
                    description=error
                )
            ]
        )
