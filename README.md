# Tradu - English <-> Spanish Translation Cards

A Python script that creates translation flashcards by translating between English and Spanish using external translation APIs and storing the results locally and optionally to [Mochi Cards](https://mochi.cards/).

## Features

- 🌍 Translates between English and Spanish using multiple translation services:
  - [**MyMemory Translation API**](https://mymemory.translated.net/) (free, no account required)
  - [**DeepL API**](https://www.deepl.com/) (free, requires account, higher quality)
- 🔄 Bidirectional translation support (English ↔ Spanish)
- 📚 Stores translation pairs as flashcard entries in YAML format
- 🃏 [Mochi Cards](https://mochi.cards/) integration - sync cards to your Mochi decks
- 🎯 Interactive command-line interface
- ⚡ Fast and lightweight
- 🔧 Configuration management for API keys and deck selection

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd tradu
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

### First-time Setup

When you first run the script, it will guide you through optional integrations:

1. **[Mochi Cards](https://mochi.cards/) Integration** (optional):

   - Choose 'y' if you want to sync cards to Mochi
   - Get your API key from https://app.mochi.cards (go to Account Settings)
   - Select a deck from your existing Mochi decks for new cards to be added to
   - Your settings will be saved in `config.yaml` for future use

2. **[DeepL Translator](https://www.deepl.com/) Integration** (optional):

   - Choose 'y' for higher quality translations (requires API key)
   - Get your API key from https://www.deepl.com/pro-api
   - DeepL offers better translation quality than the free MyMemory service
   - Your API key will be saved in `config.yaml` for future use

### Translation Services

The script supports two translation services:

- **[MyMemory](https://mymemory.translated.net/)** (default, free):

  - No account required
  - Good for basic translations and testing the script
  - Rate limits may apply for heavy usage

- **[DeepL](https://www.deepl.com/)** (premium):
  - Requires account and API key
  - Superior translation quality
  - Better context understanding
  - More natural translations

### Main Menu

The script provides an interactive menu with these options:

1. **Create new translation card**: Choose translation direction and enter text to translate
   - English to Spanish
   - Spanish to English
2. **View all cards**: Display all saved translation cards
3. **Exit**: Quit the application

### Example Session

```
🌍 Tradu - English to Spanish Translation Cards
==================================================

🃏 Mochi Cards Integration
------------------------------
Would you like to connect to Mochi Cards? (y/n): y

🔑 To connect to Mochi, you need an API key.
   1. Go to https://app.mochi.cards/
   2. Open the Account Settings and create an API key
   3. Copy and paste it below

Enter your Mochi API key: your_api_key_here

📚 Available Decks (3 found):
----------------------------------------
1. Spanish Vocabulary
2. Travel Phrases
3. Business Spanish

Select a deck (1-3): 1
✅ Selected deck: Spanish Vocabulary

🌐 DeepL Translator Integration
------------------------------
Would you like to connect to DeepL for translations? (y/n): y

🔑 To connect to DeepL, you need an API key.
   1. Go to https://www.deepl.com/pro-api
   2. Sign up for an account and find your API key in the Account settings
   3. Copy and paste it below

Enter your DeepL API key: your_deepl_api_key_here
✅ Successfully connected to DeepL!

Options:
1. Create new translation card
2. View all cards
3. Exit

Select an option (1-3): 1

Language Options:
1. English to Spanish
2. Spanish to English

Select an option (1-2): 1

📝 Enter text (EN) to translate: Good morning
🔄 Translating: 'Good morning'
✅ Card saved successfully!
   Front (EN): Good morning
   Back (ES): Buenos días
   🃏 Also added to Mochi deck!
```

## Configuration Files

### config.yaml

Stores your API keys and preferences:

```yaml
mochi:
  api_key: "your_mochi_api_key_here"
  selected_deck_id: "your_selected_deck_id_here"
deepl:
  api_key: "your_deepl_api_key_here"
```

### cards.yaml

Local storage of all translation cards:

```yaml
- back: Hola
  created_at: "2025-09-03 13:42"
  front: Hello
  id: 1
  language_pair: en-es
- back: Buenos días
  created_at: "2025-09-03 13:45"
  front: Good morning
  id: 2
  language_pair: en-es
- back: Thank you
  created_at: "2025-09-03 14:20"
  front: Gracias
  id: 3
  language_pair: es-en
```

## Integrations

### [Mochi Cards](https://mochi.cards/) Integration

This script integrates with [Mochi Cards](https://mochi.cards), a spaced repetition flashcard app. To use this feature:

1. **Create a Mochi account** at https://mochi.cards
2. **Create at least one deck** in the Mochi web app
3. **Ensure a template exists** that contains both "Front" and "Back" fields
4. **Get your API key** from https://app.mochi.cards (go to Account Settings)
5. **Run the script** and choose to connect to Mochi

**Features:**

- 🔄 Automatic sync to your chosen Mochi deck
- 📱 Access cards on all devices through Mochi apps

### [DeepL Translator](https://www.deepl.com/) Integration

This script can optionally use [DeepL](https://www.deepl.com/), a premium translation service known for high-quality translations:

1. **Create a [DeepL](https://www.deepl.com/) account** at https://www.deepl.com/pro-api
2. **Get your API key** from your account settings
3. **Run the script** and choose to connect to DeepL

**Benefits of DeepL:**

- 🎯 Higher translation accuracy
- 🧠 Better context understanding
- 🗣️ More natural, fluent translations
- 📚 Superior handling of idioms and expressions

## Requirements

- Python 3.12+
- Internet connection for translation API calls
- Dependencies listed in `requirements.txt`
- Optional: [Mochi Cards](https://mochi.cards/) Pro account for card synchronization
- Optional: [DeepL](https://www.deepl.com/) account for premium translations

## License

This project is open source and available under the [MIT License](LICENSE).
