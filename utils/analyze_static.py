import re

DANGEROUS_FUNCTIONS = [
    "mint",
    "setFee",
    "blacklist",
    "pause",
    "excludeFromFee",
    "onlyOwner",
    "renounceOwnership",
    "transferOwnership",
]

def analyze_static_code(source_code: str):
    findings = []
    for func in DANGEROUS_FUNCTIONS:
        if re.search(rf"\b{func}\b", source_code):
            findings.append(f"⚠️ Função {func} detectada")
    return findings
