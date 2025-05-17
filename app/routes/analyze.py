import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from fastapi import APIRouter
from app.schemas.analyze_response import AnalyzeResponse
from app.services.analyzer import analyze_token

router = APIRouter()

@router.get("/analyze/{token_address}", response_model=AnalyzeResponse)
def analyze(token_address: str, lp_token: str = None):
    return analyze_token(token_address, lp_token_address=lp_token)
