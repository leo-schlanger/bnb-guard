import os
from dotenv import load_dotenv

load_dotenv()

BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY")

if not BSCSCAN_API_KEY:
    raise RuntimeError("❌ BSCSCAN_API_KEY não definida no .env")

BSC_RPC_URL = "https://bsc-dataseed.binance.org"
