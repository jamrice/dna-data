from konlpy.tag import Mecab
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.database import SessionLocal
from src.models import Bill
import numpy as np


class BillRecommender:
    def __init__(self):
        self.mecab = Mecab()
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.bill_ids = None

    def tokenize(self, text):
        # 형태소 분석
        morphs = self.mecab.nouns(text)  # 명사만 추출
        return morphs

    def fit(self, bills):
        """
        bills: list of dictionaries containing 'id' and 'body' keys
        """
        self.bill_ids = [bill["id"] for bill in bills]
        texts = [bill["body"] for bill in bills]

        # TF-IDF 벡터라이저 설정
        self.tfidf_vectorizer = TfidfVectorizer(
            tokenizer=self.tokenize,
            min_df=2,  # 최소 2개의 문서에서 등장하는 단어만 포함
            max_df=0.9,  # 90% 이상의 문서에서 등장하는 단어는 제외
        )

        # TF-IDF 행렬 생성
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)

    def get_recommendations(self, bill_id, n_recommendations=5):
        """특정 법안과 유사한 다른 법안들을 추천"""
        if bill_id not in self.bill_ids:
            raise ValueError("Bill ID not found")

        idx = self.bill_ids.index(bill_id)
        bill_vector = self.tfidf_matrix[idx : idx + 1]

        # 코사인 유사도 계산
        sim_scores = cosine_similarity(bill_vector, self.tfidf_matrix)
        sim_scores = sim_scores.flatten()

        # 유사도가 높은 순으로 정렬 (자기 자신 제외)
        similar_indices = sim_scores.argsort()[::-1][1 : n_recommendations + 1]

        recommendations = [
            {"bill_id": self.bill_ids[idx], "similarity_score": sim_scores[idx]}
            for idx in similar_indices
        ]

        return recommendations


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
