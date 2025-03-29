from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from src.dna_logger import logger
from src.database import get_db
from src.models import (
    Bill,
    BillSummary,
    BillsEmbedding,
    SimilarityScore,
    Conf,
)  # Bill 모델 클래스 정의가 필요합니다


def catch_sql_except(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SQLAlchemyError as err:
            args[0].db.rollback()
            logger.error(f"error: SQLAlchemy error occurred {err}")

    return wrapper


class DBHandler:
    def __init__(self, db_session: Session):
        self.db = db_session

    @catch_sql_except
    def save_conf(self, params):
        conf = Conf(
            id=params["id"],
            url=params["url"],
            num=params["num"],
            title=params["title"],
            pdf_url=params["pdf_url"],
            date=params["date"],
            ord_num=params["ord_num"],
        )
        self.db.add(conf)
        self.db.commit()
        return conf

    @catch_sql_except
    def save_embedding(self, params):
        billsEmbedding = BillsEmbedding(
            bill_id=params["bill_id"],
            embedding=params["embedding"],
        )
        self.db.add(billsEmbedding)
        self.db.commit()

    # functions regarding bills
    @catch_sql_except
    def check_bill_exists(self, bill_id) -> bool:
        """주어진 bill_id에 해당하는 법안이 존재하는지 확인하는 함수"""
        bill = self.db.query(Bill).filter(Bill.bill_id == bill_id).first()
        return bill is not None

    @catch_sql_except
    def save_bill(self, params):
        bill = Bill(
            bill_id=params["bill_id"],
            bill_no=params["bill_no"],
            bill_title=params["bill_title"],
            bill_body=params["bill_body"],
            ppsr_name=params["ppsr_name"],
            ppsl_date=params["ppsl_date"],
            jrcmit_name=params["jrcmit_name"],
            rgs_rsln_date=params["rgs_rsln_date"],
            rgs_rsln_rslt=params["rgs_rsln_rslt"],
            ord_num=params["ord_num"],
            bill_url=params["bill_url"],
            pdf_url=params["pdf_url"],
        )
        if not self.check_bill_exists(bill.bill_id):
            print("save_bill = bill_id: ", bill.bill_id)
            self.db.add(bill)
            print("save_bill: ", bill)
            self.db.commit()
        return bill

    @catch_sql_except
    def save_bill_translation(self, bill_id, translated_title, translated_summary):
        """법안의 영어 제목과 내용을 업데이트하는 함수"""
        bill = self.db.query(Bill).filter(Bill.bill_id == bill_id).first()
        if bill:
            bill.bill_title_eng = translated_title
            bill.bill_body_eng = translated_summary
            self.db.commit()
        else:
            logger.warning(f"Bill with ID {bill_id} not found for translation update.")

    @catch_sql_except
    def get_bill(self, bill_id: str):
        try:
            bill = self.db.query(Bill).filter(Bill.bill_id == bill_id).one()
            return bill
        except NoResultFound:
            return logger.info("Bill not found")

    @catch_sql_except
    def get_all_bills(self):
        bills = self.db.query(Bill).all()
        return bills

    @catch_sql_except
    def del_bill(self, bill_id):
        bill = self.db.query(Bill).filter(Bill.bill_id == bill_id).first()
        if bill:
            self.db.delete(bill)
            self.db.commit()

    @catch_sql_except
    def get_all_value_tables(self):
        results = self.db.query(Bill).all()
        logger.debug(f"Findings number: {len(results)}")
        return results

    @catch_sql_except
    def get_value_table(self, bill_id):
        result = self.db.query(Bill).filter(Bill.bill_id == bill_id).first()
        return result

    @catch_sql_except
    def update_bill_value(self, bill_id, set_column, set_value):
        bill = self.db.query(Bill).filter(Bill.bill_id == bill_id).first()
        if bill:
            setattr(bill, set_column, set_value)
            self.db.commit()

    # 만약 코사인 유사도 계산에 추가적인 정보를 사용한다면 이 함수에서 return해줄 필요가 있음.
    @catch_sql_except
    def get_bills_content(self):
        """bills 테이블에서 모든 content를 추출하는 함수"""
        try:
            # 모든 법안의 summary를 가져옴
            summaries = self.db.query(Bill).all()
            return [
                {
                    "bill_id": bill.bill_id,
                    "bill_title": bill.bill_title,
                    "bill_summary": bill.bill_body,
                }
                for bill in summaries
            ]  # 딕셔너리 리스트로 변환
        except Exception as e:
            print(f"Error extracting summaries: {str(e)}")
            return []
        finally:
            self.db.close()

    def get_existing_translation(self, bill_id):
        """Retrieve existing translation for a given bill_id from the database."""
        query = text(
            "SELECT bill_title_eng, bill_body_eng FROM bills WHERE bill_id = :bill_id"
        )
        print(f"Executing query: {query} with parameters: {bill_id}")  # Debugging line
        result = self.db.execute(query, {"bill_id": bill_id}).first()

        if result.bill_body_eng is not None:
            print("existing title translation: " + result.bill_title_eng)
            print("existing summary translation: " + result.bill_body_eng)
            return {
                "id": bill_id,
                "translated_bill_title": result.bill_title_eng,
                "translated_bill_summary": result.bill_body_eng,
            }
        return None

    # functions regarding summaries
    @catch_sql_except
    def save_summary(self, summarizer):
        summary = BillSummary(
            headline=summarizer.get_headline(),
            body=summarizer.get_paragraph(),
            bill_id=summarizer.bill_id,
            conf_id=summarizer.conf_id,
        )
        self.db.add(summary)
        self.db.commit()
        return summary

    @catch_sql_except
    def get_all_summaries(self, bill_id):
        """주어진 bill_id에 대한 summary를 읽어오는 함수"""
        try:
            result = self.db.query(
                text("SELECT * FROM bill_summaries WHERE bill_id = :bill_id"),
                {"bill_id": bill_id},
            ).first()
            return result
        except Exception as e:
            logger.error(f"Error reading summary: {str(e)}")
            return None

    @catch_sql_except
    def get_summary(self, bill_id):
        """주어진 bill_id에 대한 summary를 읽어오는 함수"""
        try:
            result = self.db.query(
                text("SELECT * FROM bill_summaries WHERE bill_id = :bill_id"),
                {"bill_id": bill_id},
            ).first()
            return result
        except Exception as e:
            logger.error(f"Error reading summary: {str(e)}")
            return None

    @catch_sql_except
    def save_similarity_score(self, target_bill_id, source_bill_id, similarity_score):
        try:
            # 이미 있는 쌍에 대한 데이터면 새로운 데이터로 덮어쓰기
            existing_record = (
                self.db.query(SimilarityScore)
                .filter_by(source_bill_id=source_bill_id, target_bill_id=target_bill_id)
                .first()
            )

            if existing_record:
                existing_record.similarity_score = (
                    similarity_score  # Update the existing score
                )
                self.db.commit()  # Commit the transaction
            else:
                # 없는 쌍에 대해서는 새로운 행을 추가
                new_record = SimilarityScore(
                    source_bill_id=source_bill_id,
                    target_bill_id=target_bill_id,
                    similarity_score=similarity_score,
                )
                self.db.add(new_record)
                self.db.commit()  # Commit the transaction
        except Exception as e:
            self.db.rollback()  # Roll back the transaction on error
            logger.error(f"Error saving similarity score: {str(e)}")


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
