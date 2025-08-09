from fastapi import APIRouter, HTTPException
from app.models import MatchRequest, MatchResponse
from datetime import datetime
import uuid

router = APIRouter(prefix="/matches", tags=["matches"])

@router.post("/", response_model=MatchResponse)
async def create_match(match_request: MatchRequest):
    """
    Create a new match with the provided details.
    
    Args:
        match_request: MatchRequest object containing player_ids, match_start_time, 
                      match_map, and expected_match_id
    
    Returns:
        MatchResponse object with match details and status
    """
    try:
        # Validate the request
        if not match_request.player_ids:
            raise HTTPException(status_code=400, detail="Player IDs list cannot be empty")
        
        if not match_request.match_map:
            raise HTTPException(status_code=400, detail="Match map cannot be empty")
        
        # Generate a unique match ID (you might want to use the expected_match_id instead)
        match_id = str(uuid.uuid4())
        
        # Here you would typically save the match to a database
        # For now, we'll just return the match details
        
        return MatchResponse(
            match_id=match_id,
            player_ids=match_request.player_ids,
            match_start_time=match_request.match_start_time,
            match_map=match_request.match_map,
            status="created",
            message=f"Match created successfully with ID: {match_id}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(match_id: str):
    """
    Get match details by match ID.
    
    Args:
        match_id: The unique identifier for the match
    
    Returns:
        MatchResponse object with match details
    """
    # Here you would typically fetch the match from a database
    # For now, we'll return a mock response
    raise HTTPException(status_code=404, detail="Match not found")
