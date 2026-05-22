# Wikidata Translation Processor

Processes a JSONL file containing Wikidata IDs and fetches translations for each entity in its target language. Supports JSONL or TSV output based on the file extension.

## Usage

```bash
python process_wikidata.py input.jsonl output.jsonl
# or
python process_wikidata.py input.jsonl output.tsv
```

## Input format (JSONL)

Each line must be a JSON object with:

```json
{
    "id": "bc577b19fe3bd34e",
    "wikidata_id": "Q100097551",
    "entity_types": ["Movie"],
    "source": "Who played the lead role in The Mole – Undercover in North Korea?",
    "source_locale": "en",
    "target_locale": "de"
}
```

## Output fields

`id`, `wikidata_id`, `entity_types`, `source`, `targets`, `entity_label`, `source_locale`, `target_locale`

## Dependencies

Requires `sparql_utils.py` from the parent `wiki/` directory (added to `sys.path` automatically).
