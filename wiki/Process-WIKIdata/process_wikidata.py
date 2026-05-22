import sys
import os
import json
import argparse
import csv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sparql_utils import fetch_label_and_aliases


def process_file(input_file, output_file):
    """Read a JSONL file of Wikidata entity records, fetch translations, and write JSONL or TSV."""
    output_format = "jsonl" if output_file.endswith(".jsonl") else "tsv" if output_file.endswith(".tsv") else None
    if not output_format:
        raise ValueError("Output file must have either .jsonl or .tsv extension.")

    output_data = []
    with open(input_file, "r", encoding="utf-8") as infile:
        for line in infile:
            data = json.loads(line.strip())
            wikidata_id = data.get("wikidata_id")
            target_locale = data.get("target_locale")

            if wikidata_id and target_locale:
                translations, _, entity_label = fetch_label_and_aliases(wikidata_id, target_locale)
                if translations and entity_label:
                    output_data.append({
                        "id": data.get("id", ""),
                        "wikidata_id": wikidata_id,
                        "entity_types": data.get("entity_types", []),
                        "source": data.get("source", ""),
                        "targets": translations,
                        "entity_label": entity_label,
                        "source_locale": data.get("source_locale", "en"),
                        "target_locale": target_locale,
                    })

    if output_format == "jsonl":
        with open(output_file, "w", encoding="utf-8") as outfile:
            for record in output_data:
                outfile.write(json.dumps(record, ensure_ascii=False) + "\n")
    elif output_format == "tsv":
        with open(output_file, "w", encoding="utf-8", newline="") as outfile:
            writer = csv.writer(outfile, delimiter="\t")
            writer.writerow(["id", "wikidata_id", "entity_types", "source", "targets", "entity_label", "source_locale", "target_locale"])
            for record in output_data:
                writer.writerow([
                    record["id"],
                    record["wikidata_id"],
                    ", ".join(record["entity_types"]),
                    record["source"],
                    ", ".join(record["targets"]),
                    record["entity_label"],
                    record["source_locale"],
                    record["target_locale"],
                ])

    print(f"Output saved to {output_file} in {output_format.upper()} format.")


def main():
    parser = argparse.ArgumentParser(
        description="Fetch Wikidata translations for entities in a JSONL file and save as JSONL or TSV."
    )
    parser.add_argument("input_file", type=str, help="Path to the input JSONL file")
    parser.add_argument("output_file", type=str, help="Path to the output file (.jsonl or .tsv)")
    args = parser.parse_args()

    process_file(args.input_file, args.output_file)


if __name__ == "__main__":
    main()
