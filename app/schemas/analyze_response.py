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

class Alert(BaseModel):
    type: str
    message: str
    severity: Severity
    details: Optional[Dict[str, Any]] = None

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
    alerts: List[Alert] = Field(default_factory=list)
    debug_info: Optional[Dict[str, Any]] = None

    @classmethod
    def create_error_response(cls, token_address: str, error: str) -> 'AnalyzeResponse':
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
        if not token_address:
            token_address = "0x0000000000000000000000000000000000000000"
        elif not token_address.startswith('0x'):
            token_address = f'0x{token_address}'

        name = metadata.get("name", "Unknown")
        symbol = metadata.get("symbol", "UNKNOWN")

        try:
            supply = float(metadata.get("totalSupply", 0))
        except (ValueError, TypeError):
            supply = 0.0

        has_error = name == "Error" or "error" in metadata
        error_msg = metadata.get("error", None) if has_error else None

        processed_kwargs = {}

        def extract_field(field_name, cls_type):
            data = kwargs.pop(field_name, None)
            if isinstance(data, dict):
                return cls_type(**data)
            elif isinstance(data, cls_type):
                return data
            return cls_type()

        processed_kwargs["score"] = extract_field("score", Score)
        processed_kwargs["honeypot"] = extract_field("honeypot", Honeypot)
        processed_kwargs["fees"] = extract_field("fees", Fees)
        processed_kwargs["lp_lock"] = extract_field("lp_lock", LPLock)
        processed_kwargs["owner"] = extract_field("owner", Owner)

        # Holders
        holders_data = kwargs.pop("top_holders", [])
        processed_kwargs["top_holders"] = [
            Holder(**h) if isinstance(h, dict) else h for h in holders_data if isinstance(h, (dict, Holder))
        ]

        # Risks
        risks_data = kwargs.pop("risks", [])
        processed_kwargs["risks"] = [
            Risk(
                severity=Severity(r.get("severity", "info")) if isinstance(r.get("severity"), str) else r.get("severity"),
                title=r.get("title", "Unknown Risk"),
                description=r.get("description", "")
            ) if isinstance(r, dict) else r for r in risks_data if isinstance(r, (dict, Risk))
        ]

        # Alerts
        alerts_data = kwargs.pop("alerts", [])
        processed_kwargs["alerts"] = [
            Alert(
                type=a.get("type", "unspecified"),
                message=a.get("message", ""),
                severity=Severity(a.get("severity", "info")),
                details=a.get("details", {})
            ) if isinstance(a, dict) else a for a in alerts_data if isinstance(a, (dict, Alert))
        ]

        # Debug info
        processed_kwargs["debug_info"] = kwargs.pop("debug_info", None)

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
            return cls.create_error_response(
                token_address=token_address,
                error=f"Error creating response: {str(e)}"
            )
