#!/usr/bin/env python3
"""
Direct API test to debug the match history issue.
"""

import httpx
import asyncio
import urllib.parse
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

async def test_player_api():
    """Test the player API directly."""
    
    # Test players
    players = [
        {"name": "Shafaath07", "tag": "7372", "region": "ap", "platform": "pc"},
        {"name": "HystericalBat", "tag": "3571", "region": "ap", "platform": "pc"},
        {"name": "i miss her", "tag": "01819", "region": "ap", "platform": "pc"}
    ]
    
    base_url = "https://api.henrikdev.xyz/valorant/v4/matches"
    
    # Get API key from environment
    api_key = os.getenv("RIOT_APIKEY")
    print(f"🔍 Environment variables loaded:")
    print(f"   RIOT_APIKEY: {'Set' if api_key else 'Not found'}")
    if api_key:
        print(f"   API Key preview: {api_key[:10]}...")
    else:
        print("⚠️ No RIOT_APIKEY found in environment variables")
    
    async with httpx.AsyncClient() as client:
        for player in players:
            print(f"\n{'='*60}")
            print(f"Testing player: {player['name']}#{player['tag']}")
            print(f"{'='*60}")
            
            # URL encode the player name
            encoded_name = urllib.parse.quote(player['name'])
            url = f"{base_url}/{player['region']}/{player['platform']}/{encoded_name}/{player['tag']}?mode=custom"
            
            print(f"🌐 URL: {url}")
            
            # Add API key to headers - use correct format
            headers = {}
            if api_key:
                headers["Authorization"] = api_key  # No Bearer prefix needed
                print(f"🔑 Using API key: {api_key[:10]}...")
            else:
                print("⚠️ No API key found")
            
            try:
                response = await client.get(url, headers=headers, timeout=10.0)
                print(f"📡 Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"📊 Response status: {data.get('status')}")
                    
                    matches = data.get("data", [])
                    print(f"📋 Found {len(matches)} matches")
                    
                    if matches:
                        print(f"📋 First match keys: {list(matches[0].keys())}")
                        metadata = matches[0].get("metadata", {})
                        print(f"📋 Metadata keys: {list(metadata.keys())}")
                        print(f"📋 Match ID: {metadata.get('match_id')}")
                        print(f"📋 Started at: {metadata.get('started_at')}")
                        print(f"📋 Map: {metadata.get('map', {}).get('name')}")
                    else:
                        print("❌ No matches found")
                else:
                    print(f"❌ Error response: {response.text}")
                    
            except Exception as e:
                print(f"❌ Exception: {e}")

if __name__ == "__main__":
    print("Testing API directly...")
    asyncio.run(test_player_api())
