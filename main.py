import deepl
import requests
import yaml
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional

from mochi import (
    MochiConfig,
    get_mochi_config,
    create_card_on_mochi,
)

from config import (
    get_mochi_api_key,
    save_mochi_api_key,
    get_deepl_api_key,
    save_deepl_api_key,
    get_selected_deck_id,
    save_selected_deck_id,
)

CARDS_FILE_NAME = "cards.yaml"

MYMEMORY_BASE_URL = "https://api.mymemory.translated.net/get"


@dataclass
class Card:
    id: int
    front: str
    back: str
    created_at: str
    language_pair: str


def translate_with_mymemory(
    text: str, from_lang: str, to_lang: str
) -> Optional[str]:
    """
    Translate text using MyMemory Translation API (free service)

    :param text: The text to translate
    :param from_lang: The source language code (e.g., 'en' for English)
    :param to_lang: The target language code (e.g., 'es' for Spanish
    :return: The translated text or None if an error occurred
    """
    params = {"q": text, "langpair": f"{from_lang}|{to_lang}"}

    try:
        response = requests.get(MYMEMORY_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"MyMemory translation request failed: {e}")
        return None

    data = response.json()
    if data["responseStatus"] != 200:
        print(f"Translation error: {data['responseDetails']}")
        return None
    translated_text = data["responseData"]["translatedText"]
    return translated_text


def translate_with_deepl(
    deepl_translator: deepl.Translator, text: str, from_lang: str, to_lang: str
) -> Optional[str]:
    """
    Translate text using DeepL API.

    :param text: The text to translate.
    :param from_lang: The source language code (e.g., 'en' for English)
    :param to_lang: The target language code (e.g., 'es' for Spanish
    :return: The translated text or None if an error occurred.
    """
    try:
        result = deepl_translator.translate_text(
            text, source_lang=from_lang, target_lang=to_lang
        )
    except deepl.DeepLException as e:
        print(f"DeepL translation error: {e}")
        return None

    if isinstance(result, list):
        # DeepL can return a list when multiple sentences are translated
        result = result[0]
    return result.text


