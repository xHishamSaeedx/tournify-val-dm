from pydantic import BaseModel
from typing import List
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
