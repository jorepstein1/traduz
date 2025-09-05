import requests
from unittest.mock import Mock, patch
from mochi import (
    MochiConfig,
    create_card_on_mochi,
    get_mochi_template,
    get_all_mochi_decks,
)


def test_get_template_success():
    """
    Test successful template retrieval
    """
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "docs": [
            {
                "id": "template123",
                "fields": {
                    "field1": {"id": "front456", "name": "Front"},
                    "field2": {"id": "back789", "name": "Back"},
                },
            }
        ]
    }

    with patch("main.requests.get", return_value=mock_response):
        template_id, front_id, back_id = get_mochi_template("mock_api_key")

    assert template_id == "template123"
    assert front_id == "front456"
    assert back_id == "back789"


def test_get_decks_success():
    """
    Test successful deck retrieval
    """
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "docs": [
            {"id": "deck1", "name": "Spanish Vocabulary"},
            {"id": "deck2", "name": "French Phrases"},
        ]
    }
    with patch("main.requests.get", return_value=mock_response):
        decks = get_all_mochi_decks("mock_api_key")

    assert len(decks) == 2
    assert decks[0].id == "deck1"
    assert decks[0].name == "Spanish Vocabulary"
    assert decks[1].id == "deck2"
    assert decks[1].name == "French Phrases"


def test_get_decks_failure():
    """
    Test deck retrieval failure
    """
    with patch(
        "main.requests.get",
        side_effect=requests.exceptions.RequestException("Network error"),
    ):
        decks = get_all_mochi_decks("mock_api_key")

    assert decks == []


def get_mochi_config() -> MochiConfig:
    return MochiConfig(
        api_key="mock_api_key",
        selected_deck_id="deck123",
        template_id="template123",
        front_id="front456",
        back_id="back789",
    )


def test_create_card_success():
    """
    Test successful card creation
    """
    mochi_config = get_mochi_config()
    with patch("main.requests.post"):
        result = create_card_on_mochi(mochi_config, "Hello", "Hola")
    assert result is True


def test_create_card_failure():
    """
    Test card creation failure
    """
    mochi_config = get_mochi_config()
    with patch(
        "main.requests.post",
        side_effect=requests.exceptions.RequestException("API error"),
    ):
        result = create_card_on_mochi(mochi_config, "Hello", "Hola")

    assert result is False
