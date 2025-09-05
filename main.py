import requests
import yaml
import os
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Any

CONFIG_FILE_NAME = "config.yaml"
CARDS_FILE_NAME = "cards.yaml"


@dataclass
class Card:
    id: int
    front: str
    back: str
    created_at: str
    language_pair: str


@dataclass
class MochiDeck:
    id: str
    name: str


class MochiClient:
    def __init__(self, api_key: str):
        """
        :param api_key: The API key for authenticating with the Mochi API.
        """
        self.api_key = api_key
        self.base_url = "https://app.mochi.cards/api"
        self.template_id, self.front_id, self.back_id = self._get_template()

    def _get_template(self) -> tuple[str, str, str]:
        """
        Get the card template from Mochi.  Assumes a template with "Front" and "Back" fields exists.

        :return: A tuple containing the template ID, front field ID, and back field ID.
        """
        template_id, front_id, back_id = "", "", ""

        try:
            response = requests.get(
                f"{self.base_url}/templates",
                auth=(self.api_key, ""),
                timeout=10,
            )
            response.raise_for_status()
            templates_data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve templates from Mochi: {e}")
            return "", "", ""

        if (
            templates_data
            and "docs" in templates_data
            and len(templates_data["docs"]) > 0
        ):
            for template_dict in templates_data["docs"]:
                template_id = template_dict["id"]
                for field_dict in template_dict["fields"].values():
                    if field_dict["name"] == "Front":
                        front_id = field_dict["id"]
                    if field_dict["name"] == "Back":
                        back_id = field_dict["id"]
        if not front_id or not back_id:
            print("Could not find template containing Front/Back fields.")
            return "", "", ""
        return template_id, front_id, back_id

    def get_template(self) -> tuple[str, str, str]:
        """
        Get the card template details.

        :return: A tuple containing the template ID, front field ID, and back field ID.
        """
        return self.template_id, self.front_id, self.back_id

    def get_decks(self) -> list[MochiDeck]:
        """
        Retrieve user's decks from Mochi.

        :return: A list of user's decks.
        """
        try:
            response = requests.get(
                f"{self.base_url}/decks", auth=(self.api_key, ""), timeout=10
            )
            response.raise_for_status()

            decks_data = response.json()
            decks = []
            for deck_data in decks_data.get("docs", []):
                deck = MochiDeck(
                    id=deck_data["id"],
                    name=deck_data["name"],
                )
                decks.append(deck)
            return decks

        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve decks: {e}")
            return []
        except Exception as e:
            print(f"Error processing decks: {e}")
            return []

    def create_card(self, deck_id: str, front: str, back: str) -> bool:
        """
        Create a new card in the specified deck.

        :param deck_id: The ID of the deck to add the card to.
        :param front: The content for the front of the card.
        :param back: The content for the back of the card.
        :return: True if the card was created successfully, False otherwise.
        """
        card_data = {
            "content": "",
            "deck-id": deck_id,
            "template-id": self.template_id,
            "fields": {
                self.front_id: {"id": self.front_id, "value": front},
                self.back_id: {"id": self.back_id, "value": back},
            },
            "review-reverse?": True,
        }

        try:
            response = requests.post(
                f"{self.base_url}/cards",
                auth=(self.api_key, ""),
                json=card_data,
                timeout=10,
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Failed to create Mochi card: {e}")
            return False


class ConfigManager:
    """
    Persistent configuration manager for user's preferences
    """

    def load_config(self) -> dict[str, Any]:
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

    def save_config(self, config: dict[str, Any]) -> bool:
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

    def get_mochi_api_key(self) -> Optional[str]:
        """
        Get Mochi API key from config.

        :return: The Mochi API key if it exists, None otherwise.
        """
        config = self.load_config()
        return config.get("mochi", {}).get("api_key")

    def save_mochi_api_key(self, api_key: str) -> bool:
        """
        Save Mochi API key to config.

        :param api_key: The Mochi API key to save.
        :return: True if the API key was saved successfully, False otherwise.
        """
        config = self.load_config()
        if "mochi" not in config:
            config["mochi"] = {}
        config["mochi"]["api_key"] = api_key
        return self.save_config(config)

    def get_selected_deck_id(self) -> Optional[str]:
        """
        Get selected deck ID from config.

        :return: The selected deck ID if it exists, None otherwise.
        """
        config = self.load_config()
        return config.get("mochi", {}).get("selected_deck_id")

    def save_selected_deck_id(self, deck_id: str) -> bool:
        """
        Save selected deck ID to config.

        :param deck_id: The selected deck ID to save.
        :return: True if the deck ID was saved successfully, False otherwise.
        """
        config = self.load_config()
        if "mochi" not in config:
            config["mochi"] = {}
        config["mochi"]["selected_deck_id"] = deck_id
        return self.save_config(config)


class Translator:
    def __init__(self):
        self.base_url = "https://api.mymemory.translated.net/get"
        self.config_manager = ConfigManager()
        self.mochi_client: Optional[MochiClient] = None
        self.selected_deck_id: Optional[str] = None

    def setup_mochi_integration(self) -> bool:
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
            print("📝 Cards will only be saved to local YAML file.")
            return False

        if (api_key := self._get_api_key()) is None:
            return False

        # Test the API key
        self.mochi_client = MochiClient(api_key)
        decks = self.mochi_client.get_decks()

        if not decks:
            print("❌ Failed to connect to Mochi. Please check your API key.")
            return False

        # Save API key
        if self.config_manager.save_mochi_api_key(api_key):
            print("✅ API key saved successfully!")
        else:
            print("⚠️ API key works but couldn't save to config file.")

        return self._select_deck()

    def _get_api_key(self) -> Optional[str]:
        """
        Prompt user for Mochi API key if not already set.

        :return: The Mochi API key if provided, None otherwise.
        """

        # Check if API key already exists
        existing_api_key = self.config_manager.get_mochi_api_key()

        if existing_api_key:
            print("✅ Found existing Mochi API key.")
            use_existing = (
                input("Use existing API key? (y/n): ").strip().lower()
            )
            if use_existing in ["y", "yes"]:
                return existing_api_key

        # Get new API key
        print("\n🔑 To connect to Mochi, you need an API key.")
        print("   1. Go to https://app.mochi.cards/")
        print("   2. Open the Account Settings and create an API key")
        print("   3. Copy and paste it below")

        api_key = input("\nEnter your Mochi API key: ").strip()

        if not api_key:
            print("❌ No API key provided. Mochi integration disabled.")
            return None
        return api_key

    def _select_deck(self) -> bool:
        """
        Allow user to select a deck. This deck will be used for adding new cards.

        :return: True if a deck was selected successfully, False otherwise.
        """
        if not self.mochi_client:
            return False

        # Check if deck is already selected
        existing_deck_id = self.config_manager.get_selected_deck_id()
        if existing_deck_id:
            use_existing = (
                input("Use previously selected deck? (y/n): ").strip().lower()
            )
            if use_existing in ["y", "yes"]:
                self.selected_deck_id = existing_deck_id
                print("✅ Using previously selected deck.")
                return True

        decks = self.mochi_client.get_decks()

        if not decks:
            print(
                "❌ No decks found. Please create a deck on Mochi Cards first."
            )
            return False

        print(f"\n📚 Available Decks ({len(decks)} found):")
        print("-" * 40)

        for idx, deck in enumerate(decks, 1):
            print(f"{idx}. {deck.name}")

        while True:
            try:
                choice = input(f"\nSelect a deck (1-{len(decks)}): ").strip()
                deck_index = int(choice) - 1

                if 0 <= deck_index < len(decks):
                    selected_deck = decks[deck_index]
                    self.selected_deck_id = selected_deck.id

                    # Save selected deck
                    if self.config_manager.save_selected_deck_id(
                        selected_deck.id
                    ):
                        print(f"✅ Selected deck: {selected_deck.name}")
                        return True
                    else:
                        print(
                            "⚠️  Deck selected but couldn't save to config file."
                        )
                        return True
                else:
                    print("❌ Invalid selection. Please try again.")

            except ValueError:
                print("❌ Please enter a valid number.")

    def create_mochi_card(self, front: str, back: str) -> bool:
        """
        Create a card in Mochi.

        :param front: The front text of the card.
        :param back: The back text of the card.
        :return: True if the card was created successfully, False otherwise.
        """
        if not self.mochi_client or not self.selected_deck_id:
            return False

        return self.mochi_client.create_card(self.selected_deck_id, front, back)

    def translate_text(self, text: str) -> Optional[str]:
        """
        Translate text using MyMemory Translation API (free service)

        :param text: The text to translate
        :return: The translated text or None if an error occurred
        """
        try:
            params = {"q": text, "langpair": "en|es"}

            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get("responseStatus") == 200:
                translated_text = data["responseData"]["translatedText"]
                return translated_text
            else:
                print(
                    f"Translation error: {data.get('responseDetails', 'Unknown error')}"
                )
                return None

        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None
        except Exception as e:
            print(f"Translation failed: {e}")
            return None

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

    def save_card(self, english_text: str, spanish_text: str) -> bool:
        """
        Save a new translation card to the YAML file and optionally to Mochi.

        :param english_text: The English text for the card.
        :param spanish_text: The Spanish text for the card.
        :return: True if the card was saved successfully, False otherwise.
        """
        try:
            cards = self.load_existing_cards()

            new_card = Card(
                id=len(cards) + 1,
                front=english_text,
                back=spanish_text,
                created_at=datetime.now().isoformat(),
                language_pair="en-es",
            )

            cards.append(new_card)

            with open(CARDS_FILE_NAME, "w") as file:
                yaml.dump(
                    [card.__dict__ for card in cards],
                    file,
                    allow_unicode=True,
                )

            # Also create card in Mochi if configured
            mochi_success = False
            if self.mochi_client and self.selected_deck_id:
                mochi_success = self.create_mochi_card(
                    english_text, spanish_text
                )

            print("✅ Card saved successfully!")
            print(f"   Front (English): {english_text}")
            print(f"   Back (Spanish): {spanish_text}")

            if self.mochi_client and self.selected_deck_id:
                if mochi_success:
                    print("   🃏 Also added to Mochi deck!")
                else:
                    print("   ⚠️  Saved locally but failed to add to Mochi")

            return True

        except Exception as e:
            print(f"Error saving card: {e}")
            return False

    def create_translation_card(self, english_query: str) -> bool:
        """
        Create a new translation card.

        :param english_query: The English text to translate.
        :return: True if the card was created successfully, False otherwise.
        """
        print(f"🔄 Translating: '{english_query}'")

        spanish_translation = self.translate_text(english_query)

        if spanish_translation and self.save_card(
            english_query, spanish_translation
        ):
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

    translator = Translator()

    # Set up Mochi integration at startup
    translator.setup_mochi_integration()

    while True:
        print("\nOptions:")
        print("1. Create new translation card")
        print("2. View all cards")
        print("3. Exit")

        choice = input("\nSelect an option (1-3): ").strip()

        if choice == "1":
            english_query = input(
                "\n📝 Enter English text to translate: "
            ).strip()

            if not english_query:
                print("❌ Please enter some text to translate.")
                continue

            translator.create_translation_card(english_query)

        elif choice == "2":
            translator.display_all_cards()

        elif choice == "3":
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice. Please select 1, 2, or 3.")


if __name__ == "__main__":
    main()
