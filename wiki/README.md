# Wiki Retrieval Module

Fetches named entity (NE) translations from the Wikidata SPARQL endpoint. Used to supply NE knowledge to the GPT translation module.

All SPARQL logic is centralized in [`sparql_utils.py`](sparql_utils.py).

## Sub-modules

| Path | Description |
|------|-------------|
| `wikidata_named_entities.py` | Given a CSV of tokenized sentences, fetches NE translations for all target languages |
| `fetch_translations_wiki_id.py` | Fetch translations for a single Wikidata ID from the command line |
| `fetch_translation_label_alias/` | Batch-process a TSV of entities; returns label, aliases, and English name |
| `Process-WIKIdata/` | Process a JSONL of entity records and output translations as JSONL or TSV |
| `NER/` | NER-based pipeline: identify entities in raw sentences, then fetch Wikidata translations |
| `performance_evaluation/` | Evaluate Wikidata translation coverage against BabelNet reference data |

## Setup

```bash
pip install -r requirements.txt
```

## Usage

**Fetch translations for entities in a CSV:**

```bash
python wikidata_named_entities.py input.csv output.csv
```

**Fetch translations for a single Wikidata ID:**

```bash
python fetch_translations_wiki_id.py Q100231013 fr
```

**Batch TSV processing (label + aliases):**

```bash
python fetch_translation_label_alias/wikidata_nes_label_alias.py input.tsv output.tsv
```

**Process JSONL entity records:**

```bash
python Process-WIKIdata/process_wikidata.py input.jsonl output.tsv
```

**NER pipeline (raw sentences → NE translations):**

```bash
python NER/NER_translation.py input_sentences.csv fr output_sentences.csv
```

## Notes

- All scripts use a 1-second delay between SPARQL requests to stay within rate limits.
- `sparql_utils.py` is added to `sys.path` automatically by each sub-module script.
