# Fetch Translation Label & Alias

Batch-processes a TSV of Wikidata entity records and fetches, for each entity, its label, alternative names (aliases), and English name in the target language.

## Usage

```bash
python wikidata_nes_label_alias.py input.tsv output.tsv
```

## Input columns

`wikidata_id`, `entity_types`, `source`, `targets`, `source_locale`, `target_locale`

## Output columns

| Column | Description |
|--------|-------------|
| `wikidata_id` | Wikidata Q-ID |
| `Named_Entity` | English entity name |
| `Label` | Target-language label (semicolon-separated if multiple) |
| `Also known as` | Target-language aliases (semicolon-separated) |

## Dependencies

Requires `sparql_utils.py` from the parent `wiki/` directory (added to `sys.path` automatically).
