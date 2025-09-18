import requests
from dataclasses import dataclass

MOCHI_BASE_URL = "https://app.mochi.cards/api"


@dataclass
class MochiDeck:
    id: str
    name: str


@dataclass
class MochiConfig:
    api_key: str
    selected_deck_id: str
    template_id: str
    front_id: str
    back_id: str


def get_mochi_config(
    existing_api_key: str | None, existing_deck_id: str | None
) -> MochiConfig | None:
    """
    Load Mochi configuration from the config file.

    :return: MochiConfig object if configuration exists, None otherwise.
    """
    if (api_key := get_mochi_api_key(existing_api_key)) is None:
        return None

    # Test the API key
    decks = get_all_mochi_decks(api_key)

    if not decks:
        print("❌ Failed to connect to Mochi. Please check your API key.")
        return None

    template_id, front_id, back_id = get_mochi_template(api_key)
    if not template_id or not front_id or not back_id:
        print(
            "❌ Could not find a valid template with Front/Back fields in"
            " Mochi."
        )
        return None

    selected_deck_id = select_mochi_deck(existing_deck_id, api_key)
    if not selected_deck_id:
        print("❌ No deck selected. Mochi integration disabled.")
        return None

    return MochiConfig(
        api_key=api_key,
        selected_deck_id=selected_deck_id,
        template_id=template_id,
        front_id=front_id,
        back_id=back_id,
    )


def get_mochi_api_key(existing_api_key: str | None) -> str | None:
    """
    Prompt user for Mochi API key if not already set.

    :return: The Mochi API key if provided, None otherwise.
    """
    if existing_api_key:
        print("✅ Found existing Mochi API key.")
        use_existing = input("Use existing API key? (y/n): ").strip().lower()
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


def select_mochi_deck(existing_deck_id: str | None, api_key: str) -> str | None:
    decks = []
    if existing_deck_id:
        use_existing = (
            input("Use previously selected deck? (y/n): ").strip().lower()
        )
        if use_existing in ["y", "yes"]:
            selected_deck_id = existing_deck_id
            print("✅ Using previously selected deck.")
            return selected_deck_id

        decks = get_all_mochi_decks(api_key)
    if not decks:
        print("❌ No decks found. Please create a deck on Mochi Cards first.")
        return None

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
                print(f"✅ Selected deck: {selected_deck.name}")
                return selected_deck.id
            else:
                print("❌ Invalid selection. Please try again.")
        except ValueError:
            print("❌ Please enter a valid number.")


def get_all_mochi_decks(api_key: str) -> list[MochiDeck]:
    try:
        response = requests.get(
            f"{MOCHI_BASE_URL}/decks", auth=(api_key, ""), timeout=10
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


def get_mochi_template(api_key: str) -> tuple[str, str, str]:
    template_id, front_id, back_id = "", "", ""
    try:
        response = requests.get(
            f"{MOCHI_BASE_URL}/templates",
            auth=(api_key, ""),
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


def create_card_on_mochi(
    mochi_config: MochiConfig, front: str, back: str
) -> bool:
    """
    Create a new card in the specified deck.

    :param mochi_config: The Mochi configuration containing API key and deck info.
    :param front: The content for the front of the card.
    :param back: The content for the back of the card.
    :return: True if the card was created successfully, False otherwise.
    """
    card_data = {
        "content": "",
        "deck-id": mochi_config.selected_deck_id,
        "template-id": mochi_config.template_id,
        "fields": {
            mochi_config.front_id: {
                "id": mochi_config.front_id,
                "value": front,
            },
            mochi_config.back_id: {"id": mochi_config.back_id, "value": back},
        },
        "review-reverse?": True,
    }

    try:
        response = requests.post(
            f"{MOCHI_BASE_URL}/cards",
            auth=(mochi_config.api_key, ""),
            json=card_data,
            timeout=10,
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to create Mochi card: {e}")
        return False
