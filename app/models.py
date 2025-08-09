from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MatchRequest(BaseModel):
    player_ids: List[str]
    match_start_time: datetime
    match_map: str
    expected_match_id: str

class MatchResponse(BaseModel):
    match_id: str
    player_ids: List[str]
    match_start_time: datetime
    match_map: str
    status: str
    message: str

class MatchValidationRequest(BaseModel):
    match_id: str
    player_ids: List[str]

class MatchValidationResponse(BaseModel):
    match_id: str
    players_with_match: List[str]
    players_without_match: List[str]
    percentage_with_match: float
    validation_passed: bool
    message: str
    alternative_match_id: Optional[str] = None
    host_error: bool = False
