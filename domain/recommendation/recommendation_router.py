from fastapi import APIRouter, HTTPException
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from starlette import status

from src.models import SimilarityScore  # Import your SimilarityScore model
from src.database import get_db
from src.recommendation_models.collaborative_filtering import CollaborativeFiltering
from domain.recommendation import recommendation_crud, recommendation_schema

router = APIRouter(prefix="/api/recommend")


@router.post("/collaborative", status_code=status.HTTP_200_OK)
def recommend_collaborative(
    user_recommendation: recommendation_schema.CollaborativeRecommendation,
    db: Session = Depends(get_db),
):
    # Check if the user exists
    user = recommendation_crud.get_existing_user(db, user=user_recommendation)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    # Create an instance of CollaborativeFiltering
    cf_model = CollaborativeFiltering()

    # Get recommendations for the user
    recommended_items = cf_model.recommender(
        cf_model.cf_knn,
        user_recommendation.user_id,
        n_items=user_recommendation.n_items,
        neighbor_size=user_recommendation.neighbor_size,
    )

    return {
        "recommended_items": recommended_items.tolist()
    }  # Convert to list for JSON response


@router.post("/bill_contents", status_code=status.HTTP_200_OK)
def recommend_based_on_bill(
    recommendation: recommendation_schema.BillContentsRecommendation,  # Expecting content_id as input
    db: Session = Depends(get_db),
):
    # Get the specified content_id from the request
    content_id = recommendation.content_id

    # Query the similarity_scores table for the specified content_id
    similarity_scores = (
        db.query(SimilarityScore)
        .filter(SimilarityScore.source_bill_id == content_id)
        .order_by(SimilarityScore.similarity_score.desc())
        .limit(recommendation.n_items)
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


@router.post("/user_contents", status_code=status.HTTP_200_OK)
def recommend_based_on_interests(
    recommendation: recommendation_schema.UserContentsRecommendation,  # Expecting n_contents and n_items as input
    db: Session = Depends(get_db),
):
    # Get the list of content IDs the user is interested in
    n_contents = recommendation.n_contents

    # Check if the user has provided any content IDs
    if not n_contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No content IDs provided.",
        )

    # Query to calculate total cosine similarity for all contents excluding the user's interests
    total_similarity = (
        db.query(
            SimilarityScore.target_bill_id,
            func.sum(SimilarityScore.similarity_score).label("total_similarity"),
        )
        # .filter(
        #     SimilarityScore.source_bill_id.notin_(n_contents)
        # )  # Exclude user's interests
        .group_by(SimilarityScore.target_bill_id)
        .order_by(
            func.sum(SimilarityScore.similarity_score).desc()
        )  # Order by total similarity
        .limit(recommendation.n_items)  # Limit to n_items
        .all()
    )

    # Check if any similarity scores were found
    if not total_similarity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No similarity scores found for the specified contents.",
        )

    # Extract the recommended content IDs from the results
    recommended_content_ids = [
        content[0] for content in total_similarity
    ]  # score is a tuple

    return {
        "recommended_content_ids": recommended_content_ids
    }  # Return the recommended content IDs
