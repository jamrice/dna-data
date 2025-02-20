from src.database import SessionLocal
from src.models import Bill, BillRecommendation
from src.dna_logger import logger
from src.experiments.bill_recommendation_pipeline import BillRecommender
from src.summary import Summarizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import pandas as pd


def extract_bills_summary():
    """bills 테이블에서 summary를 추출하는 함수"""
    db = SessionLocal()
    try:
        # 모든 법안의 summary를 가져옴
        summaries = db.query(Bill.body).all()
        return [summary[0] for summary in summaries]  # 튜플에서 summary만 추출
    except Exception as e:
        print(f"Error extracting summaries: {str(e)}")
        return []
    finally:
        db.close()


def save_recommendations_to_db(
    recommendations,
    source_bill_id,
    host="localhost",
    user="root",
    password="your_password",
):
    """추천 결과를 데이터베이스에 저장"""
    try:
        db = SessionLocal()
        with db.cursor() as cursor:
            # 기존 추천 결과 삭제
            BillRecommendation.delete_by_source_bill(cursor, source_bill_id)

            # 새로운 추천 결과 저장
            for rec in recommendations:
                recommendation = BillRecommendation(
                    source_bill_no=source_bill_id,
                    recommended_bill_no=rec["bill_id"],
                    similarity_score=rec["similarity_score"],
                )
                recommendation.save(cursor)

            db.commit()
            logger.info(
                f"Saved {len(recommendations)} recommendations for bill {source_bill_id}"
            )

    except Exception as e:
        logger.error(f"Error saving recommendations to database: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def generate_all_recommendations(summaries):
    """모든 법안에 대한 추천 생성"""
    try:
        # 데이터베이스에서 법안 정보 가져오기
        bills = summaries

        if not bills:
            logger.warning("No bills found in database")
            return

        # 영어로 번역된 요약을 저장할 리스트
        translated_summaries = []

        # 각 법안에 대해 요약을 영어로 번역
        for idx, bill in enumerate(bills):
            summarizer = Summarizer(bill)
            translated_summary = summarizer.translate_to_english()
            translated_summaries.append({"id": idx, "summary": translated_summary})

        # TF-IDF 벡터라이저 설정
        tfidf_vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = tfidf_vectorizer.fit_transform(
            [bill["summary"] for bill in translated_summaries]
        )

        # 코사인 유사도 계산
        cosine_sim = cosine_similarity(tfidf_matrix)
        cosine_sim_df = pd.DataFrame(cosine_sim)
        print(translated_summaries)
        print(cosine_sim_df)

        # 추천 결과 생성
        recommendations = []
        for idx, bill in enumerate(translated_summaries):
            similar_indices = cosine_sim[idx].argsort()[::-1][
                1:5
            ]  # 자기 자신 제외하고 상위 4개 (현재 데이터 5개밖에 없음)
            for sim_idx in similar_indices:
                recommendations.append(
                    {
                        "bill_id": bill["id"],
                        "recommended_bill_id": translated_summaries[sim_idx]["id"],
                        "similarity_score": cosine_sim[idx][sim_idx],
                    }
                )
        return recommendations
        # 추천 결과를 DB에 저장
        # for bill in translated_summaries:
        #     save_recommendations_to_db(
        #         recommendations, bill["id"], host, user, password
        #     )

        # logger.info("Recommendation generation completed!")

    except Exception as e:
        logger.error(f"Error in recommendation generation process: {str(e)}")
        raise


if __name__ == "__main__":
    summaries = extract_bills_summary()

    # 추천 시스템 실행
    generate_all_recommendations(summaries)
