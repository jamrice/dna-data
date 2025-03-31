from pydantic import BaseModel, Field
from typing import List


class CollaborativeRecommendation(BaseModel):
    user_id: int
    # gt = validation parameter greater than
    n_items: int = Field(default=5, gt=0, description="Number of items to recommend")
    neighbor_size: int = 5


class BillContentsRecommendation(BaseModel):
    content_id: str
    n_items: int = Field(default=5, gt=0, description="Number of items to recommend")


class UserRecommendation(BaseModel):
    user_id: int
    n_contents: int = 20
    n_items: int = 5


class UserRecommendationResponse(BaseModel):
    user_id: int
    n_contents: int = 20
    n_items: int = 5
    recommended_content_ids: List[str]
