from fastapi import APIRouter, HTTPException
from ..models import MatchRequest, MatchResponse, PlayerRequest, PlayerMatchHistory
from ..services import MatchService

router = APIRouter(prefix="/matches", tags=["matches"])


@router.post("/", response_model=MatchResponse)
async def get_match_data(request: MatchRequest):
    """
    Get dummy match data for a given match ID.
    
    Args:
        request: MatchRequest containing the match_id
        
    Returns:
        MatchResponse with 10 dummy players and their stats
    """
    try:
        # Generate dummy data using the service
        match_data = MatchService.generate_dummy_players(request.match_id)
        return match_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating match data: {str(e)}")


@router.post("/player-history", response_model=PlayerMatchHistory)
async def get_player_match_history(request: PlayerRequest):
    """
    Get recent match history for a player.
    
    Args:
        request: PlayerRequest containing the player_id
        
    Returns:
        PlayerMatchHistory with 5 recent match IDs
    """
    try:
        # Get player match history using the service
        player_history = MatchService.get_player_match_history(request.player_id)
        return player_history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting player match history: {str(e)}")
