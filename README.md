# Tournify Valorant DM API

A FastAPI application for managing Valorant deathmatch tournaments.

## Features

- Create matches with player IDs, start time, map, and expected match ID
- RESTful API with automatic documentation
- Input validation using Pydantic models
- Modular code structure with routers

## Project Structure

```
tournify-val-dm/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── models.py            # Pydantic models
│   └── routers/
│       ├── __init__.py
│       └── matches.py       # Match-related endpoints
├── requirements.txt          # Python dependencies
└── README.md               # This file
```

## Setup

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**

   ```bash
   # Option 1: Using uvicorn directly
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

   # Option 2: Using Python
   python -m app.main
   ```

3. **Access the API:**
   - API: http://localhost:8000
   - Interactive documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

### Health Check

- `GET /` - Root endpoint
- `GET /health` - Health check endpoint

### Matches

- `POST /matches/` - Create a new match
- `GET /matches/{match_id}` - Get match details (placeholder)

## Example Usage

### Create a Match

```bash
curl -X POST "http://localhost:8000/matches/" \
     -H "Content-Type: application/json" \
     -d '{
       "player_ids": ["player1", "player2", "player3"],
       "match_start_time": "2024-01-15T14:30:00",
       "match_map": "Ascent",
       "expected_match_id": "match_123"
     }'
```

### Request Body Schema

```json
{
  "player_ids": ["string"],
  "match_start_time": "2024-01-15T14:30:00",
  "match_map": "string",
  "expected_match_id": "string"
}
```

### Response Schema

```json
{
  "match_id": "uuid-string",
  "player_ids": ["string"],
  "match_start_time": "2024-01-15T14:30:00",
  "match_map": "string",
  "status": "created",
  "message": "Match created successfully with ID: uuid-string"
}
```

## Development

The application uses a modular structure:

- **Models** (`app/models.py`): Pydantic models for request/response validation
- **Routers** (`app/routers/`): Separate router files for different API sections
- **Main** (`app/main.py`): FastAPI application configuration and router inclusion

## Future Enhancements

- Database integration (SQLAlchemy, PostgreSQL)
- Authentication and authorization
- Match status tracking
- Player management
- Tournament bracket generation
- Real-time updates with WebSockets
