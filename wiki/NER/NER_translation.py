import sys
import os
import argparse
import re

import pandas as pd
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sparql_utils import search_entity_with_label, fetch_label

_NER_MODEL_NAME = "dslim/bert-large-NER"
_tokenizer = AutoTokenizer.from_pretrained(_NER_MODEL_NAME)
_model = AutoModelForTokenClassification.from_pretrained(_NER_MODEL_NAME)
_ner_pipeline = pipeline("ner", model=_model, tokenizer=_tokenizer)


def is_ner(token):
    return _ner_pipeline(token)


def _ner_passes(result, highest_score):
    """Return True if the NER result score exceeds the current highest."""
    return len(result) > 0 and result[0]["score"] >= highest_score


def split_sentence(sentence):
    sentence = re.sub(r"[?!.]+$", "", sentence)
    return sentence.split()


def identify_longest_entity_and_query_wikidata(sentence, delay=1):
    tokens = split_sentence(sentence)
    ngrams = []
    for n in range(len(tokens), 0, -1):
        for i in range(len(tokens) - n + 1):
            ngrams.append(" ".join(tokens[i:i + n]))

    highest_score = 0

    # First pass: capitalized n-grams only
    for ngram in ngrams:
        words = ngram.split()
        if not (words[0].istitle() and words[-1].istitle()):
            continue
        if len(words) == 1:
            result = is_ner(words[0])
            if not _ner_passes(result, highest_score):
                continue
            highest_score = result[0]["score"]

        entity_data = search_entity_with_label(ngram)
        if entity_data:
            return entity_data

    # Second pass: relaxed — any n-gram
    for ngram in ngrams:
        words = ngram.split()
        if len(words) == 1:
            result = is_ner(words[0])
            if not _ner_passes(result, highest_score):
                continue
            highest_score = result[0]["score"]

        entity_data = search_entity_with_label(ngram)
        if entity_data:
            return entity_data

    return None


def main():
    parser = argparse.ArgumentParser(description="Fetch Wikidata entities and translations for sentences.")
    parser.add_argument("input_csv", type=str, help="Path to the input CSV file with sentences.")
    parser.add_argument("language", type=str, help="Target language for translations (e.g., 'fr').")
    parser.add_argument("output_csv", type=str, help="Path to the output CSV file.")
    args = parser.parse_args()

    try:
        df = pd.read_csv(args.input_csv, encoding="utf-8")
    except Exception as e:
        print(f"Error reading the input CSV file: {e}")
        return

    if "sentences" not in df.columns:
        raise ValueError("Input CSV must have a column named 'sentences'.")

    output_data = []
    for sentence in df["sentences"]:
        entity_data = identify_longest_entity_and_query_wikidata(sentence)
        if entity_data:
            entity_label, entity_id = entity_data
            labels = fetch_label(entity_id, args.language)
            translation = labels[0] if labels else None
            output_data.append({
                "sentence": sentence,
                "entity_label": entity_label,
                "entity_id": entity_id,
                "translation": translation,
            })
        else:
            output_data.append({
                "sentence": sentence,
                "entity_label": "",
                "entity_id": "",
                "translation": "",
            })

    pd.DataFrame(output_data).to_csv(args.output_csv, index=False)


if __name__ == "__main__":
    main()
