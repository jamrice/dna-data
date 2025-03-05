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
        "url": "https://likms.assembly.go.kr/bill/billDetail.do?billId=PRC_TEST",
        "num": "11111111",
        "title": "테스트 법안",
        "body": "테스트 내용",
        "pdf_url": "https://test.pdf",
        "date": "2024-01-01",
        "ord_num": "22",
    }


@pytest.fixture
def before_clean_bill(db_handler, sample_bill_params):
    db_handler.del_bill(sample_bill_params["bill_id"])


def test_save_bill(db_handler, sample_bill_params):
    if db_handler.check_bill_exists(sample_bill_params["bill_id"]):
        db_handler.del_bill(sample_bill_params["bill_id"])

    # When
    bill = db_handler.save_bill(sample_bill_params)

    # Then
    assert bill.bill_id == sample_bill_params["bill_id"]
    assert bill.url == sample_bill_params["url"]
    assert bill.num == int(sample_bill_params["num"])
    assert bill.title == sample_bill_params["title"]
    assert bill.body == sample_bill_params["body"]
    assert bill.pdf_url == sample_bill_params["pdf_url"]
    assert bill.date.isoformat() == sample_bill_params["date"]
    assert bill.ord_num == int(sample_bill_params["ord_num"])


def test_get_bill(db_handler, sample_bill_params):
    if db_handler.check_bill_exists(sample_bill_params["bill_id"]):
        db_handler.del_bill(sample_bill_params["bill_id"])
    # Given
    saved_bill = db_handler.save_bill(sample_bill_params)

    # When
    retrieved_bill = db_handler.get_bill(sample_bill_params["bill_id"])

    # Then
    assert retrieved_bill.bill_id == saved_bill.bill_id
    assert retrieved_bill.title == saved_bill.title


def test_get_nonexistent_bill(db_handler):
    # When
    result = db_handler.get_bill("nonexistent_id")

    # Then
    assert result is None


def test_del_bill(db_handler, sample_bill_params):
    if db_handler.check_bill_exists(sample_bill_params["bill_id"]):
        db_handler.del_bill(sample_bill_params["bill_id"])
    # Given
    db_handler.save_bill(sample_bill_params)

    # When
    db_handler.del_bill(sample_bill_params["bill_id"])

    # Then
    assert db_handler.get_bill(sample_bill_params["bill_id"]) is None


def test_read_all_value_table(db_handler, sample_bill_params):
    if db_handler.check_bill_exists(sample_bill_params["bill_id"]):
        db_handler.del_bill(sample_bill_params["bill_id"])
    # Given
    db_handler.save_bill(sample_bill_params)

    # When
    results = db_handler.get_all_value_table()

    # Then
    assert len(results) > 0
    assert isinstance(results[0], Bill)


def test_read_value_table(db_handler, sample_bill_params):
    if db_handler.check_bill_exists(sample_bill_params["bill_id"]):
        db_handler.del_bill(sample_bill_params["bill_id"])
    # Given
    saved_bill = db_handler.save_bill(sample_bill_params)

    # When
    result = db_handler.get_value_table(sample_bill_params["bill_id"])

    # Then
    assert result.bill_id == saved_bill.bill_id


def test_update_value(db_handler, sample_bill_params):
    if db_handler.check_bill_exists(sample_bill_params["bill_id"]):
        db_handler.del_bill(sample_bill_params["bill_id"])
    # Given
    db_handler.save_bill(sample_bill_params)
    new_title = "Updated Title"

    # When
    db_handler.update_value(sample_bill_params["bill_id"], "title", new_title)

    # Then
    updated_bill = db_handler.get_bill(sample_bill_params["bill_id"])
    assert updated_bill.title == new_title
