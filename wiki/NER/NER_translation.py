import argparse
import pandas as pd
import requests
import re
import time
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline

# SPARQL endpoint URL for Wikidata
SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

def is_ner(token):
    tokenizer = AutoTokenizer.from_pretrained("dslim/bert-large-NER")
    model = AutoModelForTokenClassification.from_pretrained("dslim/bert-large-NER")
    
    nlp = pipeline("ner", model=model, tokenizer=tokenizer)
    # example = "My name is Wolfgang and I live in Berlin"
    
    ner_results = nlp(token)
    return ner_results

def split_sentence(sentence):
    # Split using spaces and punctuation as delimiters
    # tokens = re.findall(r'\b\w+\b', sentence)
    sentence = re.sub(r'[?!.]+$', '', sentence)
    tokens = sentence.split()
    return tokens

def fetch_translation(entity_id, target_language):
    time.sleep(1)  # Wait 1 second to avoid hitting the rate limit
    query = f"""
    SELECT ?label WHERE {{
      wd:{entity_id} rdfs:label ?label .
      FILTER (lang(?label) = "{target_language}")
    }}
    """
    response = requests.get(SPARQL_ENDPOINT, params={"query": query, "format": "json"})
    if response.status_code == 200:
        results = response.json().get("results", {}).get("bindings", [])
        if results:
            return results[0]["label"]["value"]  # Return the first label for the target language
    return None  # Return None if no translations are found

def query_wikidata_for_entity(entity_name):
    entity_name = entity_name.strip()
    sparql_query = f"""
    SELECT ?item ?itemLabel WHERE {{
      ?item rdfs:label "{entity_name}"@en.
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}
    LIMIT 1
    """
    response = requests.get(SPARQL_ENDPOINT, params={'query': sparql_query, 'format': 'json'})
    if response.status_code == 200:
        result = response.json()
        try:
            item_uri = result['results']['bindings'][0]['item']['value']
            item_label = result['results']['bindings'][0]['itemLabel']['value']
            entity_id = re.search(r'Q\d+', item_uri).group(0)
            return item_label, entity_id
        except (KeyError, IndexError):
            return None
    else:
        return None

def identify_longest_entity_and_query_wikidata(sentence, delay=1):
    tokens = split_sentence(sentence)
    ngrams = []

    for n in range(len(tokens), 0, -1):
        for i in range(len(tokens) - n + 1):
            ngram = " ".join(tokens[i:i + n])
            ngrams.append(ngram)

    print(ngrams)

    highest_score = 0
    for ngram in ngrams:
        words = ngram.split()
        if words[0].istitle() and words[-1].istitle():
            if len(words) == 1:
                result = is_ner(words[0])
                if len(result) == 0: 
                    continue
                elif len(result) != 0 and result[0]['score'] < highest_score:
                    continue
                else:
                    highest_score = result[0]['score']
            entity_data = query_wikidata_for_entity(ngram)

            if entity_data:
                entity_label, entity_id = entity_data
                return entity_label, entity_id

            time.sleep(delay)

    for ngram in ngrams:
        words = ngram.split()
        if len(words) == 1:
            result = is_ner(words[0])
            if len(result) == 0: 
                continue
            elif len(result) != 0 and result[0]['score'] < highest_score:
                continue
            else:
                highest_score = result[0]['score']
        entity_data = query_wikidata_for_entity(ngram)

        if entity_data:
            entity_label, entity_id = entity_data
            return entity_label, entity_id

        time.sleep(delay)

    return None

def main():
    parser = argparse.ArgumentParser(description="Fetch Wikidata entities and translations for sentences.")
    parser.add_argument("input_csv", type=str, help="Path to the input CSV file with sentences.")
    parser.add_argument("language", type=str, help="Target language for translations (e.g., 'fr').")
    parser.add_argument("output_csv", type=str, help="Path to the output CSV file.")

    args = parser.parse_args()

    input_csv = args.input_csv
    target_language = args.language
    output_csv = args.output_csv

    # Read the input CSV file with encoding handling
    try:
        df = pd.read_csv(input_csv, encoding="utf-8")
    except Exception as e:
        print(f"Error reading the input CSV file: {e}")
        return

    if "sentences" not in df.columns:
        raise ValueError("Input CSV must have a column named 'sentences'.")

    # Prepare the output DataFrame
    output_data = []

    for sentence in df["sentences"]:
        entity_data = identify_longest_entity_and_query_wikidata(sentence)
        print(entity_data)
        if entity_data:
            entity_label, entity_id = entity_data
            translation = fetch_translation(entity_id, target_language)
            output_data.append({
                "sentence": sentence,
                "entity_label": entity_label,
                "entity_id": entity_id,
                "translation": translation
            })
        else:
            output_data.append({
                "sentence": sentence,
                "entity_label": "",
                "entity_id": "",
                "translation": ""
            })

    # Save to output CSV
    output_df = pd.DataFrame(output_data)   
    output_df.to_csv(output_csv, index=False)

if __name__ == '__main__':
    main()