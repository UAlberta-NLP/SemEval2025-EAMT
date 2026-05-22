# Wikidata Translation Evaluator

Measures how well Wikidata labels and aliases cover the ground-truth NE mentions in the EA-MT reference data. Compares Wikidata translations against an Excel file of BabelNet reference translations.

## Usage

```bash
python wiki_translation_evaluator.py <jsonl_folder> <excel_file> <output.json>
```

- `jsonl_folder` — directory of reference `.jsonl` files (one per language, named by locale code)
- `excel_file` — Excel workbook with one sheet per language containing Wikidata `Label` and `Also known as` columns
- `output.json` — results file with per-language match percentages

## Output format

```json
{
  "fr_FR": {
    "label_match_percentage": 72.4,
    "aka_match_percentage": 18.1
  },
  ...
}
```
