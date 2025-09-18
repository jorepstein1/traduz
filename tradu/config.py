import yaml
import os
from typing import Any

CONFIG_FILE_NAME = "config.yaml"


def load_config() -> dict[str, Any]:
    """
    Load configuration from YAML file.

    :return: The loaded configuration dict
    """
    if os.path.exists(CONFIG_FILE_NAME):
        try:
            with open(CONFIG_FILE_NAME) as file:
                return yaml.safe_load(file) or {}
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    return {}


def save_config(config: dict[str, Any]) -> bool:
    """
    Save configuration to YAML file.

    :param config: The configuration to save.
    :return: True if the configuration was saved successfully, False otherwise.
    """
    try:
        with open(CONFIG_FILE_NAME, "w") as file:
            yaml.dump(config, file)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


def get_mochi_api_key() -> str | None:
    """
    Get Mochi API key from config.

    :return: The Mochi API key if it exists, None otherwise.
    """
    config = load_config()
    return config.get("mochi", {}).get("api_key")


def save_mochi_api_key(api_key: str) -> bool:
    """
    Save Mochi API key to config.

    :param api_key: The Mochi API key to save.
    :return: True if the API key was saved successfully, False otherwise.
    """
    config = load_config()
    if "mochi" not in config:
        config["mochi"] = {}
    config["mochi"]["api_key"] = api_key
    return save_config(config)


def get_deepl_api_key() -> str | None:
    """
    Get DeepL API key from config.

    :return: The DeepL API key if it exists, None otherwise.
    """
    config = load_config()
    return config.get("deepl", {}).get("api_key")


def save_deepl_api_key(api_key: str) -> bool:
    """
    Save DeepL API key to config.

    :param api_key: The DeepL API key to save.
    :return: True if the API key was saved successfully, False otherwise.
    """
    config = load_config()
    if "deepl" not in config:
        config["deepl"] = {}
    config["deepl"]["api_key"] = api_key
    return save_config(config)


def get_selected_deck_id() -> str | None:
    """
    Get selected deck ID from config.

    :return: The selected deck ID if it exists, None otherwise.
    """
    config = load_config()
    return config.get("mochi", {}).get("selected_deck_id")


def save_selected_deck_id(deck_id: str) -> bool:
    """
    Save selected deck ID to config.

    :param deck_id: The selected deck ID to save.
    :return: True if the deck ID was saved successfully, False otherwise.
    """
    config = load_config()
    if "mochi" not in config:
        config["mochi"] = {}
    config["mochi"]["selected_deck_id"] = deck_id
    return save_config(config)
