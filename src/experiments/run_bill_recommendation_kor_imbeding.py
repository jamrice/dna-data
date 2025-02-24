from src.dna_logger import logger
import google.generativeai as genai
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from src.experiments.run_bill_recommendation import (
    extract_bills_id,
    extract_bills_summary,
    translate_summaries,
)
from src.load import api_keyManager

# Gemini API 키 설정
API_KEY = api_keyManager.get_ggl_api_key()  # 여기에 API 키를 입력하세요
genai.configure(api_key=API_KEY)


def get_embedding(text):
    result = genai.embed_content(model="models/text-embedding-004", content=text)
    return result["embedding"]


def cosine_similarity_compute(tfidf_matrix, bills_id):
    # 코사인 유사도 계산
    cosine_sim = cosine_similarity(tfidf_matrix)
    cosine_sim_df = pd.DataFrame(cosine_sim)
    print(bills_id)
    print(cosine_sim_df)

    # 추천 결과 생성
    recommendations = []
    for idx, bill in enumerate(bills_id):
        similar_indices = cosine_sim[idx].argsort()[::-1][
            1:5
        ]  # 자기 자신 제외하고 상위 4개 (현재 데이터 5개밖에 없음)
        for sim_idx in similar_indices:
            recommendations.append(
                {
                    "bill_id": bill,
                    "recommended_bill_id": bills_id[sim_idx],
                    "similarity_score": cosine_sim[idx][sim_idx],
                }
            )
    return recommendations


def generate_all_recommendations(summaries):
    """모든 법안에 대한 추천 생성"""
    try:
        # 데이터베이스에서 법안 정보 가져오기
        bills = summaries

        if not bills:
            logger.warning("No bills found in database")
            return

        # TF-IDF 벡터라이저 설정
        # for bill in bills:
        #     print(bill)
        imbeding_matrix = [get_embedding(bill) for bill in bills]

        bills_id = extract_bills_id()
        print(bills_id)
        recommendations = cosine_similarity_compute(imbeding_matrix, bills_id)
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
    logger.info("Summaries extracted: " + str(len(summaries)))
    # 추천 시스템 실행
    generate_all_recommendations(summaries)
