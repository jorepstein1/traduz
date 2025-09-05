from dataclasses import asdict
import deepl
from pathlib import Path
import pytest
import requests
import yaml
import os
from unittest.mock import Mock, patch
from main import (
    ConfigManager,
    TraduzClient,
    translate_with_mymemory,
    translate_with_deepl,
    CARDS_FILE_NAME,
    Card,
)


@pytest.fixture
def temp_cwd(tmp_path):
    """
    Fixture to change the current working directory to a temporary directory
    and then restore the original CWD after the test.
    """
    original_cwd = Path.cwd()  # Store the original CWD
    os.chdir(tmp_path)  # Change CWD to the temporary directory
    yield tmp_path  # Yield the temporary path for potential use in the test
    os.chdir(original_cwd)  # Restore the original CWD after the test


# ConfigManager tests


def test_load_empty_config(tmpdir):
    """
    Test loading config when file doesn't exist.
    """
    with tmpdir.as_cwd():
        config_manager = ConfigManager()
        config = config_manager.load_config()
    assert config == {}


def test_save_and_load_config(temp_cwd):
    """
    Test saving and loading configuration.
    """
    test_config = {
        "mochi": {"api_key": "test_key", "selected_deck_id": "deck123"},
        "deepl": {"api_key": "deepl_key"},
    }
    config_manager = ConfigManager()
    assert config_manager.save_config(test_config) is True
    loaded_config = config_manager.load_config()
    assert loaded_config == test_config


def test_get_mochi_api_key(temp_cwd):
    """
    Test getting Mochi API key
    """
    test_config = {"mochi": {"api_key": "test_mochi_key"}}

    # Test when no config exists

    config_manager = ConfigManager()
    assert config_manager.get_mochi_api_key() is None

    # Test when config exists
    config_manager.save_config(test_config)
    assert config_manager.get_mochi_api_key() == "test_mochi_key"


def test_save_mochi_api_key(temp_cwd):
    """
    Test saving Mochi API key
    """
    config_manager = ConfigManager()
    assert config_manager.save_mochi_api_key("new_key") is True
    assert config_manager.get_mochi_api_key() == "new_key"


def test_get_deepl_api_key(temp_cwd):
    """
    Test getting DeepL API key
    """
    config_manager = ConfigManager()
    # Test when no config exists
    assert config_manager.get_deepl_api_key() is None

    # Test when config exists
    test_config = {"deepl": {"api_key": "test_deepl_key"}}
    config_manager.save_config(test_config)
    assert config_manager.get_deepl_api_key() == "test_deepl_key"


def test_save_deepl_api_key(temp_cwd):
    """
    Test saving DeepL API key
    """
    config_manager = ConfigManager()
    assert config_manager.save_deepl_api_key("deepl_key") is True
    assert config_manager.get_deepl_api_key() == "deepl_key"


def test_get_selected_deck_id(temp_cwd):
    """
    Test getting selected deck ID
    """
    config_manager = ConfigManager()
    # Test when no config exists
    assert config_manager.get_selected_deck_id() is None

    # Test when config exists
    test_config = {"mochi": {"selected_deck_id": "deck456"}}
    config_manager.save_config(test_config)
    assert config_manager.get_selected_deck_id() == "deck456"


def test_save_selected_deck_id(temp_cwd):
    """
    Test saving selected deck ID
    """
    config_manager = ConfigManager()
    assert config_manager.save_selected_deck_id("deck789") is True
    assert config_manager.get_selected_deck_id() == "deck789"


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


# TraduzClient tests


def test_load_existing_cards_empty(temp_cwd):
    """
    Test loading cards when file doesn't exist
    """
    traduz_client = TraduzClient()
    cards = traduz_client.load_existing_cards()
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

    traduz_client = TraduzClient()
    cards = traduz_client.load_existing_cards()
    assert len(cards) == 1
    assert cards[0].id == 1
    assert cards[0].front == "Hello"
    assert cards[0].back == "Hola"


def test_save_card_success(temp_cwd):
    """
    Test successful card saving
    """
    traduz_client = TraduzClient()
    new_card = traduz_client.save_card("Hello", "Hola", "EN", "ES")
    assert new_card.front == "Hello"
    assert new_card.back == "Hola"
    assert new_card.language_pair == "EN-ES"

    # Verify card was saved
    cards = traduz_client.load_existing_cards()
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

    traduz_client = TraduzClient()
    with patch("main.requests.get", return_value=mock_response):
        result = traduz_client.translate_query("Hello", "en", "es")

    assert result is True

    # Verify card was created
    cards = traduz_client.load_existing_cards()
    assert len(cards) == 1
    assert cards[0].front == "Hello"
    assert cards[0].back == "Hola"


def test_translate_query_failure(temp_cwd):
    """
    Test translation query failure
    """
    traduz_client = TraduzClient()
    with patch(
        "main.requests.get",
        side_effect=requests.exceptions.RequestException("Network error"),
    ):
        result = traduz_client.translate_query("Hello", "en", "es")

    assert result is False

    # Verify no card was created
    cards = traduz_client.load_existing_cards()
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
    client = TraduzClient()
    with patch("main.requests.get", return_value=mock_response):
        result = client.translate_query("Hello world", "en", "es")

    assert result is True

    # Verify card was saved
    cards = client.load_existing_cards()
    assert len(cards) == 1
    assert cards[0].front == "Hello world"
    assert cards[0].back == "Hola mundo"
    assert cards[0].language_pair == "en-es"
