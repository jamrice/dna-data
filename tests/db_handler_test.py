import pytest
from sqlalchemy.orm import Session
from src.models import Bill
from src.db_handler import DBManager
from datetime import datetime
import src.database as database


@pytest.fixture
def db_session():
    db = next(database.get_db())
    return db


@pytest.fixture
def db_manager(db_session):
    return DBManager(db_session)


@pytest.fixture
def sample_bill_params():
    return [
        "test_id",
        "https://likms.assembly.go.kr/bill/billDetail.do?billId=PRC_TEST",
        "11111111",
        "테스트 법안",
        "테스트 내용",
        "https://test.pdf",
        "2024-01-01",
        "22",
    ]


@pytest.fixture
def before_clean_bill(db_manager, sample_bill_params):
    db_manager.del_bill(sample_bill_params[0])


def test_save_bill(db_manager, sample_bill_params):
    if db_manager.check_bill_exists(sample_bill_params[0]):
        db_manager.del_bill(sample_bill_params[0])

    # When
    bill = db_manager.save_bill(sample_bill_params)

    # Then
    assert bill.bill_id == sample_bill_params[0]
    assert bill.url == sample_bill_params[1]
    assert bill.num == int(sample_bill_params[2])
    assert bill.title == sample_bill_params[3]
    assert bill.body == sample_bill_params[4]
    assert bill.pdf_url == sample_bill_params[5]
    assert bill.date.isoformat() == sample_bill_params[6]
    assert bill.ord_num == int(sample_bill_params[7])


def test_get_bill(db_manager, sample_bill_params):
    if db_manager.check_bill_exists(sample_bill_params[0]):
        db_manager.del_bill(sample_bill_params[0])
    # Given
    saved_bill = db_manager.save_bill(sample_bill_params)

    # When
    retrieved_bill = db_manager.get_bill(sample_bill_params[0])

    # Then
    assert retrieved_bill.bill_id == saved_bill.bill_id
    assert retrieved_bill.title == saved_bill.title


def test_get_nonexistent_bill(db_manager):
    # When
    result = db_manager.get_bill("nonexistent_id")

    # Then
    assert result is None


def test_del_bill(db_manager, sample_bill_params):
    if db_manager.check_bill_exists(sample_bill_params[0]):
        db_manager.del_bill(sample_bill_params[0])
    # Given
    db_manager.save_bill(sample_bill_params)

    # When
    db_manager.del_bill(sample_bill_params[0])

    # Then
    assert db_manager.get_bill(sample_bill_params[0]) is None


def test_read_all_value_table(db_manager, sample_bill_params):
    if db_manager.check_bill_exists(sample_bill_params[0]):
        db_manager.del_bill(sample_bill_params[0])
    # Given
    db_manager.save_bill(sample_bill_params)

    # When
    results = db_manager.read_all_value_table()

    # Then
    assert len(results) > 0
    assert isinstance(results[0], Bill)


def test_read_value_table(db_manager, sample_bill_params):
    if db_manager.check_bill_exists(sample_bill_params[0]):
        db_manager.del_bill(sample_bill_params[0])
    # Given
    saved_bill = db_manager.save_bill(sample_bill_params)

    # When
    result = db_manager.read_value_table(sample_bill_params[0])

    # Then
    assert result.bill_id == saved_bill.bill_id


def test_update_value(db_manager, sample_bill_params):
    if db_manager.check_bill_exists(sample_bill_params[0]):
        db_manager.del_bill(sample_bill_params[0])
    # Given
    db_manager.save_bill(sample_bill_params)
    new_title = "Updated Title"

    # When
    db_manager.update_value(sample_bill_params[0], "title", new_title)

    # Then
    updated_bill = db_manager.get_bill(sample_bill_params[0])
    assert updated_bill.title == new_title
