from config import (
    get_deepl_api_key,
    get_mochi_api_key,
    get_selected_deck_id,
    load_config,
    save_config,
    save_deepl_api_key,
    save_mochi_api_key,
    save_selected_deck_id,
)


def test_load_empty_config(temp_cwd):
    """
    Test loading config when file doesn't exist.
    """
    config = load_config()
    assert config == {}


def test_save_and_load_config(temp_cwd):
    """
    Test saving and loading configuration.
    """
    test_config = {
        "mochi": {"api_key": "test_key", "selected_deck_id": "deck123"},
        "deepl": {"api_key": "deepl_key"},
    }
    assert save_config(test_config) is True
    loaded_config = load_config()
    assert loaded_config == test_config


def test_get_mochi_api_key(temp_cwd):
    """
    Test getting Mochi API key
    """
    test_config = {"mochi": {"api_key": "test_mochi_key"}}

    # Test when no config exists
    assert get_mochi_api_key() is None

    # Test when config exists
    save_config(test_config)
    assert get_mochi_api_key() == "test_mochi_key"


def test_save_mochi_api_key(temp_cwd):
    """
    Test saving Mochi API key
    """
    assert save_mochi_api_key("new_key") is True
    assert get_mochi_api_key() == "new_key"


def test_get_deepl_api_key(temp_cwd):
    """
    Test getting DeepL API key
    """
    # Test when no config exists
    assert get_deepl_api_key() is None

    # Test when config exists
    test_config = {"deepl": {"api_key": "test_deepl_key"}}
    save_config(test_config)
    assert get_deepl_api_key() == "test_deepl_key"


def test_save_deepl_api_key(temp_cwd):
    """
    Test saving DeepL API key
    """
    assert save_deepl_api_key("deepl_key") is True
    assert get_deepl_api_key() == "deepl_key"


def test_get_selected_deck_id(temp_cwd):
    """
    Test getting selected deck ID
    """
    # Test when no config exists
    assert get_selected_deck_id() is None

    # Test when config exists
    test_config = {"mochi": {"selected_deck_id": "deck456"}}
    save_config(test_config)
    assert get_selected_deck_id() == "deck456"


def test_save_selected_deck_id(temp_cwd):
    """
    Test saving selected deck ID
    """
    assert save_selected_deck_id("deck789") is True
    assert get_selected_deck_id() == "deck789"
