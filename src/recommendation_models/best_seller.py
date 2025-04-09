import pandas as pd
from src.dna_logger import logger
from src.db_handler import get_db_handler
from sqlalchemy import text


class BestSeller:
    def __init__(self):
        self.db_handler = get_db_handler()
        self.metrics = self.get_metrics()
        self.best_sellers = self.get_best_sellers()

    def get_metrics(self):
        metrics = self.db_handler.db.execute(text("SELECT * FROM user_content_metrics"))
        metrics = (
            pd.DataFrame(metrics, columns=metrics.keys())
            .drop_duplicates(subset="id")
            .set_index("id")
        )
        return metrics

    def get_best_sellers(self, top_n: int = 10) -> pd.DataFrame:
        """
        content_id 기준으로 평균 metric_score를 계산하여
        상위 top_n개의 베스트셀러를 반환한다.
        """
        grouped = (
            self.metrics.groupby("content_id")["metric_score"]
            .mean()
            .reset_index()
            .rename(columns={"metric_score": "avg_metric_score"})
            .sort_values(by="avg_metric_score", ascending=False)
        )
        return grouped.head(top_n)


if __name__ == "__main__":
    bs = BestSeller()
    print(bs.best_sellers)
