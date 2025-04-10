import pandas as pd
from src.dna_logger import logger
from src.db_handler import get_db_handler
from sqlalchemy import text


class RandomRecommendation:
    def __init__(self):
        self.db_handler = get_db_handler()

    def recommend_radomly(self, n: int = 5) -> list:
        """
        랜덤으로 n개의 컨텐츠를 추천합니다.
        """
        bills = self.db_handler.db.execute(text("SELECT id, bill_id FROM bills"))
        bills = (
            pd.DataFrame(bills, columns=bills.keys())
            .drop_duplicates(subset="bill_id")
            .set_index("id")  # id를 index로 사용
            .dropna()  # 지금은 일단 null값을 제거
        )
        bills = bills.sample(n=min(n, len(bills)), random_state=42)  # 랜덤하게 n개 선택
        return bills["bill_id"].tolist()


if __name__ == "__main__":
    rr = RandomRecommendation()
    print(rr.recommend_radomly(5))
