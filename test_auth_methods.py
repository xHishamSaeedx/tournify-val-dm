#!/usr/bin/env python3
"""
Test different authentication methods for the Henrik.Dev API
"""

import httpx
import asyncio
import urllib.parse
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

async def test_auth_methods():
    """Test different authentication methods."""
    
    # Test player
    player = {"name": "HystericalBat", "tag": "3571", "region": "ap", "platform": "pc"}
    base_url = "https://api.henrikdev.xyz/valorant/v4/matches"
    
    # Get API key from environment
    api_key = os.getenv("RIOT_APIKEY")
    print(f"🔑 API Key: {api_key}")
    
    # URL encode the player name
    encoded_name = urllib.parse.quote(player['name'])
    url = f"{base_url}/{player['region']}/{player['platform']}/{encoded_name}/{player['tag']}?mode=custom"
    
    print(f"🌐 URL: {url}")
    
    async with httpx.AsyncClient() as client:
        # Test different authentication methods
        auth_methods = [
            {"Authorization": f"Bearer {api_key}"},
            {"Authorization": api_key},
            {"X-API-Key": api_key},
            {"api-key": api_key},
            {"key": api_key},
            {}  # No auth
        ]
        
        for i, headers in enumerate(auth_methods):
            print(f"\n{'='*60}")
            print(f"Test {i+1}: {list(headers.keys()) if headers else 'No auth'}")
            print(f"{'='*60}")
            
            try:
                response = await client.get(url, headers=headers, timeout=10.0)
                print(f"📡 Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ SUCCESS! Response status: {data.get('status')}")
                    matches = data.get("data", [])
                    print(f"📋 Found {len(matches)} matches")
                    if matches:
                        metadata = matches[0].get("metadata", {})
                        print(f"🎯 Match ID: {metadata.get('match_id')}")
                    break
                else:
                    print(f"❌ Error: {response.text}")
                    
            except Exception as e:
                print(f"❌ Exception: {e}")

if __name__ == "__main__":
    print("Testing different authentication methods...")
    asyncio.run(test_auth_methods())
