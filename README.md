# Tournify Valorant DM API

A FastAPI-based application for managing Valorant deathmatch tournaments.

## Features

- Create and manage matches
- Validate match history for players
- Detect host errors by finding alternative match IDs
- Integration with Riot dummy server for match data

## API Endpoints

### Match Management

#### POST `/matches/`

Create a new match with player details.

**Request Body:**

```json
{
  "player_ids": ["player1", "player2"],
  "match_start_time": "2024-01-15T14:30:00",
  "match_map": "Ascent",
  "expected_match_id": "match_123"
}
```

#### GET `/matches/{match_id}`

Get match details by match ID.

### Match History Validation

#### POST `/matches/validate-match-history`

Validate if players have a specific match ID in their match history. If 70% of players don't have the original match ID, the system will check for alternative match IDs that 70% of players share to detect host errors.

**Request Body:**

```json
{
  "match_id": "test_match_123",
  "player_ids": ["player1", "player2", "player3"]
}
```

**Response Examples:**

**Successful Validation:**

```json
{
  "match_id": "test_match_123",
  "players_with_match": ["player1", "player2", "player3"],
  "players_without_match": [],
  "percentage_with_match": 100.0,
  "validation_passed": true,
  "message": "Validation passed! 100.0% of players have the match in their history.",
  "alternative_match_id": null,
  "host_error": false
}
```

**Host Error Detected:**

```json
{
  "match_id": "wrong_match_id",
  "players_with_match": [],
  "players_without_match": [
    "player1",
    "player2",
    "player3",
    "player4",
    "player5"
  ],
  "percentage_with_match": 0.0,
  "validation_passed": true,
  "message": "Original match ID 'wrong_match_id' not found in 70% of players' history. However, found alternative match ID 'test_match_123' that 100.0% of players share. This suggests a host error.",
  "alternative_match_id": "test_match_123",
  "host_error": true
}
```

**Validation Failed:**

```json
{
  "match_id": "completely_wrong_id",
  "players_with_match": [],
  "players_without_match": ["player1", "player2", "player3"],
  "percentage_with_match": 0.0,
  "validation_passed": false,
  "message": "Validation failed! Only 0.0% of players have the match 'completely_wrong_id' in their history (70% required). No alternative match ID found that 70% of players share.",
  "alternative_match_id": null,
  "host_error": false
}
```

**Validation Logic:**

- Checks each player's match history via the Riot dummy server (port 8001)
- Calculates the percentage of players who have the match ID in their history
- If 70% or more players have the match → **Validation Passed**
- If less than 70% have the match → Check for alternative match IDs that 70% share
  - If alternative found → **Validation Passed** with `host_error: true`
  - If no alternative found → **Validation Failed**

## Setup and Running

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Start the main application (port 8000):

   ```bash
   python run.py
   ```

3. Start the Riot dummy server (port 8001):

   ```bash
   cd riot_dummy_server
   python main.py
   ```

4. Test the functionality:

   ```bash
   python test_match_validation.py
   ```

## Architecture

- **Main App (Port 8000)**: Handles match creation and validation
- **Riot Dummy Server (Port 8001)**: Provides mock match data and player history
- **Async HTTP Client**: Uses `httpx` for concurrent requests to check player histories
- **Host Error Detection**: Automatically detects when the wrong match ID was provided but players share a common match

## Dependencies

- FastAPI
- Uvicorn
- Pydantic
- httpx (for async HTTP requests)
- requests (for testing)
