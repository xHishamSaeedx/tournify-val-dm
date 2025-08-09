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
                "player_ids": [
            "player_test_match_123_1",
            "player_test_match_123_2", 
            "player_test_match_123_3",
            "player_test_match_123_4",
            "player_test_match_123_5",
            "player_test_match_123_6",
            "player_test_match_123_7",
            "player_test_match_123_8",
            "player_test_match_123_9",
            "player_test_match_123_10"
                ],
                "expected_start_time": "2024-01-15T14:32:00",
                "expected_map": "Ascent"
            }
        },
        {
            "name": "Valid players but wrong time/map (should fail verification)",
            "data": {
                "player_ids": [
                    "player_test_match_123_1",
                    "player_test_match_123_2", 
                    "player_test_match_123_3"
                ],
                "expected_start_time": "2024-01-15T15:00:00",  # Wrong time
                "expected_map": "Bind"  # Wrong map
            }
        },
        {
            "name": "Players with no common match (should fail)",
            "data": {
                "player_ids": [
                    "player_no_match_1",
                    "player_no_match_2", 
                    "player_no_match_3"
                ],
                "expected_start_time": "2024-01-15T14:30:00",
                "expected_map": "Ascent"
            }
        },
        {
            "name": "Empty player list (should fail)",
            "data": {
                "player_ids": [],
                "expected_start_time": "2024-01-15T14:30:00",
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
                print(f"Match ID: {result['match_id']}")
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
