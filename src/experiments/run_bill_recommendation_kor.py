from src.dna_logger import logger
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from konlpy.tag import Okt
import re
from src.experiments.run_bill_recommendation import (
    extract_bills_id,
    extract_bills_summary,
)
import pandas as pd


class KoreanTfidfVectorizer:
    def __init__(self):
        self.okt = Okt()
        self.vectorizer = TfidfVectorizer(
            tokenizer=self.tokenize,
            preprocessor=self.preprocess,
            stop_words=["은", "는", "이", "가", "을", "를"],
            min_df=2,
            max_df=0.9,
        )

    def preprocess(self, text):
        """기본적인 토큰화"""
        # 개행 문자 제거
        text = re.sub(r"[\r\n]+", " ", text)
        # 특수문자 제거 및 공백 기준 분리
        text = re.sub(r"[^\w\s]+", "", text)
        # 중복 공백 제거
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"ㆍ+", " ", text)
        # 텍스트 전처리
        return text.strip()

    def tokenize(self, text):
        # 형태소 분석
        return self.okt.morphs(text)

    def fit_transform(self, texts):
        return self.vectorizer.fit_transform(texts)

    def transform(self, texts):
        return self.vectorizer.transform(texts)

    def get_feature_names(self):
        return self.vectorizer.get_feature_names_out()


# 사용 예시
texts = [
    "자연어 처리는 매우 재미있습니다.",
    "파이썬으로 자연어 처리를 공부해요.",
    "자연어 처리는 어렵지만 중요합니다.",
]


class KoreanTokenizer:
    def __init__(self):
        self.okt = Okt()

    def tokenize_okt(self, text, pos=False):
        """Okt(Open Korean Text) 토크나이저 사용"""
        if pos:
            return self.okt.pos(text)  # 품사 태깅 포함
        return self.okt.morphs(text)  # 형태소 분석

    def tokenizing(self, text):
        """토큰화 함수"""
        reformatted_text = self.tokenize_basic(text)
        return self.tokenize_okt(reformatted_text)


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

        vectorizer = KoreanTfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(bills)
        bills_id = extract_bills_id()
        print(bills_id)
        recommendations = cosine_similarity_compute(tfidf_matrix, bills_id)
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
