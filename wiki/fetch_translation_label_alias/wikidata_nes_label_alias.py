import sys
import os
import argparse

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sparql_utils import fetch_label_and_aliases


def process_tsv_with_translations(input_file, output_file):
    df = pd.read_csv(input_file, sep="\t")

    required = ["wikidata_id", "entity_types", "source", "targets", "source_locale", "target_locale"]
    if not all(col in df.columns for col in required):
        raise ValueError(f"Input file must contain the columns: {', '.join(required)}")

    output_rows = []
    for _, row in df.iterrows():
        entity_id = row["wikidata_id"]
        named_entity = row["targets"]
        target_language = row["target_locale"]

        label, also_known_as, named_entity_in_english = fetch_label_and_aliases(entity_id, target_language)

        output_rows.append({
            "wikidata_id": entity_id,
            "entity_types": row["entity_types"],
            "source": row["source"],
            "source_locale": row["source_locale"],
            "target_locale": target_language,
            "Named_Entity": named_entity_in_english if named_entity_in_english else named_entity,
            "Label": "; ".join(label) if label else "",
            "Also known as": "; ".join(also_known_as) if also_known_as else "",
        })

    output_df = pd.DataFrame(output_rows)
    output_df.to_csv(output_file, sep="\t", index=False, encoding="utf-8-sig")
    print(f"Translations saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process Wikidata translations from a TSV file.")
    parser.add_argument("input_file", type=str, help="Path to the input TSV file.")
    parser.add_argument("output_file", type=str, help="Path to the output TSV file.")
    args = parser.parse_args()

    process_tsv_with_translations(args.input_file, args.output_file)