class TraduzClient:
    """
    The main client for the Traduz application, handling translations, card management, and user input.
    """

    def __init__(self):
        self.selected_deck_id: Optional[str] = None
        self.deepl_translator: Optional[deepl.Translator] = None
        self.mochi_config: Optional[MochiConfig] = None

    def setup_mochi_integration(self) -> MochiConfig | None:
        """
        Set up Mochi integration if user wants it.

        :return: True if integration was set up successfully, False otherwise.
        """
        print("\n🃏 Mochi Cards Integration")
        print("-" * 30)

        use_mochi = (
            input("Would you like to connect to Mochi Cards? (y/n): ")
            .strip()
            .lower()
        )

        if use_mochi not in ["y", "yes"]:
            return None

        existing_api_key = get_mochi_api_key()
        existing_deck_id = get_selected_deck_id()
        if mochi_config := get_mochi_config(existing_api_key, existing_deck_id):
            self.mochi_config = mochi_config
            save_mochi_api_key(mochi_config.api_key)
            save_selected_deck_id(mochi_config.selected_deck_id)
            return mochi_config
        return None

    def setup_deepl_integration(self) -> bool:
        """
        Set up DeepL integration if user wants it.

        :return: True if integration was set up successfully, False otherwise.
        """
        print("\n🌐 DeepL Translation Integration")
        print("-" * 30)

        use_deepl = (
            input(
                "Would you like to connect to DeepL for translations? (y/n): "
            )
            .strip()
            .lower()
        )

        if use_deepl not in ["y", "yes"]:
            return False

        if (api_key := self._get_deepl_api_key()) is None:
            return False

        self.deepl_translator = deepl.Translator(api_key)
        # Test the API key with a simple translation
        try:
            self.deepl_translator.translate_text("Hello", target_lang="ES")
        except deepl.DeepLException as e:
            print(f"❌ DeepL error: {e}")
            self.deepl_translator = None
            return False

        save_deepl_api_key(api_key)
        return True

    def _get_deepl_api_key(self) -> Optional[str]:
        """
        Prompt user for DeepL API key if not already set.

        :return: The DeepL API key if provided, None otherwise.
        """
        # Check if API key already exists
        existing_api_key = get_deepl_api_key()

        if existing_api_key:
            print("✅ Found existing DeepL API key.")
            use_existing = (
                input("Use existing DeepL API key? (y/n): ").strip().lower()
            )
            if use_existing in ["y", "yes"]:
                return existing_api_key

        # Get new API key
        print("\n🔑 To connect to DeepL, you need an API key.")
        print("   1. Go to https://www.deepl.com/pro-api")
        print(
            "   2. Sign up for an account and find your API key in the Account"
            " settings"
        )
        print("   3. Copy and paste it below")

        api_key = input("\nEnter your DeepL API key: ").strip()

        if not api_key:
            print("❌ No API key provided. DeepL integration disabled.")
            return None
        return api_key

    def load_existing_cards(self) -> list[Card]:
        """
        Load existing cards from YAML file.

        :return: A list of the loaded cards.
        """
        if os.path.exists(CARDS_FILE_NAME):
            try:
                with open(CARDS_FILE_NAME) as file:
                    data = yaml.safe_load(file) or []
                    return [Card(**card_data) for card_data in data]
            except Exception as e:
                print(f"Error loading existing cards: {e}")
                return []
        return []

    def save_card(
        self, from_text: str, to_text: str, from_language: str, to_language: str
    ) -> Card:
        """
        Save a new translation card to the YAML file and optionally to Mochi.

        :param from_text: The source text for the card.
        :param to_text: The translated text for the card.
        :return: The newly created Card object.
        """
        cards = self.load_existing_cards()

        new_card = Card(
            id=len(cards) + 1,
            front=from_text,
            back=to_text,
            created_at=datetime.now().isoformat(),
            language_pair=f"{from_language}-{to_language}",
        )

        cards.append(new_card)
        print(CARDS_FILE_NAME)
        with open(CARDS_FILE_NAME, "w") as file:
            yaml.dump(
                [asdict(card) for card in cards],
                file,
                allow_unicode=True,
            )

        # Also create card in Mochi if configured
        mochi_success = False
        if self.mochi_config:
            mochi_success = create_card_on_mochi(
                self.mochi_config, front=from_text, back=to_text
            )

        print("✅ Card saved successfully!")
        print(f"   Front ({from_language}): {from_text}")
        print(f"   Back ({to_language}): {to_text}")

        if self.mochi_config:
            if mochi_success:
                print("   🃏 Also added to Mochi deck!")
            else:
                print("   ⚠️  Saved locally but failed to add to Mochi")

        return new_card

    def translate_query(self, query: str, from_lang: str, to_lang: str) -> bool:
        """
        Translate the given English query and save the result as a card.

        :param english_query: The English text to translate.
        :return: True if the card was created successfully, False otherwise.
        """
        print(f"🔄 Translating: '{query}'")

        if self.deepl_translator:
            translation = translate_with_deepl(
                self.deepl_translator,
                query,
                from_lang=from_lang,
                to_lang=to_lang,
            )
        else:
            translation = translate_with_mymemory(
                query, from_lang=from_lang, to_lang=to_lang
            )

        if translation:
            self.save_card(query, translation, from_lang, to_lang)
            return True
        else:
            print("❌ Translation failed. Card not created.")
            return False

    def display_all_cards(self) -> None:
        """
        Display (print) all existing translation cards.
        """
        cards = self.load_existing_cards()
        if not cards:
            print("No cards found.")
            return

        print(f"\n📚 All Translation Cards ({len(cards)} total):")
        print("-" * 50)
        for card in cards:
            print(f"ID: {card.id}")
            print(f"Front: {card.front}")
            print(f"Back: {card.back}")
            print(f"Created: {card.created_at}")
            print("-" * 30)


def main() -> None:
    print("🌍 Traduz - English to Spanish Translation Cards")
    print("=" * 50)

    traduz_client = TraduzClient()

    # Set up Mochi and DeepL integration at startup
    use_mochi = traduz_client.setup_mochi_integration()
    if not use_mochi:
        print("📝 Cards will only be saved to local YAML file.")
    else:
        print("✅ Successfully connected to Mochi Cards!")

    use_deepl = traduz_client.setup_deepl_integration()
    if not use_deepl:
        print("🔤 Translations will use MyMemory (free service).")
    else:
        print("✅ Successfully connected to DeepL!")

    while True:
        print("\nOptions:")
        print("1. Create new translation card")
        print("2. View all cards")
        print("3. Exit")

        choice = input("\nSelect an option (1-3): ").strip()

        if choice == "1":
            print("\nLanguage Options: ")
            print("1. English to Spanish")
            print("2. Spanish to English")
            choice = input("\nSelect an option (1-2): ").strip()
            if choice == "1":
                from_lang, to_lang = "EN", "ES"
            elif choice == "2":
                from_lang, to_lang = "ES", "EN-US"
            else:
                print("❌ Invalid choice. Please select 1 or 2.")
                continue
            query = input(
                f"\n📝 Enter text ({from_lang}) to translate: "
            ).strip()

            if not query:
                print("❌ Please enter some text to translate.")
                continue

            traduz_client.translate_query(query, from_lang, to_lang)

        elif choice == "2":
            traduz_client.display_all_cards()

        elif choice == "3":
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice. Please select 1, 2, or 3.")


if __name__ == "__main__":
    main()
