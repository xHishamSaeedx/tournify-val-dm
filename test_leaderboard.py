import asyncio
import httpx
from datetime import datetime

async def test_leaderboard():
    """Test the leaderboard functionality by first validating the match, then getting the leaderboard."""
    
    # Test data - using players that we know have a common match in the dummy server
    test_request = {
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
        "expected_start_time": "2024-01-15T14:30:00",
        "expected_map": "Ascent"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # Step 1: First validate the match
            print("🔍 Step 1: Validating match...")
            validation_response = await client.post(
                "http://localhost:8000/matches/validate-match-history",
                json=test_request,
                timeout=30.0
            )
            
            if validation_response.status_code != 200:
                print(f"❌ Match validation failed with status {validation_response.status_code}")
                print(f"Error: {validation_response.text}")
                return
            
            validation_data = validation_response.json()
            print("✅ Match validation successful!")
            print(f"Match ID: {validation_data['match_id']}")
            print(f"Validation Passed: {validation_data['validation_passed']}")
            print(f"Players with match: {len(validation_data['players_with_match'])}/{len(test_request['player_ids'])}")
            print(f"Percentage: {validation_data['percentage_with_match']:.1f}%")
            print(f"Message: {validation_data['message']}")
            
            if not validation_data['validation_passed']:
                print("❌ Match validation failed, cannot proceed to leaderboard")
                return
            
            # Step 2: Get the leaderboard using the validated match
            print("\n🏆 Step 2: Getting leaderboard...")
            leaderboard_response = await client.post(
                "http://localhost:8000/matches/leaderboard",
                json=test_request,
                timeout=30.0
            )
            
            if leaderboard_response.status_code == 200:
                leaderboard_data = leaderboard_response.json()
                print("✅ Leaderboard generation successful!")
                print(f"Match ID: {leaderboard_data['match_id']}")
                print(f"Map: {leaderboard_data['map']}")
                print(f"Total Players: {leaderboard_data['total_players']}")
                print(f"Message: {leaderboard_data['message']}")
                print("\n🏆 Leaderboard:")
                print("Rank | Player ID | Kills | Average Combat Score")
                print("-" * 50)
                
                for entry in leaderboard_data['leaderboard']:
                    print(f"{entry['rank']:4} | {entry['player_id']:20} | {entry['kills']:5} | {entry['average_combat_score']:8.2f}")
                    
            else:
                print(f"❌ Leaderboard generation failed with status {leaderboard_response.status_code}")
                print(f"Error: {leaderboard_response.text}")
                
    except Exception as e:
        print(f"❌ Error testing leaderboard: {str(e)}")

if __name__ == "__main__":
    print("Testing leaderboard functionality with proper validation flow...")
    asyncio.run(test_leaderboard())
