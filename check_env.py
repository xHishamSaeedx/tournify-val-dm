#!/usr/bin/env python3
"""
Check environment variables and .env file
"""

import os
from dotenv import load_dotenv

print("🔍 Checking environment variables...")

# Check if .env file exists
if os.path.exists('.env'):
    print("✅ .env file found")
    with open('.env', 'r') as f:
        print("📄 .env file contents:")
        for line in f:
            if line.strip() and not line.startswith('#'):
                print(f"   {line.strip()}")
else:
    print("❌ .env file not found")

# Load .env file
print("\n🔄 Loading .env file...")
load_dotenv()

# Check environment variables
riot_api_key = os.getenv("RIOT_APIKEY")
print(f"\n🔑 RIOT_APIKEY: {'Set' if riot_api_key else 'Not found'}")
if riot_api_key:
    print(f"   Preview: {riot_api_key[:10]}...")

# Check other environment variables
print(f"\n📋 All environment variables:")
for key, value in os.environ.items():
    if 'RIOT' in key or 'API' in key or 'KEY' in key:
        print(f"   {key}: {'Set' if value else 'Not set'}")
