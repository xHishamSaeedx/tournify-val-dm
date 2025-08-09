#!/usr/bin/env python3
"""
Test script for the match validation functionality.
This script demonstrates how to use the new endpoint to validate match history.
"""

import requests
import json
from datetime import datetime

def test_match_validation():
    """Test the match validation endpoint."""
    
    # Test cases
    test_cases = [
        {
            "name": "Valid players with common match (should pass)",
            "data": {
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
                "expected_start_time": "2025-08-09T11:58:27",
                "expected_map": "Ascent"
            }
        },
        {
            "name": "Valid players but wrong time/map (should fail verification)",
            "data": {
                "players": [
                    {
                        "name": "Shafaath07",
                        "tag": "7372",
                        "region": "ap",
                        "platform": "pc"
                    },
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
                "expected_start_time": "2025-08-09T11:58:27",  # Wrong time
                "expected_map": "Bind"  # Wrong map
            }
        },
        {
            "name": "Players with no common match (should fail)",
            "data": {
                "players": [
                    {
                        "name": "PlayerNoMatch1",
                        "tag": "1234",
                        "region": "ap",
                        "platform": "pc"
                    },
                    {
                        "name": "PlayerNoMatch2",
                        "tag": "5678",
                        "region": "ap",
                        "platform": "pc"
                    }
                ],
                "expected_start_time": "2025-08-09T11:58:27",
                "expected_map": "Ascent"
            }
        },
        {
            "name": "Empty player list (should fail)",
            "data": {
                "players": [],
                "expected_start_time": "2025-08-09T11:58:27",
                "expected_map": "Ascent"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"Test Case {i}: {test_case['name']}")
        print(f"{'='*60}")
        
        try:
            # Make request to the validation endpoint
            response = requests.post(
                "http://localhost:8000/matches/validate-match-history",
                json=test_case['data'],
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Match validation successful!")
                print(f"🎯 Match ID found: {result['match_id']}")
                print(f"Percentage with match: {result['percentage_with_match']:.1f}%")
                print(f"Validation passed: {result['validation_passed']}")
                print(f"Match details verified: {result['match_details_verified']}")
                if result.get('alternative_match_id'):
                    print(f"Alternative match ID: {result['alternative_match_id']}")
                if result.get('time_verification_passed') is not None:
                    print(f"Time verification passed: {result['time_verification_passed']}")
                if result.get('map_verification_passed') is not None:
                    print(f"Map verification passed: {result['map_verification_passed']}")
                print(f"Message: {result['message']}")
                print(f"Players with match: {result['players_with_match']}")
                print(f"Players without match: {result['players_without_match']}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text)
                
        except requests.exceptions.ConnectionError:
            print("❌ Error: Could not connect to the server. Make sure both servers are running:")
            print("  - Main app on port 8000")
            print("  - Riot dummy server on port 8001")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("Testing match validation functionality...")
    print("Make sure both servers are running:")
    print("  - Main app: python run.py")
    print("  - Riot dummy server: cd riot_dummy_server && python main.py")
    print()
    test_match_validation()
