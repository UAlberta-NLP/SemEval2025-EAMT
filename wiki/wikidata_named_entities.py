import pandas as pd
import argparse

from sparql_utils import search_entity, fetch_label

TARGET_LANGUAGES = ["it", "es", "fr", "de", "ar", "ja", "zh", "ko", "th", "tr", "en"]


def get_word_translations_via_sparql(word, search_language="en"):
    """Return a dict of {language_code: translation} for a given word, or None."""
    entity_id = search_entity(word, language=search_language)
    if not entity_id:
        return None

    translations = {}
    for lang in TARGET_LANGUAGES:
        labels = fetch_label(entity_id, lang)
        if labels:
            translations[lang] = labels[0]
    translations["entity_id"] = entity_id
    return translations if translations else None


def generate_token_list(csv_file, sequence_number):
    df = pd.read_csv(csv_file)
    sequence_tokens = df[df["Sentence Number"] == sequence_number]["Text"].tolist()

    token_list = []
    for length in range(len(sequence_tokens), 0, -1):
        for start_idx in range(len(sequence_tokens) - length + 1):
            token_list.append(" ".join(sequence_tokens[start_idx:start_idx + length]))
    return token_list


def process_csv_with_translations(input_file, output_file):
    df = pd.read_csv(input_file)
    highest_value = df["Sentence Number"].max()

    languages = ["en", "it", "es", "fr", "de", "ar", "ja", "zh", "ko", "th", "tr", "entity_id"]
    translations_df = pd.DataFrame(columns=["Token"] + languages)

    all_tokens = []
    for i in range(highest_value + 1):
        all_tokens.extend(generate_token_list(input_file, i))

    seen = set()
    rows = []
    for token in all_tokens:
        if token in seen:
            continue
        seen.add(token)

        result = get_word_translations_via_sparql(token, search_language="en")
        if result is None:
            continue

        row = {"Token": token}
        row.update(result)
        rows.append(row)

    if rows:
        translations_df = pd.DataFrame(rows, columns=["Token"] + languages)

    translations_df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"Translations saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch translated named entities from Wikidata.")
    parser.add_argument("input_file", help="Path to the input CSV file")
    parser.add_argument("output_file", help="Path to the output CSV file")
    args = parser.parse_args()

    process_csv_with_translations(args.input_file, args.output_file)
