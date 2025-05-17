import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from fastapi import FastAPI
from app.routes.analyze import router as analyze_router
from app.routes.audit import router as audit_router

app = FastAPI(
    title="BNBGuard API",
    version="0.1.0",
    description="Análise de risco automatizada para tokens da BNB Chain"
)

app.include_router(analyze_router)
app.include_router(audit_router)
