from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PlayerInfo(BaseModel):
    name: str
    tag: str
    region: str
    platform: str
    
    def __eq__(self, other):
        if not isinstance(other, PlayerInfo):
            return False
        return (self.name == other.name and 
                self.tag == other.tag and 
                self.region == other.region and 
                self.platform == other.platform)
    
    def __hash__(self):
        return hash((self.name, self.tag, self.region, self.platform))

class MatchRequest(BaseModel):
    players: List[PlayerInfo]
    match_start_time: datetime
    match_map: str
    expected_match_id: str

class MatchResponse(BaseModel):
    match_id: str
    players: List[PlayerInfo]
    match_start_time: datetime
    match_map: str
    status: str
    message: str

class MatchValidationRequest(BaseModel):
    players: List[PlayerInfo]
    expected_start_time: datetime
    expected_map: str

class MatchValidationResponse(BaseModel):
    match_id: str
    players_with_match: List[PlayerInfo]
    players_without_match: List[PlayerInfo]
    percentage_with_match: float
    validation_passed: bool
    message: str
    alternative_match_id: Optional[str] = None
    match_details_verified: bool = False
    time_verification_passed: Optional[bool] = None
    map_verification_passed: Optional[bool] = None

class PlayerStats(BaseModel):
    player_info: PlayerInfo
    kills: int
    average_combat_score: float

class LeaderboardEntry(BaseModel):
    rank: int
    player_info: PlayerInfo
    kills: int
    average_combat_score: float

class LeaderboardResponse(BaseModel):
    match_id: str
    match_start_time: datetime
    map: str
    leaderboard: List[LeaderboardEntry]
    total_players: int
    message: str
