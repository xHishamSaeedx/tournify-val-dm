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
            "name": "Valid match ID (should pass)",
            "data": {
                "match_id": "test_match_123",
                "player_ids": [
                    "player_test_match_123_1",
                    "player_test_match_123_2", 
                    "player_test_match_123_3",
                    "player_test_match_123_4",
                    "player_test_match_123_5"
                ]
            }
        },
        {
            "name": "Invalid match ID but with alternative (should detect host error)",
            "data": {
                "match_id": "wrong_match_id",
                "player_ids": [
                    "player_test_match_123_1",
                    "player_test_match_123_2", 
                    "player_test_match_123_3",
                    "player_test_match_123_4",
                    "player_test_match_123_5"
                ]
            }
        },
        {
            "name": "Completely invalid match ID (should fail)",
            "data": {
                "match_id": "completely_wrong_id",
                "player_ids": [
                    "player_test_match_123_1",
                    "player_test_match_123_2", 
                    "player_test_match_123_3"
                ]
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
                print(f"Host error detected: {result['host_error']}")
                if result.get('alternative_match_id'):
                    print(f"Alternative match ID: {result['alternative_match_id']}")
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
