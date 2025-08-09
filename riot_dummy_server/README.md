# Riot Dummy Server

A FastAPI application that provides dummy match data for testing purposes.

## Project Structure

```
riot_dummy_server/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app configuration
│   ├── models.py        # Pydantic models
│   ├── services.py      # Business logic
│   └── routers/
│       ├── __init__.py
│       └── matches.py   # Match-related endpoints
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

### Option 1: Using Python directly

```bash
python main.py
```

### Option 2: Using uvicorn directly

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The server will start on `http://localhost:8000`

## API Endpoints

### GET /

- **Description**: Root endpoint with basic information
- **Response**: Application info and available endpoints

### GET /health

- **Description**: Health check endpoint
- **Response**: `{"status": "healthy"}`

### POST /matches/

- **Description**: Get dummy match data with player statistics
- **Request Body**:
  ```json
  {
    "match_id": "your_match_id_here"
  }
  ```
- **Response**:
  ```json
  {
    "match_id": "your_match_id_here",
    "players": [
      {
        "player_id": "player_your_match_id_here_1",
        "kills": 15,
        "average_combat_score": 245.67
      }
      // ... 9 more players
    ]
  }
  ```

## API Documentation

Once the server is running, you can access:

- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc

## Example Usage

```bash
curl -X POST "http://localhost:8000/matches/" \
     -H "Content-Type: application/json" \
     -d '{"match_id": "test_match_123"}'
```

This will return dummy data for 10 players with random kills (0-25) and average combat scores (150-350).
