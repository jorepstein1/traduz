import requests
import yaml
import os
import sys
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Card:
    id: int
    front: str
    back: str
    created_at: str
    language_pair: str

class Translator:
    def __init__(self, yaml_file: str = "cards.yaml") -> None:
        self.yaml_file = yaml_file
        self.base_url = "https://api.mymemory.translated.net/get"
    
    def translate_text(self, text: str, source_lang: str = "en", target_lang: str = "es") -> Optional[str]:
        """
        Translate text using MyMemory Translation API (free service)
        """
        try:
            params = {
                'q': text,
                'langpair': f"{source_lang}|{target_lang}"
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('responseStatus') == 200:
                translated_text = data['responseData']['translatedText']
                return translated_text
            else:
                print(f"Translation error: {data.get('responseDetails', 'Unknown error')}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None
        except Exception as e:
            print(f"Translation failed: {e}")
            return None
    
    def load_existing_cards(self) -> List[Card]:
        """Load existing cards from YAML file"""
        if os.path.exists(self.yaml_file):
            try:
                with open(self.yaml_file, 'r', encoding='utf-8') as file:
                    data = yaml.safe_load(file) or []
                    return [Card(**card_data) for card_data in data]
            except Exception as e:
                print(f"Error loading existing cards: {e}")
                return []
        return []
    
    def save_card(self, english_text: str, spanish_text: str) -> bool:
        """Save a new translation card to the YAML file"""
        try:
            cards = self.load_existing_cards()
            
            new_card = Card(
                id=len(cards) + 1,
                front=english_text,
                back=spanish_text,
                created_at=datetime.now().isoformat(),
                language_pair='en-es'
            )
            
            cards.append(new_card)
            
            # Convert cards to dict format for YAML serialization
            cards_dict = [card.__dict__ for card in cards]
            
            with open(self.yaml_file, 'w', encoding='utf-8') as file:
                yaml.dump(cards_dict, file, default_flow_style=False, allow_unicode=True, indent=2)
            
            print(f"✅ Card saved successfully!")
            print(f"   Front (English): {english_text}")
            print(f"   Back (Spanish): {spanish_text}")
            return True
            
        except Exception as e:
            print(f"Error saving card: {e}")
            return False
    
    def create_translation_card(self, english_query: str) -> bool:
        """Main method to create a translation card"""
        print(f"🔄 Translating: '{english_query}'")
        
        spanish_translation = self.translate_text(english_query)
        
        if spanish_translation:
            success = self.save_card(english_query, spanish_translation)
            if success:
                return True
        else:
            print("❌ Translation failed. Card not created.")
            return False
    
    def display_all_cards(self) -> None:
        """Display all existing cards"""
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
    
    while True:
        print("\nOptions:")
        print("1. Create new translation card")
        print("2. View all cards")
        print("3. Exit")
        
        choice = input("\nSelect an option (1-3): ").strip()
        
        if choice == "1":
            english_query = input("\n📝 Enter English text to translate: ").strip()
            
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