import pandas as pd
from src.dna_logger import logger
from src.db_handler import get_db_handler
from sqlalchemy import text


class NewRecommendation:
    def __init__(self):
        self.db_handler = get_db_handler()
        self.views = self.get_views()
        self.worst_sellers = self.get_worst_sellers()
        self.dates = self.get_dates()

    def get_views(self):
        views = self.db_handler.db.execute(text("SELECT * FROM contents"))
        views = (
            pd.DataFrame(views, columns=views.keys())
            .drop_duplicates(subset="id")
            .set_index("id")
        )
        return views

    def get_dates(self):
        dates = self.db_handler.db.execute(
            text("SELECT id, bill_id, rgs_rsln_date FROM bills")
        )
        dates = (
            pd.DataFrame(dates, columns=dates.keys())
            .drop_duplicates(subset="bill_id")
            .set_index("id")  # id를 index로 사용
            .dropna()  # 지금은 일단 null값을 제거
        )
        return dates

    def get_worst_sellers(self, top_n: int = 6) -> list:
        """
        의안의 views를 기준으로 오름차순 정렬하여
        하위 top_n개의 베스트셀러의 content_id 리스트를 반환한다.
        """
        recos = self.views.sort_values(by="views", ascending=True)
        return recos["content_id"].head(top_n).tolist()

    def get_newest(self, recent_n: int = 6) -> list:
        """
        본회의에서 의안이 확결된 날짜를 기준으로
        가장 최근 n개의 의안 리스트를 반환한다.
        """
        recos = self.dates.sort_values(by="rgs_rsln_date", ascending=False)
        return recos["bill_id"].head(recent_n).tolist()


if __name__ == "__main__":
    nr = NewRecommendation()
    print(nr.get_dates())
    print(nr.get_newest(6))
