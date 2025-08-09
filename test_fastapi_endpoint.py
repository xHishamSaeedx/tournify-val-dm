#!/usr/bin/env python3
"""
Test the FastAPI endpoint directly
"""

import requests
import json

def test_fastapi_endpoint():
    """Test the FastAPI validate-match-history endpoint."""
    
    # Test data - just the two players that we know have the common match
    test_data = {
        "players": [
            {
                "name": "HystericalBat",
                "tag": "3571",
                "region": "ap",
                "platform": "pc"
            },
            {
                "name": "i miss her",
                "tag": "01819",
                "region": "ap",
                "platform": "pc"
            }
        ],
        "expected_start_time": "2025-08-09T15:58:27",
        "expected_map": "Ascent"
    }
    
    print("🧪 Testing FastAPI endpoint...")
    print(f"📤 Request data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            "http://localhost:8000/matches/validate-match-history",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Response received:")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Error response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on port 8000")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_fastapi_endpoint()
