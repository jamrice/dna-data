from src.dna_logger import logger
from src.summary import Summarizer
from src.db_handler import get_db_handler

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def generate_all_recommendations(summaries, db_handler):
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
        for bill in bills:
            summarizer = Summarizer(bill["bill_summary"])  # bill_summary를 사용
            translated_summary = summarizer.translate_to_english()

            # 번역된 요약이 None이 아닌 경우에만 추가
            if translated_summary is not None:
                translated_summaries.append(
                    {"id": bill["bill_id"], "summary": translated_summary}
                )

        # TF-IDF 벡터라이저 설정
        if not translated_summaries:
            logger.warning("No valid translated summaries found.")
            return

        tfidf_vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = tfidf_vectorizer.fit_transform(
            [bill["summary"] for bill in translated_summaries]
        )

        # 코사인 유사도 계산
        cosine_sim = cosine_similarity(tfidf_matrix)
        cosine_sim_df = pd.DataFrame(cosine_sim)
        # print(translated_summaries)
        # print(cosine_sim_df)

        # 추천 결과 생성 및 DB에 저장
        for idx, bill in enumerate(translated_summaries):
            source_bill_id = bill["id"]  # 현재 법안의 ID를 source_bill_id로 설정
            for sim_idx in range(len(translated_summaries)):  # 모든 법안에 대해 반복
                if sim_idx != idx:  # 자기 자신 제외
                    target_bill_id = translated_summaries[sim_idx]["id"]
                    similarity_score = cosine_sim[idx][sim_idx]
                    db_handler.save_similarity_score(
                        target_bill_id, source_bill_id, similarity_score
                    )

        return translated_summaries

    except Exception as e:
        logger.error(f"Error in recommendation generation process: {str(e)}")
        raise


if __name__ == "__main__":
    db_handler = get_db_handler()
    summaries = db_handler.extract_bills_summary()
    summaries = [summary for summary in summaries if summary is not None]

    # 추천 시스템 실행
    target_bills = generate_all_recommendations(summaries, db_handler)
    for bill in target_bills:
        print(bill)
