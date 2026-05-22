# NER Translation Pipeline

Identifies named entities in raw sentences using n-gram Wikidata lookup and a BERT-based NER model, then fetches their translations in a target language.

## How It Works

1. **N-gram generation** — sentence tokens are combined into n-grams from longest to shortest, prioritizing multi-word entities.
2. **Capitalization heuristics** — first pass queries only n-grams that start and end with a capitalized word.
3. **Wikidata lookup** — each candidate n-gram is searched against the Wikidata SPARQL endpoint.
4. **NER validation** — for single-token candidates, `dslim/bert-large-NER` is used to filter out common non-entity words (e.g. "How", "When").
5. **Translation fetch** — once an entity ID is found, its label in the target language is retrieved from Wikidata.

## Usage

```bash
python NER_translation.py input_sentences.csv fr output_sentences.csv
```

- `input_sentences.csv` — CSV with a column named `sentences`
- `fr` — target language code (e.g. `fr`, `de`, `ja`)
- `output_sentences.csv` — output path

## Output columns

| Column | Description |
|--------|-------------|
| `sentence` | Original input sentence |
| `entity_label` | English label of the identified entity |
| `entity_id` | Wikidata Q-ID |
| `translation` | Entity label in the target language |

## Example

Input:

| sentences |
|-----------|
| What is the scope of the Statistical Classification of Economic Activities in the European Community? |
| What type of artwork is So Long, and Thanks for All the Fish?? |

Command:

```bash
python NER_translation.py input_sentences.csv fr output_sentences.csv
```

Output:

| sentence | entity_label | entity_id | translation |
|----------|-------------|-----------|-------------|
| What is the scope of... | Statistical Classification of Economic Activities in the European Community | Q100231013 | Nomenclature statistique des activités économiques dans la Communauté européenne |
| What type of artwork is So Long... | So Long, and Thanks for All the Fish | Q1042294 | Salut, et encore merci pour le poisson |

## Dependencies

Requires `sparql_utils.py` from the parent `wiki/` directory (added to `sys.path` automatically). NER model (`dslim/bert-large-NER`) is downloaded from HuggingFace on first run.
