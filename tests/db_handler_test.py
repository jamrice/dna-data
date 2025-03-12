import pytest
from sqlalchemy.orm import Session
from src.models import Bill
from src.db_handler import DBHandler
from datetime import datetime
import src.database as database


@pytest.fixture
def db_session():
    db = next(database.get_db())
    return db


@pytest.fixture
def db_handler(db_session):
    return DBHandler(db_session)


@pytest.fixture
def sample_bill_params():
    return {
        "bill_id": "test_id",
        "bill_no": "11111111",
        "bill_title": "테스트 법안",
        "bill_body": "테스트 내용",
        "ppsr_name": "최준영",
        "ppsl_date": "2024-01-01",
        "jrcmit_name": "소관위 예시",
        "rgs_rsln_date": "2024-01-01",
        "rgs_rsln_rslt": "본회의 심의결과 예시",
        "ord_num": "22",
        "bill_url": "https://likms.assembly.go.kr/bill/billDetail.do?billId=PRC_TEST",
        "pdf_url": "https://test.pdf",
    }


@pytest.fixture
def before_clean_bill(db_handler: DBHandler, sample_bill_params):
    db_handler.del_bill(sample_bill_params["bill_id"])


def test_save_bill(db_handler: DBHandler, sample_bill_params):
    if db_handler.check_bill_exists(sample_bill_params["bill_id"]):
        db_handler.del_bill(sample_bill_params["bill_id"])

    # When
    bill = db_handler.save_bill(sample_bill_params)

    # Then
    assert bill.bill_id == sample_bill_params["bill_id"]

    assert bill.bill_no == int(sample_bill_params["bill_no"])
    assert bill.bill_title == sample_bill_params["bill_title"]
    assert bill.bill_body == sample_bill_params["bill_body"]
    assert bill.ppsr_name == sample_bill_params["ppsr_name"]
    assert bill.ppsl_date.isoformat() == sample_bill_params["ppsl_date"]
    assert bill.jrcmit_name == sample_bill_params["jrcmit_name"]
    assert bill.rgs_rsln_date.isoformat() == sample_bill_params["rgs_rsln_date"]
    assert bill.rgs_rsln_rslt == sample_bill_params["rgs_rsln_rslt"]
    assert bill.ord_num == int(sample_bill_params["ord_num"])
    assert bill.bill_url == sample_bill_params["bill_url"]
    assert bill.pdf_url == sample_bill_params["pdf_url"]


def test_get_bill(db_handler: DBHandler, sample_bill_params):
    if db_handler.check_bill_exists(sample_bill_params["bill_id"]):
        db_handler.del_bill(sample_bill_params["bill_id"])
    # Given
    saved_bill = db_handler.save_bill(sample_bill_params)

    # When
    retrieved_bill = db_handler.get_bill(sample_bill_params["bill_id"])

    # Then
    assert retrieved_bill.bill_id == saved_bill.bill_id
    assert retrieved_bill.bill_title == saved_bill.bill_title


def test_get_nonexistent_bill(db_handler: DBHandler):
    # When
    result = db_handler.get_bill("nonexistent_id")

    # Then
    assert result is None


def test_read_all_value_table(db_handler: DBHandler, sample_bill_params):
    if db_handler.check_bill_exists(sample_bill_params["bill_id"]):
        db_handler.del_bill(sample_bill_params["bill_id"])
    # Given
    db_handler.save_bill(sample_bill_params)

    # When
    results = db_handler.get_all_value_tables()

    # Then
    assert len(results) > 0
    assert isinstance(results[0], Bill)


def test_read_value_table(db_handler: DBHandler, sample_bill_params):
    if db_handler.check_bill_exists(sample_bill_params["bill_id"]):
        db_handler.del_bill(sample_bill_params["bill_id"])
    # Given
    saved_bill = db_handler.save_bill(sample_bill_params)

    # When
    result = db_handler.get_value_table(sample_bill_params["bill_id"])

    # Then
    assert result.bill_id == saved_bill.bill_id


def test_update_value(db_handler: DBHandler, sample_bill_params):
    if db_handler.check_bill_exists(sample_bill_params["bill_id"]):
        db_handler.del_bill(sample_bill_params["bill_id"])
    # Given
    db_handler.save_bill(sample_bill_params)
    new_title = "Updated Title"

    # When
    db_handler.update_bill_value(sample_bill_params["bill_id"], "bill_title", new_title)

    # Then
    updated_bill = db_handler.get_bill(sample_bill_params["bill_id"])
    assert updated_bill.bill_title == new_title


def test_del_bill(db_handler: DBHandler, sample_bill_params):
    if db_handler.check_bill_exists(sample_bill_params["bill_id"]):
        db_handler.del_bill(sample_bill_params["bill_id"])
    # Given
    db_handler.save_bill(sample_bill_params)

    # When
    db_handler.del_bill(sample_bill_params["bill_id"])

    # Then
    assert db_handler.get_bill(sample_bill_params["bill_id"]) is None
