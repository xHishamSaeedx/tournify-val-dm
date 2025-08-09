# Leaderboard API Documentation

## Overview

After a match is completely validated, you can use the leaderboard endpoint to get the ranked results based on player performance.

## Endpoint

**POST** `/matches/leaderboard`

## Request Body

The endpoint uses the same request model as match validation:

```json
{
  "match_id": "string",
  "player_ids": ["string"],
  "expected_start_time": "datetime",
  "expected_map": "string"
}
```

## Response

```json
{
  "match_id": "string",
  "match_start_time": "datetime",
  "map": "string",
  "leaderboard": [
    {
      "rank": 1,
      "player_id": "string",
      "kills": 25,
      "average_combat_score": 320.5
    }
  ],
  "total_players": 10,
  "message": "string"
}
```

## Leaderboard Ranking Logic

Players are ranked based on the following criteria (in order of priority):

1. **Kills** (Primary factor) - Higher kills = higher rank
2. **Average Combat Score** (Secondary factor) - If kills are equal, higher ACS = higher rank

## Example Usage

```python
import httpx
import asyncio

async def get_leaderboard():
    request_data = {
        "match_id": "test_match_123",
        "player_ids": [
            "player_test_match_123_1",
            "player_test_match_123_2",
            "player_test_match_123_3"
        ],
        "expected_start_time": "2024-01-15T14:30:00",
        "expected_map": "Ascent"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/matches/leaderboard",
            json=request_data
        )

        if response.status_code == 200:
            leaderboard_data = response.json()
            print(f"Match: {leaderboard_data['match_id']}")
            print(f"Map: {leaderboard_data['map']}")

            for entry in leaderboard_data['leaderboard']:
                print(f"#{entry['rank']}: {entry['player_id']} - {entry['kills']} kills, {entry['average_combat_score']} ACS")

# Run the example
asyncio.run(get_leaderboard())
```

## Error Handling

The endpoint will return appropriate HTTP status codes:

- **400 Bad Request**: Match validation failed
- **404 Not Found**: Match details not found
- **500 Internal Server Error**: Server error during processing

## Integration Flow

1. **Match Validation**: First validate the match using `/matches/validate-match-history`
2. **Leaderboard Generation**: Use the validated match data to generate the leaderboard
3. **Result Processing**: Process the ranked results for tournament management

## Notes

- The endpoint automatically validates the match before generating the leaderboard
- If an alternative match ID is found during validation, it will be used for the leaderboard
- All player statistics are fetched from the match details
- The leaderboard is sorted in descending order (best performance first)
