from fastapi import APIRouter, HTTPException, Query
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from starlette import status

from src.db_handler import db_handler
from src.models import SimilarityScore  # Import your SimilarityScore model
from src.database import get_db
from src.recommendation_models.collaborative_filtering import CollaborativeFiltering
from src.recommendation_models.best_seller import BestSeller
from src.recommendation_models.new_reco import NewRecommendation
from src.recommendation_models.random_reco import RandomRecommendation
from domain.recommendation import recommendation_crud, recommendation_schema

router = APIRouter(prefix="/api/recommend")


@router.post("/collaborative", status_code=status.HTTP_200_OK)
def recommend_collaborative(
    recommendation_schema: recommendation_schema.CollaborativeRecommendation,
    db: Session = Depends(get_db),
):
    # Check if the user exists
    user = recommendation_crud.get_existing_user(db, user=recommendation_schema)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    n_recommendations = recommendation_schema.n_recommendations

    # Create an instance of CollaborativeFiltering
    cf_model = CollaborativeFiltering()

    # Get recommendations for the user
    recommended_items = cf_model.recommender(
        cf_model.cf_knn,
        recommendation_schema.user_id,
        n_recommendations=n_recommendations,
        neighbor_size=recommendation_schema.neighbor_size,
    )

    return {
        "recommended_items": recommended_items.tolist()
    }  # Convert to list for JSON response


@router.post("/bill_contents", status_code=status.HTTP_200_OK)
def recommend_based_on_bill(
    recommendation_schema: recommendation_schema.BillContentsRecommendation,  # Expecting content_id as input
    db: Session = Depends(get_db),
):
    # Get the specified content_id from the request
    content_id = recommendation_schema.content_id
    n_recommendations = (
        recommendation_schema.n_items
    )  # This is already available in your request

    # Query the similarity_scores table for the specified content_id
    similarity_scores = (
        db.query(SimilarityScore)
        .filter(SimilarityScore.source_bill_id == content_id)
        .order_by(SimilarityScore.similarity_score.desc())
        .limit(n_recommendations)
        .all()
    )

    # Check if any similarity scores were found
    if not similarity_scores:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No similarity scores found for the specified content ID.",
        )

    # Extract the recommended content IDs from the results
    recommended_content_ids = [content.target_bill_id for content in similarity_scores]

    # Optionally, limit the number of recommendations
    # top_n = 5  # For example, return the top 5 similar contents
    # top_recommendations = recommended_content_ids[:top_n]

    return {
        "recommended_content_ids": recommended_content_ids
    }  # Return the recommended content IDs


@router.post(
    "/user_contents",
    response_model=recommendation_schema.UserRecommendationResponse,
    status_code=status.HTTP_200_OK,
)
def recommend_based_on_interests(
    user_id: int = Query(1, description="User ID"),
    n_contents: int = Query(
        20,
        description="Number of contents to take into consideration for recommendation",
    ),  # Default value from schema
    n_recommendations: int = Query(
        5, description="Number of recommended contents"
    ),  # Default value from schema
    db: Session = Depends(get_db),
):
    """
    특정 사용자의 최근 방문한 n_contents 페이지들의 코사인 유사도 점수를 합산하여,
    가장 점수가 높은 n_recommendations 개의 컨텐츠를 추천합니다.

    Args:
        user_id (int): 사용자 ID
        n_contents (int): 참고할 유저의 컨텐츠 수
        n_recommendations (int): 추천할 컨텐츠 수

    Returns:
        dictionary: schema를 따르는 추천된 컨텐츠를 포함한 반환값
    """

    return_contents = []
    rr = RandomRecommendation()

    # Check if the user has provided any content IDs
    if not n_contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No content IDs provided.",
        )

    # default n_contents = 20
    recent_page_ids = db_handler.get_recent_contents(user_id, n_contents)

    # 만약 참조할 유저의 컨텐츠가 5개 미만이라면, best seller와 random reco를 사용
    if recent_page_ids == False:
        bs = BestSeller()
        return_contents.extend(bs.get_best_sellers(6))
        # 주목도가 적은거 or 아예 새롭게 추가된 의안
        nr = NewRecommendation()
        return_contents.extend(nr.get_newest(return_contents, 2))
        return_contents.extend(nr.get_worst_sellers(return_contents, 2))
        # 아예 random reco
        return_contents.extend(rr.recommend_randomly(return_contents, 2))

    else:
        # set number of random recommendations to make
        n_random = 2
        # Query to calculate total cosine similarity for contents based on user's recent visits
        total_similarity = (
            db.query(
                SimilarityScore.target_bill_id,
                func.sum(SimilarityScore.similarity_score).label("total_similarity"),
            )
            .filter(
                SimilarityScore.source_bill_id.in_(
                    recent_page_ids
                )  # Include only similarities from recent visits
            )
            .filter(
                SimilarityScore.target_bill_id.notin_(
                    recent_page_ids
                )  # Exclude already visited pages
            )
            .group_by(SimilarityScore.target_bill_id)
            .order_by(
                func.sum(SimilarityScore.similarity_score).desc()
            )  # Order by total similarity
            .limit(n_recommendations - n_random)  # Limit to n_recommendations
            .all()
        )
        # Check if any similarity scores were found
        return_contents = [content[0] for content in total_similarity]
        # add random recommendations
        return_contents.extend(rr.recommend_randomly(return_contents, n_random))

    # 여기도 random reco를 활용해야함
    # If the number of recommended contents is less than n_recommendations,
    # fill the remaining slots with zeros
    if len(return_contents) < n_recommendations:
        n_remaining_slots = n_recommendations - len(return_contents)
        return_contents.extend(
            rr.recommend_randomly(return_contents, n_remaining_slots)
        )

    return {
        "user_id": user_id,
        "recommended_content_ids": return_contents,
        "n_contents": n_contents,
        "n_recommendations": n_recommendations,
    }  # Return the recommended content IDs
