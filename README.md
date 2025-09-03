# Traduz - English to Spanish Translation Cards

A Python script that creates translation flashcards by translating English text to Spanish using an external translation API and storing the results in a YAML file.

## Features

- 🌍 Translates English text to Spanish using MyMemory Translation API (free)
- 📚 Stores translation pairs as flashcard entries in YAML format
- 💾 Persistent storage - cards are saved and can be viewed later
- 🎯 Interactive command-line interface
- ⚡ Fast and lightweight

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

### Example Session

```
🌍 Traduz - English to Spanish Translation Cards
==================================================

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
```

## Output Format

Translation cards are saved in `cards.yaml` with the following structure:

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

Each card contains:

- `id`: Unique identifier
- `front`: English text (question side)
- `back`: Spanish translation (answer side)
- `created_at`: Timestamp when the card was created
- `language_pair`: Source and target languages (en-es)

## API Information

This script uses the [MyMemory Translation API](https://mymemory.translated.net/), which provides:

- Free translation service
- No API key required
- Rate limits apply for heavy usage
- Supports many language pairs

## Requirements

- Python 3.7+
- Internet connection for translation API calls
- Dependencies listed in `requirements.txt`

## License

This project is open source and available under the [MIT License](LICENSE).
