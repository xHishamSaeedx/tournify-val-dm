from fastapi import APIRouter, HTTPException
from app.models import MatchRequest, MatchResponse, MatchValidationRequest, MatchValidationResponse, PlayerStats, LeaderboardEntry, LeaderboardResponse, PlayerInfo
from datetime import datetime, timedelta, timezone
from typing import List
import uuid
import httpx
import asyncio
from collections import Counter
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

router = APIRouter(prefix="/matches", tags=["matches"])

# Get the player match history URL from environment variable
VALO_PLAYER_MH_URL = os.getenv("VALO_PLAYER_MH_URL", "https://api.henrikdev.xyz/valorant/v4/matches")

# Get the match details URL from environment variable
VALO_MATCH_DETAILS_URL = os.getenv("VALO_MATCH_DETAILS_URL", "https://api.henrikdev.xyz/valorant/v2/match")

# Get the API key from environment variable
RIOT_API_KEY = os.getenv("RIOT_APIKEY")

@router.post("/", response_model=MatchResponse)
async def create_match(match_request: MatchRequest):
    """
    Create a new match with the provided details.
    
    Args:
        match_request: MatchRequest object containing players, match_start_time, 
                      match_map, and expected_match_id
    
    Returns:
        MatchResponse object with match details and status
    """
    try:
        # Validate the request
        if not match_request.players:
            raise HTTPException(status_code=400, detail="Players list cannot be empty")
        
        if not match_request.match_map:
            raise HTTPException(status_code=400, detail="Match map cannot be empty")
        
        # Generate a unique match ID (you might want to use the expected_match_id instead)
        match_id = str(uuid.uuid4())
        
        # Here you would typically save the match to a database
        # For now, we'll just return the match details
        
        return MatchResponse(
            match_id=match_id,
            players=match_request.players,
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
    Find the common match ID among all players and validate it.
    After finding the common match ID, fetch match details and verify start time and map.
    
    Args:
        request: MatchValidationRequest containing players, expected_start_time, and expected_map
    
    Returns:
        MatchValidationResponse with validation results
    """
    try:
        # Validate the request
        if not request.players:
            raise HTTPException(status_code=400, detail="Players list cannot be empty")
        
        # Check each player's match history
        all_player_matches = {}
        
        async with httpx.AsyncClient() as client:
            # Check each player's match history concurrently
            tasks = []
            for player in request.players:
                task = get_player_match_history(client, player)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(results):
                player = request.players[i]
                if isinstance(result, Exception):
                    # If there's an error checking the player, count them as not having any matches
                    all_player_matches[player] = []
                    print(f"❌ Error getting matches for {player.name}#{player.tag}: {result}")
                else:
                    matches = result
                    all_player_matches[player] = matches
                    print(f"✅ Found {len(matches)} matches for {player.name}#{player.tag}: {matches}")
            
            # Find the common match ID that 70% of players share
            total_players = len(request.players)
            print(f"\n🔍 Looking for common match ID among {total_players} players...")
            common_match_id, percentage_with_match = find_common_match_id(all_player_matches, total_players)
            print(f"🎯 Common match ID found: {common_match_id} (shared by {percentage_with_match:.1f}% of players)")
            
            if not common_match_id:
                message = f"Validation failed! No match ID found that 70% of players share. At least 70% of players share. At least 70% of players must have a common match in their history."
                return MatchValidationResponse(
                    match_id="",
                    players_with_match=[],
                    players_without_match=request.players,
                    percentage_with_match=0.0,
                    validation_passed=False,
                    message=message,
                    alternative_match_id=None,
                    match_details_verified=False,
                    time_verification_passed=None,
                    map_verification_passed=None
                )
            
            # Find which players have the common match ID
            players_with_match = []
            players_without_match = []
            
            for player, matches in all_player_matches.items():
                if common_match_id in matches:
                    players_with_match.append(player)
                else:
                    players_without_match.append(player)
            
            # Verify match details
            async with httpx.AsyncClient() as verify_client:
                match_details_verified, time_verification_passed, map_verification_passed, verification_message = await verify_match_details(verify_client, common_match_id, request.expected_start_time, request.expected_map)
            
            if not match_details_verified:
                validation_passed = False
                message = f"Found common match ID '{common_match_id}' that {percentage_with_match:.1f}% of players share, but match details verification failed: {verification_message}"
            else:
                validation_passed = True
                message = f"Validation passed! Found common match ID '{common_match_id}' that {percentage_with_match:.1f}% of players share. Match details verified successfully."
            
            return MatchValidationResponse(
                match_id=common_match_id,
                players_with_match=players_with_match,
                players_without_match=players_without_match,
                percentage_with_match=percentage_with_match,
                validation_passed=validation_passed,
                message=message,
                alternative_match_id=None,
                match_details_verified=match_details_verified if validation_passed else False,
                time_verification_passed=time_verification_passed,
                map_verification_passed=map_verification_passed
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

async def get_player_match_history(client: httpx.AsyncClient, player: PlayerInfo) -> list:
    """
    Get a player's match history.
    
    Args:
        client: HTTP client for making requests
        player: PlayerInfo object containing name, tag, region, and platform
    
    Returns:
        List of match IDs in the player's history (filtered to matches within last 2 days)
    """
    try:
        # Make request to real Riot API using player info
        # URL encode the player name to handle spaces and special characters
        import urllib.parse
        encoded_name = urllib.parse.quote(player.name)
        
        # Use the same hardcoded base URL as the test files
        base_url = "https://api.henrikdev.xyz/valorant/v4/matches"
        url = f"{base_url}/{player.region}/{player.platform}/{encoded_name}/{player.tag}?mode=custom"
        print(f"🌐 Making API request to: {url}")
        
        # Add API key to headers if available
        headers = {}
        if RIOT_API_KEY:
            headers["Authorization"] = RIOT_API_KEY  # No Bearer prefix needed
            print(f"🔑 Using API key: {RIOT_API_KEY[:10]}...")
        else:
            print("⚠️ No API key found in environment variables")
        
        response = await client.get(url, headers=headers, timeout=10.0)
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            recent_matches = data.get("data", [])
            
            print(f"🔍 Raw response for {player.name}#{player.tag}: {len(recent_matches)} matches found")
            print(f"🔍 Full response status: {data.get('status')}")
            if recent_matches:
                print(f"📋 First match metadata keys: {list(recent_matches[0].get('metadata', {}).keys())}")
                print(f"📋 First match started_at: {recent_matches[0].get('metadata', {}).get('started_at')}")
                print(f"📋 First match match_id: {recent_matches[0].get('metadata', {}).get('match_id')}")
            
            # Calculate the cutoff time (30 days ago to be more lenient)
            # Use UTC timezone to match the API timestamps
            cutoff_time = datetime.now(timezone.utc) - timedelta(days=30)
            print(f"⏰ Cutoff time: {cutoff_time}")
            
            # Filter matches that are within the last 30 days and extract match IDs
            match_ids = []
            for i, match in enumerate(recent_matches):
                metadata = match.get("metadata", {})
                started_at_str = metadata.get("started_at")
                
                print(f"📅 Match {i+1} started_at: {started_at_str}")
                
                if started_at_str:
                    try:
                        # Parse the started_at timestamp
                        started_at = datetime.fromisoformat(started_at_str.replace('Z', '+00:00'))
                        print(f"📅 Parsed started_at: {started_at}")
                        # Check if the match is within the last 30 days
                        if started_at >= cutoff_time:
                            match_id = metadata.get("match_id")
                            if match_id:
                                match_ids.append(match_id)
                                print(f"✅ Added match ID: {match_id} for {player.name}#{player.tag}")
                            else:
                                print(f"❌ No match_id found in metadata for {player.name}#{player.tag}")
                        else:
                            print(f"⏰ Match too old for {player.name}#{player.tag} (started: {started_at})")
                    except (ValueError, TypeError) as e:
                        # If parsing fails, skip this match
                        print(f"❌ Failed to parse started_at for {player.name}#{player.tag}: {e}")
                        continue
                else:
                    print(f"❌ No started_at found for match {i+1} for {player.name}#{player.tag}")
            
            return match_ids
        else:
            # If the request fails, return empty list
            return []
            
    except Exception:
        # If there's any error, return empty list
        return []

def find_common_match_id(all_player_matches: dict, total_players: int) -> tuple:
    """
    Find a common match ID that 70% of players share.
    
    Args:
        all_player_matches: Dictionary mapping player_id to list of match IDs
        total_players: Total number of players
    
    Returns:
        Tuple of (common_match_id, percentage) or (None, 0) if not found
    """
    # Collect all match IDs from all players
    all_match_ids = []
    for player_matches in all_player_matches.values():
        all_match_ids.extend(player_matches)
    
    print(f"📊 All match IDs found: {all_match_ids}")
    
    # Count occurrences of each match ID
    match_counter = Counter(all_match_ids)
    print(f"📈 Match ID counts: {dict(match_counter)}")
    
    # Find match IDs that appear in at least 70% of players
    required_count = int(total_players * 0.7)
    print(f"🎯 Required count for 70%: {required_count} out of {total_players} players")
    
    for match_id, count in match_counter.most_common():
        if count >= required_count:
            percentage = (count / total_players) * 100
            return match_id, percentage
    
    return None, 0



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
        # Fetch match details from real Riot API
        headers = {}
        if RIOT_API_KEY:
            headers["Authorization"] = RIOT_API_KEY  # No Bearer prefix needed
        
        response = await client.get(
            f"https://api.henrikdev.xyz/valorant/v2/match/{match_id}",
            headers=headers,
            timeout=10.0
        )
        
        if response.status_code != 200:
            return False, None, None, f"Failed to fetch match details for match ID '{match_id}'"
        
        data = response.json()
        # Extract data from the real Riot API response format
        match_data = data.get("data", {})
        actual_start_time_unix = match_data.get("metadata", {}).get("game_start")
        actual_map = match_data.get("metadata", {}).get("map")
        
        if not actual_start_time_unix or not actual_map:
            return False, None, None, f"Invalid match data received for match ID '{match_id}'"
        
        # Parse the actual start time from Unix timestamp
        try:
            # Convert Unix timestamp to datetime in UTC
            actual_start_time = datetime.fromtimestamp(actual_start_time_unix, tz=timezone.utc)
        except (ValueError, TypeError) as e:
            return False, None, None, f"Invalid start time format in match data for match ID '{match_id}': {actual_start_time_unix}"
        
        # Ensure expected_start_time is also in UTC for comparison
        if expected_start_time.tzinfo is None:
            # If expected_start_time has no timezone info, assume it's UTC
            expected_start_time = expected_start_time.replace(tzinfo=timezone.utc)
        
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
    Fetch match details including player statistics from the real Riot API.
    
    Args:
        client: HTTP client for making requests
        match_id: The match ID to fetch details for
    
    Returns:
        Dictionary containing match details and player statistics
    """
    try:
        headers = {}
        if RIOT_API_KEY:
            headers["Authorization"] = RIOT_API_KEY  # No Bearer prefix needed
        
        response = await client.get(
            f"https://api.henrikdev.xyz/valorant/v2/match/{match_id}",
            headers=headers,
            timeout=10.0
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=404, detail=f"Match details not found for match ID: {match_id}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching match details: {str(e)}")

def create_leaderboard(players: List[PlayerStats], allowed_players: List[PlayerInfo] = None) -> List[LeaderboardEntry]:
    """
    Create a leaderboard from player statistics, sorted by kills first, then by average combat score.
    Only includes players that are in the allowed_players list if provided.
    
    Args:
        players: List of PlayerStats objects
        allowed_players: Optional list of PlayerInfo objects to include in the leaderboard
    
    Returns:
        List of LeaderboardEntry objects sorted by rank
    """
    # Filter players if allowed_players is provided
    if allowed_players:
        filtered_players = [player for player in players if player.player_info in allowed_players]
    else:
        filtered_players = players
    
    # Sort players by kills (descending), then by average combat score (descending)
    sorted_players = sorted(filtered_players, key=lambda x: (x.kills, x.average_combat_score), reverse=True)
    
    leaderboard = []
    for i, player in enumerate(sorted_players):
        entry = LeaderboardEntry(
            rank=i + 1,
            player_info=player.player_info,
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
        
        # Use the found match ID from validation
        final_match_id = validation_response.match_id
        
        # Fetch match details
        async with httpx.AsyncClient() as client:
            match_details = await get_match_details(client, final_match_id)
        
        # Extract player statistics from real Riot API response
        match_data = match_details.get("data", {})
        players_data = match_data.get("players", {}).get("all_players", [])
        
        # Convert Riot API player data to our PlayerStats format
        players = []
        for player_data in players_data:
            # Create PlayerInfo from the player data
            player_info = PlayerInfo(
                name=player_data.get("name", ""),
                tag=player_data.get("tag", ""),
                region=request.players[0].region if request.players else "na",  # Use region from request
                platform=request.players[0].platform if request.players else "pc"  # Use platform from request
            )
            
            # Create PlayerStats
            player_stats = PlayerStats(
                player_info=player_info,
                kills=player_data.get("stats", {}).get("kills", 0),
                average_combat_score=player_data.get("stats", {}).get("score", 0) / max(player_data.get("stats", {}).get("rounds_played", 1), 1)
            )
            players.append(player_stats)
        
        # Create leaderboard with only the players from the original request
        leaderboard = create_leaderboard(players, request.players)
        
        # Parse match start time from Unix timestamp
        match_start_time_unix = match_data.get("metadata", {}).get("game_start")
        if match_start_time_unix:
            try:
                match_start_time = datetime.fromtimestamp(match_start_time_unix, tz=timezone.utc)
            except (ValueError, TypeError):
                match_start_time = datetime.now(timezone.utc)  # Fallback
        else:
            match_start_time = datetime.now(timezone.utc)  # Fallback
        
        return LeaderboardResponse(
            match_id=final_match_id,
            match_start_time=match_start_time,
            map=match_data.get("metadata", {}).get("map", ""),
            leaderboard=leaderboard,
            total_players=len(leaderboard),
            message=f"Leaderboard generated successfully for match '{final_match_id}'. {len(leaderboard)} players from the original request ranked by kills and average combat score."
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
