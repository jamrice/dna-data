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


class UserContentsRecommendation(BaseModel):
    n_contents: List[str]
    n_items: int = Field(default=20, gt=0, description="Number of items to recommend")
