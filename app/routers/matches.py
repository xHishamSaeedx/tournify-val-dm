from fastapi import APIRouter, HTTPException
from app.models import MatchRequest, MatchResponse, MatchValidationRequest, MatchValidationResponse, PlayerStats, LeaderboardEntry, LeaderboardResponse
from datetime import datetime, timedelta
from typing import List
import uuid
import httpx
import asyncio
from collections import Counter

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

@router.post("/validate-match-history", response_model=MatchValidationResponse)
async def validate_match_history(request: MatchValidationRequest):
    """
    Validate if players have the match ID in their match history.
    If 70% don't have the original match ID, check for alternative match IDs that 70% share.
    After confirming the correct match ID, fetch match details and verify start time and map.
    
    Args:
        request: MatchValidationRequest containing match_id, player_ids, expected_start_time, and expected_map
    
    Returns:
        MatchValidationResponse with validation results
    """
    try:
        # Validate the request
        if not request.player_ids:
            raise HTTPException(status_code=400, detail="Player IDs list cannot be empty")
        
        if not request.match_id:
            raise HTTPException(status_code=400, detail="Match ID cannot be empty")
        
        # Check each player's match history
        players_with_match = []
        players_without_match = []
        all_player_matches = {}
        
        async with httpx.AsyncClient() as client:
            # Check each player's match history concurrently
            tasks = []
            for player_id in request.player_ids:
                task = get_player_match_history(client, player_id)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(results):
                player_id = request.player_ids[i]
                if isinstance(result, Exception):
                    # If there's an error checking the player, count them as not having the match
                    players_without_match.append(player_id)
                    all_player_matches[player_id] = []
                else:
                    matches = result
                    all_player_matches[player_id] = matches
                    if request.match_id in matches:
                        players_with_match.append(player_id)
                    else:
                        players_without_match.append(player_id)
            
            # Calculate percentage for original match ID
            total_players = len(request.player_ids)
            percentage_with_match = (len(players_with_match) / total_players) * 100 if total_players > 0 else 0
            
            # Check if 70% threshold is met for original match ID
            validation_passed = percentage_with_match >= 70
            alternative_match_id = None
            host_error = False
            final_match_id = request.match_id
            
            # If original validation failed, check for alternative match IDs
            if not validation_passed:
                alternative_match_id, alternative_percentage = find_alternative_match_id(all_player_matches, total_players)
                
                if alternative_match_id:
                    # Found an alternative match ID that 70% of players share
                    validation_passed = True
                    host_error = True  # Indicate this is due to host error
                    final_match_id = alternative_match_id
                    message = f"Original match ID '{request.match_id}' not found in 70% of players' history. However, found alternative match ID '{alternative_match_id}' that {alternative_percentage:.1f}% of players share. This suggests a host error."
                else:
                    # No alternative match ID found
                    message = f"Validation failed! Only {percentage_with_match:.1f}% of players have the match '{request.match_id}' in their history (70% required). No alternative match ID found that 70% of players share."
                    return MatchValidationResponse(
                        match_id=request.match_id,
                        players_with_match=players_with_match,
                        players_without_match=players_without_match,
                        percentage_with_match=percentage_with_match,
                        validation_passed=False,
                        message=message,
                        alternative_match_id=None,
                        host_error=False,
                        match_details_verified=False,
                        time_verification_passed=None,
                        map_verification_passed=None
                    )
            else:
                message = f"Validation passed! {percentage_with_match:.1f}% of players have the match in their history."
            
            # If validation passed (either original or alternative), verify match details
            if validation_passed:
                # Create a new client for match details verification
                async with httpx.AsyncClient() as verify_client:
                    match_details_verified, time_verification_passed, map_verification_passed, verification_message = await verify_match_details(verify_client, final_match_id, request.expected_start_time, request.expected_map)
                
                if not match_details_verified:
                    validation_passed = False
                    message = verification_message
                else:
                    message += f" Match details verified successfully."
            
            return MatchValidationResponse(
                match_id=request.match_id,
                players_with_match=players_with_match,
                players_without_match=players_without_match,
                percentage_with_match=percentage_with_match,
                validation_passed=validation_passed,
                message=message,
                alternative_match_id=alternative_match_id,
                host_error=host_error,
                match_details_verified=match_details_verified if validation_passed else False,
                time_verification_passed=time_verification_passed,
                map_verification_passed=map_verification_passed
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

async def get_player_match_history(client: httpx.AsyncClient, player_id: str) -> list:
    """
    Get a player's match history.
    
    Args:
        client: HTTP client for making requests
        player_id: The player ID to check
    
    Returns:
        List of match IDs in the player's history
    """
    try:
        # Make request to riot dummy server (port 8001)
        response = await client.post(
            "http://localhost:8001/matches/player-history",
            json={"player_id": player_id},
            timeout=10.0
        )
        
        if response.status_code == 200:
            data = response.json()
            recent_matches = data.get("recent_matches", [])
            return recent_matches
        else:
            # If the request fails, return empty list
            return []
            
    except Exception:
        # If there's any error, return empty list
        return []

def find_alternative_match_id(all_player_matches: dict, total_players: int) -> tuple:
    """
    Find an alternative match ID that 70% of players share.
    
    Args:
        all_player_matches: Dictionary mapping player_id to list of match IDs
        total_players: Total number of players
    
    Returns:
        Tuple of (alternative_match_id, percentage) or (None, 0) if not found
    """
    # Collect all match IDs from all players
    all_match_ids = []
    for player_matches in all_player_matches.values():
        all_match_ids.extend(player_matches)
    
    # Count occurrences of each match ID
    match_counter = Counter(all_match_ids)
    
    # Find match IDs that appear in at least 70% of players
    required_count = int(total_players * 0.7)
    
    for match_id, count in match_counter.most_common():
        if count >= required_count:
            percentage = (count / total_players) * 100
            return match_id, percentage
    
    return None, 0

async def check_player_match_history(client: httpx.AsyncClient, player_id: str, match_id: str) -> bool:
    """
    Check if a player has the match ID in their match history.
    
    Args:
        client: HTTP client for making requests
        player_id: The player ID to check
        match_id: The match ID to look for
    
    Returns:
        True if the player has the match in their history, False otherwise
    """
    try:
        # Make request to riot dummy server (port 8001)
        response = await client.post(
            "http://localhost:8001/matches/player-history",
            json={"player_id": player_id},
            timeout=10.0
        )
        
        if response.status_code == 200:
            data = response.json()
            recent_matches = data.get("recent_matches", [])
            return match_id in recent_matches
        else:
            # If the request fails, assume the player doesn't have the match
            return False
            
    except Exception:
        # If there's any error, assume the player doesn't have the match
        return False

async def verify_match_details(client: httpx.AsyncClient, match_id: str, expected_start_time: datetime, expected_map: str) -> tuple:
    """
    Verify match details by fetching match data and checking start time and map.
    
    Args:
        client: HTTP client for making requests
        match_id: The match ID to verify
        expected_start_time: Expected match start time
        expected_map: Expected map name
    
    Returns:
        Tuple of (verified, time_passed, map_passed, message)
    """
    try:
        # Fetch match details from riot dummy server
        response = await client.post(
            "http://localhost:8001/matches/",
            json={"match_id": match_id},
            timeout=10.0
        )
        
        if response.status_code != 200:
            return False, None, None, f"Failed to fetch match details for match ID '{match_id}'"
        
        data = response.json()
        actual_start_time_str = data.get("match_start_time")
        actual_map = data.get("map")
        
        if not actual_start_time_str or not actual_map:
            return False, None, None, f"Invalid match data received for match ID '{match_id}'"
        
        # Parse the actual start time - handle different datetime formats
        try:
            # Try parsing as ISO format first
            if 'T' in actual_start_time_str:
                # ISO format: "2024-01-15T14:30:00" or "2024-01-15T14:30:00.000000"
                actual_start_time = datetime.fromisoformat(actual_start_time_str.replace('Z', '+00:00'))
            else:
                # Try other common formats
                actual_start_time = datetime.fromisoformat(actual_start_time_str)
        except ValueError as e:
            return False, None, None, f"Invalid start time format in match data for match ID '{match_id}': {actual_start_time_str}"
        
        # Verify start time (within ±5 minutes)
        time_difference = abs((actual_start_time - expected_start_time).total_seconds())
        time_verification_passed = time_difference <= 300  # 5 minutes = 300 seconds
        
        # Verify map (case-insensitive)
        map_verification_passed = actual_map.lower() == expected_map.lower()
        
        # Both must pass for overall verification
        verified = time_verification_passed and map_verification_passed
        
        if not verified:
            message_parts = []
            if not time_verification_passed:
                message_parts.append(f"start time mismatch (expected: {expected_start_time}, actual: {actual_start_time})")
            if not map_verification_passed:
                message_parts.append(f"map mismatch (expected: {expected_map}, actual: {actual_map})")
            
            message = f"Match details verification failed: {', '.join(message_parts)}"
        else:
            message = "Match details verified successfully"
        
        return verified, time_verification_passed, map_verification_passed, message
        
    except Exception as e:
        return False, None, None, f"Error verifying match details: {str(e)}"

async def get_match_details(client: httpx.AsyncClient, match_id: str) -> dict:
    """
    Fetch match details including player statistics from the riot dummy server.
    
    Args:
        client: HTTP client for making requests
        match_id: The match ID to fetch details for
    
    Returns:
        Dictionary containing match details and player statistics
    """
    try:
        response = await client.post(
            "http://localhost:8001/matches/",
            json={"match_id": match_id},
            timeout=10.0
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=404, detail=f"Match details not found for match ID: {match_id}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching match details: {str(e)}")

def create_leaderboard(players: List[PlayerStats]) -> List[LeaderboardEntry]:
    """
    Create a leaderboard from player statistics, sorted by kills first, then by average combat score.
    
    Args:
        players: List of PlayerStats objects
    
    Returns:
        List of LeaderboardEntry objects sorted by rank
    """
    # Sort players by kills (descending), then by average combat score (descending)
    sorted_players = sorted(players, key=lambda x: (x.kills, x.average_combat_score), reverse=True)
    
    leaderboard = []
    for i, player in enumerate(sorted_players):
        entry = LeaderboardEntry(
            rank=i + 1,
            player_id=player.player_id,
            kills=player.kills,
            average_combat_score=player.average_combat_score
        )
        leaderboard.append(entry)
    
    return leaderboard

@router.post("/leaderboard", response_model=LeaderboardResponse)
async def get_match_leaderboard(request: MatchValidationRequest):
    """
    Get the leaderboard for a validated match. This endpoint first validates the match
    and then returns the leaderboard sorted by kills (primary) and average combat score (secondary).
    
    Args:
        request: MatchValidationRequest containing match validation details
    
    Returns:
        LeaderboardResponse with sorted leaderboard and match details
    """
    try:
        # First validate the match
        validation_response = await validate_match_history(request)
        
        if not validation_response.validation_passed:
            raise HTTPException(
                status_code=400, 
                detail=f"Match validation failed: {validation_response.message}"
            )
        
        # Use the final match ID (original or alternative)
        final_match_id = validation_response.alternative_match_id or request.match_id
        
        # Fetch match details
        async with httpx.AsyncClient() as client:
            match_details = await get_match_details(client, final_match_id)
        
        # Extract player statistics
        players_data = match_details.get("players", [])
        players = [PlayerStats(**player_data) for player_data in players_data]
        
        # Create leaderboard
        leaderboard = create_leaderboard(players)
        
        # Parse match start time
        match_start_time_str = match_details.get("match_start_time")
        if 'T' in match_start_time_str:
            match_start_time = datetime.fromisoformat(match_start_time_str.replace('Z', '+00:00'))
        else:
            match_start_time = datetime.fromisoformat(match_start_time_str)
        
        return LeaderboardResponse(
            match_id=final_match_id,
            match_start_time=match_start_time,
            map=match_details.get("map", ""),
            leaderboard=leaderboard,
            total_players=len(players),
            message=f"Leaderboard generated successfully for match '{final_match_id}'. {len(players)} players ranked by kills and average combat score."
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
