import pytest
from unittest.mock import patch
from src.summary import Summarizer

@pytest.fixture
def mock_bill_extractor():
    with patch('src.summary.BillExtractor') as MockBillExtractor:
        mock_instance = MockBillExtractor.return_value
        mock_instance.bill_summary = "This is a test bill summary."
        yield mock_instance

@pytest.fixture
def mock_api_key_manager():
    with patch('src.summary.api_keyManager') as MockApiKeyManager:
        mock_instance = MockApiKeyManager.return_value
        mock_instance.get_ggl_api_key.return_value = "test_api_key"
        yield mock_instance

@pytest.fixture
def mock_genai():
    with patch('src.summary.genai') as MockGenai:
        mock_instance = MockGenai
        mock_instance.GenerativeModel.return_value.generate_content.return_value.text = "Generated text"
        yield mock_instance

@pytest.fixture
def mock_logger():
    with patch('src.summary.logger') as MockLogger:
        yield MockLogger

@pytest.fixture
def mock_db_manager():
    with patch('src.summary.db_manager') as MockDbManager:
        yield MockDbManager

def test_get_headline(mock_bill_extractor, mock_api_key_manager, mock_genai, mock_logger):
    summarizer = Summarizer(mock_bill_extractor.bill_summary)
    summarizer.headline = "Test Headline"
    assert summarizer.get_headline() == "Test Headline"

def test_get_paragraph(mock_bill_extractor, mock_api_key_manager, mock_genai, mock_logger):
    summarizer = Summarizer(mock_bill_extractor.bill_summary)
    summarizer.paragraph = "Test Paragraph"
    assert summarizer.get_paragraph() == "Test Paragraph"

def test_save_summary(mock_bill_extractor, mock_api_key_manager, mock_genai, mock_logger, mock_db_manager):
    """
    Test the save_summary method of the Summarizer class.

    This test verifies that the save_summary method correctly saves the summary
    data to the database using the mock_db_manager. It checks that the save_table
    method is called once with the correct parameters.

    Args:
        mock_bill_extractor (Mock): Mock object for the bill extractor.
        mock_api_key_manager (Mock): Mock object for the API key manager.
        mock_genai (Mock): Mock object for the GenAI.
        mock_logger (Mock): Mock object for the logger.
        mock_db_manager (Mock): Mock object for the database manager.

    Asserts:
        mock_db_manager.save_table.assert_called_once_with: Ensures that the
        save_table method is called once with the expected table name and data.
    """
    summarizer = Summarizer(mock_bill_extractor.bill_summary)
    summarizer.headline = "Test Headline"
    summarizer.paragraph = "Test Paragraph"
    summarizer.bill_id = "123"
    summarizer.conf_id = "456"
    summarizer.save_summary("localhost", "root", "password")
    mock_db_manager.save_table.assert_called_once_with(
        "bill_summary",
        ("headline", "body", "bill_id", "conf_id"),
        ("Test Headline", "Test Paragraph", "123", "456")
    )