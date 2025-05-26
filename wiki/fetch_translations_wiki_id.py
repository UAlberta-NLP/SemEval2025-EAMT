import argparse
from wikidata_named_entities import fetch_translations

def main():
    parser = argparse.ArgumentParser(description="Fetch all translations for wikidata IDs.")
    parser.add_argument("entity_id", type=str, help="WikiData IDs.")
    parser.add_argument("language", type=str, help="Target language for translations (e.g., 'fr').")
    
    args = parser.parse_args()

    entity_id = args.entity_id
    target_language = args.language

    result = fetch_translations(entity_id, target_language)
    print(result)
    return result

if __name__ == '__main__':
    main()

# HOW TO USE:
## python3 fetch_translations_wiki_id.py 'Q100231013' 'fr'