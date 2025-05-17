from pydantic import BaseModel
from typing import List

class TokenAnalysisResponse(BaseModel):
    address: str
    score: int
    status: str
    alerts: List[str]
