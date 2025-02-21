from sqlalchemy.orm import Session
from src.dna_logger import logger
from src.database import get_db
from src.models import Bill  # Bill 모델 클래스 정의가 필요합니다
from sqlalchemy.exc import SQLAlchemyError


def catch_sql_except(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SQLAlchemyError as err:
            logger.error(f"error: SQLAlchemy error occurred {err}")

    return wrapper


class DBHandler:

    def __init__(self, db_session: Session):
        self.db = db_session

    # Functions regarding Bills
    @catch_sql_except
    def save_bill(self, params):
        bill = Bill(
            bill_id=params["bill_id"],
            url=params["url"],
            num=params["num"],
            title=params["title"],
            body=params["body"],
            pdf_url=params["pdf_url"],
            date=params["date"],
            ord_num=params["ord_num"],
        )
        self.db.add(bill)
        self.db.commit()
        return bill

    @catch_sql_except
    def del_bill(self, bill_id):
        bill = self.db.query(Bill).filter(Bill.bill_id == bill_id).first()
        if bill:
            self.db.delete(bill)
            self.db.commit()

    @catch_sql_except
    def read_all_value_table(self):
        results = self.db.query(Bill).all()
        logger.debug(f"Findings number: {len(results)}")
        return results

    @catch_sql_except
    def read_value_table(self, bill_id):
        result = self.db.query(Bill).filter(Bill.bill_id == bill_id).first()
        return result

    @catch_sql_except
    def update_value(self, bill_id, set_column, set_value):
        bill = self.db.query(Bill).filter(Bill.bill_id == bill_id).first()
        if bill:
            setattr(bill, set_column, set_value)
            self.db.commit()

    @catch_sql_except
    def extract_bills_summary(self):
        """bills 테이블에서 summary를 추출하는 함수"""
        try:
            # 모든 법안의 summary를 가져옴
            summaries = self.db.query(Bill.body).all()
            return [summary[0] for summary in summaries]  # 튜플에서 summary만 추출
        except Exception as e:
            print(f"Error extracting summaries: {str(e)}")
            return []
        finally:
            self.db.close()

    def save_summary(self, summarizer):
        from src.summary import Summarizer

        columns = ("headline", "body", "bill_id", "conf_id")
        params = (
            summarizer.get_headline(),
            summarizer.get_paragraph(),
            summarizer.bill_id,
            summarizer.conf_id,
        )
        table = "bill_summaries"
        self.db.save_table(table, columns, params)

    def read_summary(self, bill_id):
        """주어진 bill_id에 대한 summary를 읽어오는 함수"""
        try:
            result = self.db.query(
                "SELECT * FROM bill_summaries WHERE bill_id = :bill_id",
                {"bill_id": bill_id},
            ).first()
            return result
        except Exception as e:
            logger.error(f"Error reading summary: {str(e)}")
            return None


# Dependency for DB connection
def get_db_handler():
    db = next(get_db())  # get_db()는 generator이므로 next()로 세션 가져옴
    return DBHandler(db)


db_handler = get_db_handler()

if __name__ == "__main__":
    params = {
        "bill_id": "test_id",
        "url": "https://likms.assembly.go.kr/bill/billDetail.do?billId=PRC_N2C4C1O1V2V0N2G0J5X0V5Z3L7Z5Z0",
        "num": "11111111",
        "title": "테스트 헤드라인",
        "body": "테스트 요약",
        "pdf_url": "https://likms.assembly.go.kr/filegate/sender24?dummy=dummy&bookId=8A944004-E8FF-C5BE-948F-304B7A8B1790&type=1",
        "date": "2024-11-27",
        "ord_num": "22",
    }
    db_handler.save_bill(params)
    summaries = db_handler.extract_bills_summary()
    for idx, summary in enumerate(summaries):
        print(f"summary {idx}: ")
        print(summary)
    db_handler.del_bill("test_id")
