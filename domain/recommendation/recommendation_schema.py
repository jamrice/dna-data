from pydantic import BaseModel
from typing import List


class CollaborativeRecommendation(BaseModel):
    user_id: int
    n_items: int = 5
    neighbor_size: int = 5


class BillContentsRecommendation(BaseModel):
    content_id: str
    n_items: int = 5


class UserContentsRecommendation(BaseModel):
    n_contents: List[str]
    n_items: int = 20

class UserRecommendation(BaseModel):
    user_id: int
    n_contents: int = 20
    n_items: int = 5

class UserRecommendationResponse(BaseModel):
    user_id: int
    n_contents: int = 20
    n_items: int = 5
    recommended_content_ids: List[str]