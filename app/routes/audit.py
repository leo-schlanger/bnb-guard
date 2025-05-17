import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from fastapi import APIRouter
from app.schemas.audit_response import AuditResponse
from app.services.auditor import audit_token

router = APIRouter()

@router.get("/audit/{token_address}", response_model=AuditResponse)
def audit_route(token_address: str, lp_token: str = None):
    data = audit_token(token_address)
    return data
