from sqlalchemy.orm import Session
from src.dna_logger import logger
from .database import get_db
from .models import Bill  # Bill 모델 클래스 정의가 필요합니다
from sqlalchemy.exc import SQLAlchemyError


def catch_sql_except(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SQLAlchemyError as err:
            logger.error(f"error: SQLAlchemy error occurred {err}")

    return wrapper


class DBManager:

    def __init__(self, db_session: Session):
        self.db = db_session

    @catch_sql_except
    def save_bill(self, params):
        bill = Bill(
            bill_id=params[0],
            url=params[1],
            num=params[2],
            title=params[3],
            body=params[4],
            pdf_url=params[5],
            date=params[6],
            ord_num=params[7],
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


# Dependency for DB connection
def get_db_manager():
    db = next(get_db())  # get_db()는 generator이므로 next()로 세션 가져옴
    return DBManager(db)


# id pw for tomato's local db
db_manager = get_db_manager()

if __name__ == "__main__":
    params = [
        "test_id",
        "https://likms.assembly.go.kr/bill/billDetail.do?billId=PRC_N2C4C1O1V2V0N2G0J5X0V5Z3L7Z5Z0",
        "11111111",
        "테스트 헤드라인",
        "테스트 요약",
        "https://likms.assembly.go.kr/filegate/sender24?dummy=dummy&bookId=8A944004-E8FF-C5BE-948F-304B7A8B1790&type=1",
        "2024-11-27",
        "22",
    ]
    db_manager.save_bill(params)
    db_manager.del_bill("test_id")
