# This file takes a jsonl file and can output jsonl or tsv ...
# based on the given ouput file path
# This file takes a JSONL file and can output JSONL or TSV based on the given output file path
import json
import requests
import time
import argparse
import csv

# SPARQL endpoint URL for Wikidata
SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

# Function to fetch translations and the label for a given Wikidata ID and target language
def fetch_translations_and_label(entity_id, target_language):
    print(f"Fetching translations for Entity ID: {entity_id} in Language: {target_language}")
    query = f"""
    SELECT ?label ?entityLabel WHERE {{
      wd:{entity_id} rdfs:label ?label .
      wd:{entity_id} rdfs:label ?entityLabel .
      FILTER (lang(?label) = "{target_language}" && lang(?entityLabel) = "en")
    }}
    """
    response = requests.get(SPARQL_ENDPOINT, params={"query": query, "format": "json"})
    time.sleep(1)  # Avoid hitting the rate limit

    if response.status_code == 200:
        results = response.json().get("results", {}).get("bindings", [])
        translations = [result["label"]["value"] for result in results if "label" in result]
        entity_label = results[0]["entityLabel"]["value"] if results and "entityLabel" in results[0] else None
        print(f"Results for {entity_id} in {target_language}: {results}")
        return translations, entity_label
    else:
        print(f"Failed to fetch data for Entity ID: {entity_id} with status code {response.status_code}")
    return None, None

# Function to process the file
def process_file(input_file, output_file):
    output_format = "jsonl" if output_file.endswith(".jsonl") else "tsv" if output_file.endswith(".tsv") else None

    if not output_format:
        raise ValueError("Output file must have either .jsonl or .tsv extension.")

    output_data = []
    with open(input_file, 'r', encoding='utf-8') as infile:
        for line in infile:
            data = json.loads(line.strip())
            wikidata_id = data.get("wikidata_id")
            target_locale = data.get("target_locale")

            if wikidata_id and target_locale:
                translations, entity_label = fetch_translations_and_label(wikidata_id, target_locale)
                if translations and entity_label:
                    formatted_output = {
                        "id": data.get("id", ""),
                        "wikidata_id": wikidata_id,
                        "entity_types": data.get("entity_types", []),
                        "source": data.get("source", ""),
                        "targets": translations,
                        "entity_label": entity_label,
                        "source_locale": data.get("source_locale", "en"),
                        "target_locale": target_locale
                    }
                    output_data.append(formatted_output)

    if output_format == "jsonl":
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for record in output_data:
                outfile.write(json.dumps(record, ensure_ascii=False) + '\n')
        print(f"Output saved to {output_file} in JSONL format.")
    elif output_format == "tsv":
        with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            tsv_writer = csv.writer(outfile, delimiter='\t')
            # Write header
            tsv_writer.writerow(["id", "wikidata_id", "entity_types", "source", "targets", "entity_label", "source_locale", "target_locale"])
            for record in output_data:
                tsv_writer.writerow([
                    record["id"],
                    record["wikidata_id"],
                    ", ".join(record["entity_types"]),
                    record["source"],
                    ", ".join(record["targets"]),
                    record["entity_label"],
                    record["source_locale"],
                    record["target_locale"]
                ])
        print(f"Output saved to {output_file} in TSV format.")

# Main function to handle argparse and call processing functions
def main():
    parser = argparse.ArgumentParser(description="Process Wikidata translations and save the output in JSONL or TSV format.")
    parser.add_argument("input_file", type=str, help="Path to the input JSONL file")
    parser.add_argument("output_file", type=str, help="Path to the output file (must have .jsonl or .tsv extension)")

    args = parser.parse_args()

    process_file(args.input_file, args.output_file)

if __name__ == "__main__":
    main()





# README
"""
# Wikidata Translation Processor

This script processes a JSONL file containing Wikidata IDs and generates translations for the specified target language. 
It supports output in either JSONL or TSV format, depending on the specified output file extension.

## Features

- Fetches translations for Wikidata entities using the SPARQL endpoint.
- Outputs data in JSONL or TSV format based on the output file extension.

## Requirements

- Python 3.7 or higher
- Required Python libraries: `requests`, `argparse`

Install dependencies using:
```bash
pip install requests
```

## Usage

1. Prepare an input file in JSONL format. Each line should be a JSON object with the following structure:
   ```json
   {
       "id": "unique_id",
       "wikidata_id": "Q100097551",
       "entity_types": ["Movie"],
       "source": "Who played the lead role in The Mole – Undercover in North Korea?",
       "source_locale": "en",
       "target_locale": "de"
   }
   ```

2. Run the script from the command line:
   ```bash
   python process_wikidata.py input.jsonl output.jsonl
   ```
   or
   ```bash
   python process_wikidata.py input.jsonl output.tsv
   ```

### Input File

- **Format:** JSONL
- **Fields:**
  - `id` (string): Unique identifier for the record.
  - `wikidata_id` (string): The Wikidata ID to fetch translations for.
  - `entity_types` (list): A list of entity types (e.g., "Movie").
  - `source` (string): The source question or context.
  - `source_locale` (string): Source language locale (e.g., "en").
  - `target_locale` (string): Target language locale (e.g., "de").

### Output Files

- **JSONL Format:** Each line is a JSON object with the following fields:
  - `id`, `wikidata_id`, `entity_types`, `source`, `targets`, `source_locale`, `target_locale`
- **TSV Format:** A tab-separated file with the following columns:
  - `id`, `wikidata_id`, `entity_types`, `source`, `targets`, `source_locale`, `target_locale`

## Example

### Input File (`input.jsonl`):
```json
{"id": "bc577b19fe3bd34e", "wikidata_id": "Q100097551", "entity_types": ["Movie"], "source": "Who played the lead role in The Mole – Undercover in North Korea?", "source_locale": "en", "target_locale": "de"}
```

### Command:
```bash
python process_wikidata.py input.jsonl output.tsv
```

### Output File (`output.tsv`):
```
id	wikidata_id	entity_types	source	targets	source_locale	target_locale
bc577b19fe3bd34e	Q100097551	Movie	Who played the lead role in The Mole – Undercover in North Korea?	Der Maulwurf: Undercover in Nordkorea	en	de
```

## Notes

- Ensure the output file has a `.jsonl` or `.tsv` extension to specify the desired format.
- The script uses a 1-second delay per SPARQL request to avoid hitting rate limits.
"""