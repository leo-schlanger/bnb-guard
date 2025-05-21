import os
from app.core.config import settings

print("=== Environment Variables ===")
print(f"LOG_LEVEL from env: {os.getenv('LOG_LEVEL')}")
print(f"BSCSCAN_API_KEY from env: {os.getenv('BSCSCAN_API_KEY')}")
print("\n=== Settings ===")
print(f"LOG_LEVEL: {settings.LOG_LEVEL}")
print(f"BSCSCAN_API_KEY: {settings.BSCSCAN_API_KEY}")
print(f"DEBUG: {settings.DEBUG}")
print(f"ENV: {settings.ENV}")

# Verify if .env is being loaded
print("\n=== .env file check ===")
try:
    with open('.env', 'r') as f:
        print(".env file exists and is readable")
except Exception as e:
    print(f"Error reading .env file: {e}")
