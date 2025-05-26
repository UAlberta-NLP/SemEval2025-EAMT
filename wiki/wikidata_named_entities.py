import pandas as pd
import requests
import time
import argparse

# SPARQL endpoint URL for Wikidata
SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
en_id = " "

# Step 1: Search for the entity using SPARQL
def search_entity(token, language="en"):
    query = f"""
    SELECT ?entity WHERE {{
      ?entity rdfs:label "{token}"@{language} .
    }} LIMIT 1
    """
    response = requests.get(SPARQL_ENDPOINT, params={"query": query, "format": "json"})

    if response.status_code == 200:
        results = response.json().get("results", {}).get("bindings", [])
        if results:
            return results[0]["entity"]["value"].split("/")[-1]  # Extract the entity ID
    return None

# Step 2: Fetch translations for the entity and target language
def fetch_translations(entity_id, target_language):
    # SPARQL endpoint URL for Wikidata
    SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
    time.sleep(3)  # Wait 1 second to avoid hitting the rate limit
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
            result = []
            for r in results:
              result.append(r["label"]["value"])
            return result
            # return results[0]["label"]["value"]  # Return the first label for the target language
    return None  # Return None if no translations are found

# Combined Function: Get Translations for a Word
def get_word_translations_via_sparql(word, search_language="en"):
    # List of target languages
    languages = ["it", "es", "fr", "de", "ar", "ja", "zh", "ko", "th", "tr", "en"]
    # Find the entity ID
    entity_id = search_entity(word, language=search_language)

    global en_id
    en_id = entity_id

    if entity_id:
        translations = {}
        # Fetch translations for each target language
        for lang in languages:
            translation = fetch_translations(entity_id, lang)[0]
            if translation:  # Add only if a translation exists
                translations[lang] = translation
        return translations if translations else 0
    else:
        return 0

def generate_token_list(csv_file, sequence_number):
    # Read the CSV file
    df = pd.read_csv(csv_file)

    # Filter the dataframe for the given sequence number
    sequence_tokens = df[df["Sentence Number"] == sequence_number]["Text"].tolist()

    # Generate the token list
    token_list = []
    for length in range(len(sequence_tokens), 0, -1):
        for start_idx in range(len(sequence_tokens) - length + 1):
            token_list.append(" ".join(sequence_tokens[start_idx:start_idx + length]))

    return token_list

def process_csv_with_translations(input_file, output_file):
    # Load the input CSV
    df = pd.read_csv(input_file)
    highest_value = df["Sentence Number"].max()

    # List of target languages
    languages = ["en","it", "es", "fr", "de", "ar", "ja", "zh", "ko", "th", "tr","entity_id"]

    # Create a new DataFrame to store translations
    translations_df = pd.DataFrame(columns=["Token"] + languages)
    # print(translations_df)  # Empty DataFrame
                              # Columns: [Token, en, it, es, fr, de, ar, ja, zh, ko, th, tr, entity_id]
                              # Index: []

    global en_id
    translations_df["entity_id"] = en_id #Initialize the entity id after language columns

    result = [] # Process sequence 0
    num_sequences = highest_value +1

    for i in range(num_sequences):
      result.extend(generate_token_list(input_file, i))

    # for idx, tokens in enumerate(result, i):
    #     print(f"{idx}: {tokens}")

    # Iterate through each row and generate translations
    for index, token in enumerate(result, i):
      if token in result[:i]:
        continue
      print(f"{index} : {token}")
      translations = get_word_translations_via_sparql(token, search_language = "en")
      print(translations)
      if translations == 0:  # If translations are not found
        continue
      else:
        translations["entity_id"]= en_id

      # Check if translations is a valid dictionary
      if isinstance(translations, dict):  # Ensure it's a dictionary before processing
          for lang, translation in translations.items():
              translations_df.at[index, "Token"] = token
              translations_df.at[index, lang] = translation  # Update the DataFrame with translations

    # Save the updated DataFrame to a new CSV file
    translations_df.to_csv(output_file, index = False, encoding = "utf-8-sig")
    print(f"Translations saved to {output_file}")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Fetch translated named entities from wikidata.")
    parser.add_argument("input_file", help="Path to the input CSV file")
    parser.add_argument("output_file", help="Path to the output CSV file")

    args = parser.parse_args()

    # Call the processing function with the provided arguments
    process_csv_with_translations(args.input_file, args.output_file)