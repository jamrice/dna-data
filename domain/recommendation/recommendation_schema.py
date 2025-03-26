from pydantic import BaseModel, Field
from typing import List


class CollaborativeRecommendation(BaseModel):
    user_id: int
    n_items: int = 5
    neighbor_size: int = 5


class BillContentsRecommendation(BaseModel):
    content_id: str
    # gt = validation parameter greater than
    n_items: int = Field(default=5, gt=0, description="Number of items to recommend")


class UserContentsRecommendation(BaseModel):
    n_contents: List[str]
    n_items: int = 20
