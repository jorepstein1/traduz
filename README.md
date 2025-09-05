# Traduz - English to Spanish Translation Cards

A Python script that creates translation flashcards by translating English text to Spanish using an external translation API and storing the results in a YAML file and optionally to Mochi Cards.

## Features

- 🌍 Translates English text to Spanish using MyMemory Translation API (free)
- 📚 Stores translation pairs as flashcard entries in YAML format
- 🃏 Mochi Cards integration - sync cards to your Mochi decks
- 💾 Persistent storage - cards are saved locally and optionally to Mochi
- 🎯 Interactive command-line interface
- ⚡ Fast and lightweight
- 🔧 Configuration management for API keys and deck selection

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd traduz
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the script:

```bash
python main.py
```

The script provides an interactive menu with these options:

1. **Create new translation card**: Enter English text to translate to Spanish
2. **View all cards**: Display all saved translation cards
3. **Exit**: Quit the application

## Usage

Run the script:

```bash
python main.py
```

### First-time Setup

When you first run the script, it will ask if you want to connect to Mochi Cards:

1. **Mochi Integration Setup** (optional):

   - Choose 'y' if you want to sync cards to Mochi
   - Get your API key from https://app.mochi.cards (go to Settings)
   - Select a deck from your existing Mochi decks
   - Your settings will be saved in `config.yaml` for future use

2. **Local-only Mode**:
   - Choose 'n' to only save cards to the local YAML file

### Main Menu

The script provides an interactive menu with these options:

1. **Create new translation card**: Enter English text to translate to Spanish
2. **View all cards**: Display all saved translation cards
3. **Exit**: Quit the application

### Example Session

```
🌍 Traduz - English to Spanish Translation Cards
==================================================

🃏 Mochi Cards Integration
------------------------------
Would you like to connect to Mochi Cards? (y/n): y

🔑 To connect to Mochi, you need an API key.
   1. Go to https://app.mochi.cards
   2. Open Settings (click your profile/avatar)
   3. Generate an API key
   4. Copy and paste it below

Enter your Mochi API key: your_api_key_here

📚 Available Decks (3 found):
----------------------------------------
1. Spanish Vocabulary (45 cards)
2. Travel Phrases (23 cards)
3. Business Spanish (12 cards)

Select a deck (1-3): 1
✅ Selected deck: Spanish Vocabulary

Options:
1. Create new translation card
2. View all cards
3. Exit

Select an option (1-3): 1

📝 Enter English text to translate: Good morning
🔄 Translating: 'Good morning'
✅ Card saved successfully!
   Front (English): Good morning
   Back (Spanish): Buenos días
   🃏 Also added to Mochi deck!
```

## Output Format

## Configuration Files

### config.yaml

Stores your Mochi API key and selected deck:

```yaml
mochi:
  api_key: "your_mochi_api_key_here"
  selected_deck_id: "your_selected_deck_id_here"
```

### cards.yaml

Local storage of all translation cards:

```yaml
- back: Hola
  created_at: "2025-09-03T13:42:03.049570"
  front: Hello
  id: 1
  language_pair: en-es
- back: Buenos días
  created_at: "2025-09-03T13:45:12.123456"
  front: Good morning
  id: 2
  language_pair: en-es
```

## Mochi Cards Integration

This script integrates with [Mochi Cards](https://mochi.cards), a spaced repetition flashcard app. To use this feature:

1. **Create a Mochi account** at https://mochi.cards
2. **Create at least one deck** in the Mochi web app
3. **Get your API key** from https://app.mochi.cards (go to Settings)
4. **Run the script** and choose to connect to Mochi

### Features:

- 🔄 Automatic sync to your chosen Mochi deck
- 📱 Access cards on all devices through Mochi apps
- 🧠 Spaced repetition learning algorithm
- 📊 Progress tracking and statistics
- 🎨 Rich formatting and media support

## Output Format

Translation cards are saved in `cards.yaml` with the following structure:

```yaml
- back: Hola
  created_at: "2025-09-03T13:42:03.049570"
  front: Hello
  id: 1
  language_pair: en-es
```

Each card contains:

- `id`: Unique identifier
- `front`: English text (question side)
- `back`: Spanish translation (answer side)
- `created_at`: Timestamp when the card was created
- `language_pair`: Source and target languages (en-es)

## API Information

### MyMemory Translation API

This script uses the [MyMemory Translation API](https://mymemory.translated.net/), which provides:

- Free translation service
- No API key required
- Rate limits apply for heavy usage
- Supports many language pairs

### Mochi Cards API

Integration with [Mochi Cards API](https://app.mochi.cards/api) provides:

- Deck management
- Card creation and synchronization
- Cross-device access
- Spaced repetition features

## Requirements

- Python 3.7+
- Internet connection for translation API calls
- Dependencies listed in `requirements.txt`
- Optional: A Mochi Pro Subscription

## License

This project is open source and available under the [MIT License](LICENSE).
