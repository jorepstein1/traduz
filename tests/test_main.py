from dataclasses import asdict
import deepl
import requests
import yaml

from unittest.mock import Mock, patch
from main import (
    TraduClient,
    translate_with_mymemory,
    translate_with_deepl,
    CARDS_FILE_NAME,
    Card,
)

# Translation function tests


@patch("main.requests.get")
def test_translate_with_mymemory_success(mock_get):
    """
    Test successful MyMemory translation
    """
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "responseStatus": 200,
        "responseData": {"translatedText": "Hola"},
    }
    mock_get.return_value = mock_response
    result = translate_with_mymemory("Hello", "en", "es")

    assert result == "Hola"
    mock_get.assert_called_once()


@patch("main.requests.get")
def test_translate_with_mymemory_failure(mock_get):
    """
    Test MyMemory translation failure
    """
    mock_get.side_effect = requests.exceptions.RequestException("Network error")

    result = translate_with_mymemory("Hello", "en", "es")

    assert result is None


def test_translate_with_deepl_success():
    """
    Test successful DeepL translation

    For future testing, consider using the `deepl-mock` server
    """
    translator = deepl.Translator("mock_api_key")
    mock_result = Mock()
    mock_result.text = "Hola"

    with patch.object(
        translator,
        "translate_text",
        return_value=mock_result,
    ):
        result = translate_with_deepl(translator, "Hello", "en", "es")

    assert result == "Hola"


def test_translate_with_deepl_failure():
    """
    Test successful DeepL translation

    For future testing, consider using the `deepl-mock` server
    """
    translator = deepl.Translator("mock_api_key")
    result = translate_with_deepl(translator, "Hello", "en", "es")

    assert result is None


# TraduClient tests


def test_load_existing_cards_empty(temp_cwd):
    """
    Test loading cards when file doesn't exist
    """
    tradu_client = TraduClient()
    cards = tradu_client.load_existing_cards()
    assert cards == []


def test_load_existing_cards_with_data(temp_cwd):
    """
    Test loading existing cards
    """
    test_card = Card(
        id=1,
        front="Hello",
        back="Hola",
        created_at="2025-09-05T10:00:00",
        language_pair="en-es",
    )
    with open(CARDS_FILE_NAME, "w") as f:
        yaml.dump([asdict(test_card)], f)

    tradu_client = TraduClient()
    cards = tradu_client.load_existing_cards()
    assert len(cards) == 1
    assert cards[0].id == 1
    assert cards[0].front == "Hello"
    assert cards[0].back == "Hola"


def test_save_card_success(temp_cwd):
    """
    Test successful card saving
    """
    tradu_client = TraduClient()
    new_card = tradu_client.save_card("Hello", "Hola", "EN", "ES")
    assert new_card.front == "Hello"
    assert new_card.back == "Hola"
    assert new_card.language_pair == "EN-ES"

    # Verify card was saved
    cards = tradu_client.load_existing_cards()
    assert len(cards) == 1
    assert cards[0] == new_card


def test_translate_query_success(temp_cwd):
    """
    Test successful translation query
    """
    # Mock MyMemory response
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "responseStatus": 200,
        "responseData": {"translatedText": "Hola"},
    }

    tradu_client = TraduClient()
    with patch("main.translate_with_mymemory", return_value="Hola"):
        result = tradu_client.translate_query("Hello", "en", "es")

    assert result is True

    # Verify card was created
    cards = tradu_client.load_existing_cards()
    assert len(cards) == 1
    assert cards[0].front == "Hello"
    assert cards[0].back == "Hola"


def test_translate_query_failure(temp_cwd):
    """
    Test translation query failure
    """
    tradu_client = TraduClient()
    with patch(
        "main.requests.get",
        side_effect=requests.exceptions.RequestException("Network error"),
    ):
        result = tradu_client.translate_query("Hello", "en", "es")

    assert result is False

    # Verify no card was created
    cards = tradu_client.load_existing_cards()
    assert len(cards) == 0


def test_end_to_end_translation(
    temp_cwd,
):
    """
    Test end-to-end translation workflow
    """

    # Mock MyMemory response
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "responseStatus": 200,
        "responseData": {"translatedText": "Hola mundo"},
    }

    # Create client and translate
    client = TraduClient()
    with patch("main.requests.get", return_value=mock_response):
        result = client.translate_query("Hello world", "en", "es")

    assert result is True

    # Verify card was saved
    cards = client.load_existing_cards()
    assert len(cards) == 1
    assert cards[0].front == "Hello world"
    assert cards[0].back == "Hola mundo"
    assert cards[0].language_pair == "en-es"
