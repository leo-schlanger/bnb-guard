import requests
from config import BSCSCAN_API_KEY

def analyze_onchain(metadata: dict) -> dict:
    result = {
        "deployer_address": metadata.get("deployer_address"),
        "deployer_token_count": metadata.get("deployer_token_count"),
        "deployer_flagged": False,
        "top_holder_concentration": None,
        "lp_locked": False,
        "lp_percent_locked": None,
        "lp_info": metadata.get("lp_info", {}),
        "alerts": []
    }

    # 🚨 Detect suspicious deployer
    if metadata.get("deployer_token_count", 0) > 5:
        result["deployer_flagged"] = True
        result["alerts"].append("🚨 Deployer created many tokens")

    # 📊 Holder concentration
    holders = metadata.get("holders", [])
    if holders:
        top_5 = sorted(holders, key=lambda x: x["percent"], reverse=True)[:5]
        total_top_5 = sum([h["percent"] for h in top_5])
        result["top_holder_concentration"] = round(total_top_5, 2)
        if total_top_5 > 50:
            result["alerts"].append("⚠️ Top 5 holders hold more than 50% of supply")

    # 🔒 Dynamic LP lock verification
    lp_info = metadata.get("lp_info", {})
    lp_percent_locked = lp_info.get("percent_locked")
    lp_address = lp_info.get("address")

    # Real call to is_lp_locked
    if lp_address:
        try:
            result["lp_locked"] = is_lp_locked(lp_address)
        except Exception as e:
            print(f"⚠️ Error verifying is_lp_locked: {e}")
            result["lp_locked"] = False
    else:
        result["lp_locked"] = False

    result["lp_percent_locked"] = lp_percent_locked

    if not result["lp_locked"] or (lp_percent_locked is not None and lp_percent_locked < 70):
        result["alerts"].append("❌ LP is not properly locked (>70%)")

    return result

def get_deployer_address(contract_address):
    url = (
        f"https://api.bscscan.com/api"
        f"?module=contract"
        f"&action=getcontractcreation"
        f"&contractaddresses={contract_address}"
        f"&apikey={BSCSCAN_API_KEY}"
    )
    
    print(f"🔍 [LOG] Calling BscScan: {url}")  # LOG
    
    response = requests.get(url)

    if not response.ok:
        print(f"❌ [LOG] HTTP Status: {response.status_code}")  # LOG
        raise Exception("❌ Error fetching contract creator")
    
    data = response.json()

    result = data.get("result", [])
    if not result or not result[0].get("contractCreator"):
        print("⚠️ [LOG] Deployer not found in result[0]")  # LOG
        raise Exception("❌ Deployer not found")
    
    creator = result[0]["contractCreator"]
    print(f"✅ [LOG] Deployer found: {creator}")  # LOG
    return creator

def get_holder_distribution(token_address):
    url = (
        f"https://api.bscscan.com/api"
        f"?module=token"
        f"&action=tokenholderlist"
        f"&contractaddress={token_address}"
        f"&page=1"
        f"&offset=10"
        f"&apikey={BSCSCAN_API_KEY}"
    )

    print(f"🔍 [LOG] Fetching holders: {url}")  # LOG
    response = requests.get(url)

    if not response.ok:
        raise Exception("❌ Error fetching holder distribution")

    data = response.json()

    holders = data.get("result", [])
    if not holders or not isinstance(holders, list):
        raise Exception("❌ Unable to fetch holders")

    total_percentage = sum(float(holder.get("percentage", "0").replace("%", "")) for holder in holders[:5])
    return {
        "top5_percentage": round(total_percentage, 2),
        "holders": holders
    }

KNOWN_LOCKERS = [
    "0x1fE80fC86816B778B529D3C2a3830e44A6519A25",  # PinkLock
    "0x88b8e5f5b052f9b38b3b7f529d6bd0a09c84c3a0",  # Mudra Locker
    # other known lockers can be added here
]

def is_lp_locked(lp_token_address):
    url = (
        f"https://api.bscscan.com/api"
        f"?module=token"
        f"&action=tokenholderlist"
        f"&contractaddress={lp_token_address}"
        f"&page=1"
        f"&offset=10"
        f"&apikey={BSCSCAN_API_KEY}"
    )

    print(f"🔍 [LOG] Verifying LP lock: {url}")
    response = requests.get(url)
    if not response.ok:
        raise Exception("❌ Error fetching LP holders")

    data = response.json()
    holders = data.get("result", [])

    if not isinstance(holders, list):
        raise Exception("❌ Invalid result when fetching LP")

    for holder in holders:
        addr = holder.get("address", "").lower()
        if addr in [locker.lower() for locker in KNOWN_LOCKERS]:
            return True  

    return False 
