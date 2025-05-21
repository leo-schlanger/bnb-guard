from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
import datetime

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
    debug_info: Optional[Dict[str, Any]] = None
    
    @classmethod
    def create_error_response(cls, token_address: str, error: str) -> 'AnalyzeResponse':
        # Ensure token_address is properly formatted
        if token_address and not token_address.startswith('0x'):
            token_address = f'0x{token_address}'
            
        return cls(
            success=False,
            error=error,
            token_address=token_address,
            name="Error",
            symbol="ERR",
            score=Score(value=0, label="Error"),
            honeypot=Honeypot(is_honeypot=False, error=error),
            risks=[
                Risk(
                    severity=Severity.CRITICAL,
                    title="Analysis Failed",
                    description=error
                )
            ],
            debug_info={
                "error_message": error,
                "timestamp": str(datetime.datetime.now())
            }
        )
        
    @classmethod
    def from_metadata(cls, token_address: str, metadata: Dict[str, Any], **kwargs) -> 'AnalyzeResponse':
        """Create a response from token metadata"""
        
        # Validate token_address
        if not token_address:
            token_address = "0x0000000000000000000000000000000000000000"
        elif not token_address.startswith('0x'):
            token_address = f'0x{token_address}'
        
        # Extract basic token info with safe defaults
        name = metadata.get("name", "Unknown")
        symbol = metadata.get("symbol", "UNKNOWN")
        
        # Handle supply safely
        try:
            supply = float(metadata.get("totalSupply", 0))
        except (ValueError, TypeError):
            supply = 0.0
        
        # Check for errors in metadata
        has_error = name == "Error" or "error" in metadata
        error_msg = metadata.get("error", None) if has_error else None
        
        # Process kwargs to ensure they match expected types
        processed_kwargs = {}
        
        # Handle score
        if "score" in kwargs:
            score_data = kwargs.pop("score")
            if isinstance(score_data, dict):
                processed_kwargs["score"] = Score(
                    value=score_data.get("value", 0),
                    label=score_data.get("label", "Unknown")
                )
            elif not isinstance(score_data, Score):
                processed_kwargs["score"] = Score()
            else:
                processed_kwargs["score"] = score_data
        
        # Handle honeypot
        if "honeypot" in kwargs:
            honeypot_data = kwargs.pop("honeypot")
            if isinstance(honeypot_data, dict):
                processed_kwargs["honeypot"] = Honeypot(
                    is_honeypot=honeypot_data.get("is_honeypot", False),
                    buy_success=honeypot_data.get("buy_success"),
                    sell_success=honeypot_data.get("sell_success"),
                    high_tax=honeypot_data.get("high_tax"),
                    tax_discrepancy=honeypot_data.get("tax_discrepancy"),
                    error=honeypot_data.get("error")
                )
            elif not isinstance(honeypot_data, Honeypot):
                processed_kwargs["honeypot"] = Honeypot()
            else:
                processed_kwargs["honeypot"] = honeypot_data
        
        # Handle fees
        if "fees" in kwargs:
            fees_data = kwargs.pop("fees")
            if isinstance(fees_data, dict):
                processed_kwargs["fees"] = Fees(
                    buy=float(fees_data.get("buy", 0.0)),
                    sell=float(fees_data.get("sell", 0.0)),
                    buy_slippage=float(fees_data.get("buy_slippage", 0.0)),
                    sell_slippage=float(fees_data.get("sell_slippage", 0.0)),
                    buy_mutable=bool(fees_data.get("buy_mutable", False)),
                    sell_mutable=bool(fees_data.get("sell_mutable", False))
                )
            elif not isinstance(fees_data, Fees):
                processed_kwargs["fees"] = Fees()
            else:
                processed_kwargs["fees"] = fees_data
        
        # Handle lp_lock
        if "lp_lock" in kwargs:
            lp_lock_data = kwargs.pop("lp_lock")
            if isinstance(lp_lock_data, dict):
                processed_kwargs["lp_lock"] = LPLock(
                    locked=bool(lp_lock_data.get("locked", False)),
                    percent_locked=lp_lock_data.get("percent_locked")
                )
            elif not isinstance(lp_lock_data, LPLock):
                processed_kwargs["lp_lock"] = LPLock()
            else:
                processed_kwargs["lp_lock"] = lp_lock_data
        
        # Handle owner
        if "owner" in kwargs:
            owner_data = kwargs.pop("owner")
            if isinstance(owner_data, dict):
                processed_kwargs["owner"] = Owner(
                    renounced=bool(owner_data.get("renounced", False)),
                    address=owner_data.get("address")
                )
            elif not isinstance(owner_data, Owner):
                processed_kwargs["owner"] = Owner()
            else:
                processed_kwargs["owner"] = owner_data
        
        # Handle top_holders
        if "top_holders" in kwargs:
            holders_data = kwargs.pop("top_holders")
            if isinstance(holders_data, list):
                processed_holders = []
                for holder in holders_data:
                    if isinstance(holder, dict):
                        processed_holders.append(Holder(
                            address=holder.get("address", ""),
                            percent=float(holder.get("percent", 0.0))
                        ))
                    elif isinstance(holder, Holder):
                        processed_holders.append(holder)
                processed_kwargs["top_holders"] = processed_holders
            elif not isinstance(holders_data, list):
                processed_kwargs["top_holders"] = []
            else:
                processed_kwargs["top_holders"] = holders_data
        
        # Handle risks
        if "risks" in kwargs:
            risks_data = kwargs.pop("risks")
            if isinstance(risks_data, list):
                processed_risks = []
                for risk in risks_data:
                    if isinstance(risk, dict):
                        severity = risk.get("severity", "info")
                        if not isinstance(severity, Severity):
                            try:
                                severity = Severity(severity)
                            except ValueError:
                                severity = Severity.INFO
                        
                        processed_risks.append(Risk(
                            severity=severity,
                            title=risk.get("title", "Unknown Risk"),
                            description=risk.get("description", "")
                        ))
                    elif isinstance(risk, Risk):
                        processed_risks.append(risk)
                processed_kwargs["risks"] = processed_risks
            elif not isinstance(risks_data, list):
                processed_kwargs["risks"] = []
            else:
                processed_kwargs["risks"] = risks_data
        
        # Add any remaining kwargs
        processed_kwargs.update(kwargs)
        
        # Create and return the response
        try:
            return cls(
                success=not has_error,
                error=error_msg,
                token_address=token_address,
                name=name,
                symbol=symbol,
                supply=supply,
                **processed_kwargs
            )
        except Exception as e:
            # Fallback to a simple error response if anything fails
            return cls.create_error_response(
                token_address=token_address,
                error=f"Error creating response: {str(e)}"
            )
