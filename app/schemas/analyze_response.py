from pydantic import BaseModel
from typing import List

class Holder(BaseModel):
    address: str
    percent: float

class Score(BaseModel):
    value: int
    label: str

class Honeypot(BaseModel):
    is_honeypot: bool

class Fees(BaseModel):
    buy: float
    sell: float

class LPLock(BaseModel):
    locked: bool

class Owner(BaseModel):
    renounced: bool

class AnalyzeResponse(BaseModel):
    token_address: str
    name: str
    symbol: str
    supply: float
    score: Score
    honeypot: Honeypot
    fees: Fees
    lp_lock: LPLock
    owner: Owner
    top_holders: List[Holder]
    risks: List[str]
