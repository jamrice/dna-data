from sqlalchemy.orm import Session
from domain.recommendation import recommendation_schema
from src.models import User


# 유저의 다른 정보를 기반으로 id를 가져올 때를 위한 함수
def get_existing_user(
    db: Session, user=recommendation_schema.CollaborativeRecommendation
):
    print(f"Looking for user with ID: {user.user_id}")  # Debugging line
    user = db.query(User).filter((User.id == user.user_id)).first()
    return user.id
