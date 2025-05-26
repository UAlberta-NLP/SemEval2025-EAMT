import pandas as pd
import requests
import time
import argparse

# SPARQL endpoint URL for Wikidata
SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

def fetch_translations_and_label(entity_id, target_language):
    print(f"Fetching translations for Entity ID: {entity_id} in Language: {target_language}")
    query = f"""
    SELECT ?label ?alias ?entityLabel WHERE {{
      wd:{entity_id} rdfs:label ?label .
      OPTIONAL {{ wd:{entity_id} skos:altLabel ?alias FILTER(lang(?alias) = "{target_language}") }}
      OPTIONAL {{ wd:{entity_id} rdfs:label ?entityLabel FILTER(lang(?entityLabel) = "en") }}
      FILTER (lang(?label) = "{target_language}")
    }}
    """
    response = requests.get(SPARQL_ENDPOINT, params={"query": query, "format": "json"})
    time.sleep(1)  # Avoid hitting the rate limit

    if response.status_code == 200:
        results = response.json().get("results", {}).get("bindings", [])
        label = list({result["label"]["value"] for result in results if "label" in result})
        also_known_as = list({result["alias"]["value"] for result in results if "alias" in result})
        named_entity = next((result["entityLabel"]["value"] for result in results if "entityLabel" in result), None)
        print(f"Labels: {label}, Also known as: {also_known_as}, Named Entity: {named_entity} for {entity_id} in {target_language}")
        return label, also_known_as, named_entity
    else:
        print(f"Failed to fetch data for Entity ID: {entity_id} with status code {response.status_code}")

    return None, None, None

def process_tsv_with_translations(input_file, output_file):
    df = pd.read_csv(input_file, sep="\t")

    # Columns in the input file
    if not all(col in df.columns for col in ["wikidata_id", "entity_types", "source", "targets", "source_locale", "target_locale"]):
        raise ValueError("Input file must contain the columns: wikidata_id, entity_types, source, targets, source_locale, target_locale")

    # Prepare output DataFrame
    output_columns = ["wikidata_id", "entity_types", "source", "source_locale", "target_locale", "Named_Entity", "Label", "Also known as"]
    output_df = pd.DataFrame(columns=output_columns)

    for index, row in df.iterrows():
        entity_id = row["wikidata_id"]
        named_entity = row["targets"]
        target_language = row["target_locale"]

        # Fetch translations, aliases, and entity label
        label, also_known_as, named_entity_in_english = fetch_translations_and_label(entity_id, target_language)

        # Prepare data for the output row
        output_row = {
            "wikidata_id": entity_id,
            "entity_types": row["entity_types"],
            "source": row["source"],
            "source_locale": row["source_locale"],
            "target_locale": target_language,
            "Named_Entity": named_entity_in_english if named_entity_in_english else named_entity,
            "Label": "; ".join(label) if label else "",
            "Also known as": "; ".join(also_known_as) if also_known_as else ""
        }

        output_df = pd.concat([output_df, pd.DataFrame([output_row])], ignore_index=True)

    # Save the output to a TSV file
    output_df.to_csv(output_file, sep="\t", index=False, encoding="utf-8-sig")
    print(f"Translations saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process Wikidata translations from a TSV file.")
    parser.add_argument("input_file", type=str, help="Path to the input TSV file.")
    parser.add_argument("output_file", type=str, help="Path to the output TSV file.")

    args = parser.parse_args()

    process_tsv_with_translations(args.input_file, args.output_file)
