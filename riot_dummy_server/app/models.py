from pydantic import BaseModel
from typing import List
from datetime import datetime


class MatchRequest(BaseModel):
    match_id: str


class PlayerRequest(BaseModel):
    player_id: str


class PlayerStats(BaseModel):
    player_id: str
    kills: int
    average_combat_score: float


class MatchResponse(BaseModel):
    match_id: str
    match_start_time: datetime
    map: str
    players: List[PlayerStats]


class PlayerMatchHistory(BaseModel):
    player_id: str
    recent_matches: List[str]
