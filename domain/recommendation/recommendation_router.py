from fastapi import APIRouter, HTTPException, Query
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from starlette import status

import src.recommendation_models as rm
from src.dna_logger import logger
from src.db_handler import DBHandler, get_db_handler
from src.database import get_db
from src.models import SimilarityScore  # Import your SimilarityScore model
from domain.recommendation import recommendation_crud, recommendation_schema

router = APIRouter(prefix="/api/recommend")

exception_counter = {"count": 0}


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
    cf_model = rm.CollaborativeFiltering()

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
    ),
    n_recommendations: int = Query(5, description="Number of recommended contents"),
    db: Session = Depends(get_db),
    db_handler: DBHandler = Depends(get_db_handler),
):
    """
    특정 사용자의 최근 방문한 n_contents 페이지들의 코사인 유사도 점수를 합산하여,
    가장 점수가 높은 n_recommendations 개의 컨텐츠를 추천합니다.
    """

    try:
        return_contents = []
        rr = rm.RandomRecommendation(db_handler)

        if not n_contents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No content IDs provided.",
            )

        recent_page_ids = db_handler.get_recent_contents(user_id, n_contents)

        if recent_page_ids == False:
            bs = rm.BestSeller(db_handler)
            return_contents.extend(bs.get_best_sellers(6))
            nr = rm.NewRecommendation(db_handler)
            return_contents.extend(nr.get_newest(return_contents, 2))
            return_contents.extend(nr.get_worst_sellers(return_contents, 2))
            return_contents.extend(rr.recommend_randomly(return_contents, 2))
        else:
            n_random = 2
            total_similarity = (
                db.query(
                    SimilarityScore.target_bill_id,
                    func.sum(SimilarityScore.similarity_score).label(
                        "total_similarity"
                    ),
                )
                .filter(SimilarityScore.source_bill_id.in_(recent_page_ids))
                .filter(SimilarityScore.target_bill_id.notin_(recent_page_ids))
                .group_by(SimilarityScore.target_bill_id)
                .order_by(func.sum(SimilarityScore.similarity_score).desc())
                .limit(n_recommendations - n_random)
                .all()
            )
            return_contents = [content[0] for content in total_similarity]  # 여기 문제
            return_contents.extend(rr.recommend_randomly(return_contents, n_random))

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
        }

    except Exception as e:
        exception_counter["count"] += 1
        logger.exception(
            f"[예외 발생 {exception_counter['count']}회차] 추천 생성 중 예외 발생: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error during recommendation process.",
        )
