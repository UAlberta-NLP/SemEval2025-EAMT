
# Named Entity Recognition (Phase-I) and Translation Pipeline (Phase-II)

This project provides a pipeline for identifying named entities in sentences, querying Wikidata for their corresponding entity information, and retrieving translations in a target language. The tool is implemented in Python and leverages the `transformers` library for Named Entity Recognition (NER) and the Wikidata SPARQL endpoint for querying entity information.

---

## Features

1. **Named Entity Recognition (NER):**
   - Developed a pipeline to identify named entities from Wikidata. Initially, an n-gram generation approach is used, where sentences are split into tokens, and n-grams are generated starting with the longest possible sequences to prioritize identifying complete entities.
   - Each n-gram is checked against capitalization heuristics (ensuring the sequence starts and ends with capitalized words). Queries are then sent to the Wikidata SPARQL endpoint to search for matching entities. If a match is found, the entity label and ID are retrieved.
   - For identified entities, the script queries Wikidata to fetch the entity's label(Named Entities) in the specified target language.
   - If no entities are found using n-grams with capitalization heuristics, the search is expanded to handle cases where named entities may have been missed due to punctuation issues. For example, for a named entity like “Symphony No.9”, it will ignore the punctuation and correctly identify the entity.
   - Additionally, a pre-trained NER model is used to validate whether individual tokens are likely to be named entities.
3. **Wikidata Integration:** Queries the Wikidata SPARQL endpoint to retrieve entity information and translations.
4. **Multi-Language Support:** Supports translations in various languages by specifying a target language code.
5. **Flexible Input/Output:** Reads input sentences from a CSV file and saves the results to an output CSV file.

---

## How It Works

### N-gram Generation
- The code generates n-grams from high to low order. For instance, a 5-word sentence will result in one 5-gram, two 4-grams, three 3-grams, and so on, down to five 1-grams.

### Entity Search
- Each n-gram is queried on Wikidata for available entities. The process halts as soon as a valid entity is found. This ensures the identification of the longest possible named entities.

### Capitalization Heuristics
- The initial search focuses on entities starting and ending with words that begin with capital letters.
- If no match is found, the program broadens the search to include entities with lowercase words.

### Double-Checking with NER Models
- For 1-grams, Wikidata often misidentifies non-entities like "How" or "When" as named entities. To address this, we verify results using a fine-tuned NER model (`DistilBERT-NER`) to ensure accuracy.

---

## Usage

1. Prepare a CSV file with a column named `sentences` containing the sentences you want to process.

2. Run the script:
   ```bash
   python main.py input.csv target_language output.csv
   ```
   - `input.csv`: Path to the input CSV file.
   - `target_language`: Target language code for translations (e.g., `fr` for French).
   - `output.csv`: Path to save the output CSV file.

---

## Output Format

The output CSV file will contain the following columns:
- `sentence`: The original sentence.
- `entity_label`: The label of the identified entity.
- `entity_id`: The Wikidata ID of the entity.
- `translation`: The translation of the entity label in the target language.

---

## Example

### Input CSV (`input.csv`):
| sentences             |
|-----------------------|
| What is the scope of the Statistical Classification of Economic Activities in the European Community? |
| What type of artwork is So Long, and Thanks for All the Fish??|

### Command:
```bash
python3 NER_translation.py input_sentences.csv 'fr' output_sentences.csv
```

### Output CSV (`output.csv`):
| sentence                             | entity_label | entity_id | translation        |
|-------------------------------------|--------------|-----------|--------------------|
| What is the scope of the Statistical Classification of Economic Activities in the European Community?   | Statistical Classification of Economic Activities in the European Community | Q100231013      | Nomenclature statistique des activités économiques dans la Communauté européenne |
| What type of artwork is So Long, and Thanks for All the Fish?? | So Long, and Thanks for All the Fish      | Q1042294   | Salut, et encore merci pour le poisson  |

---

## Requirements

- Python 3.7+
- Libraries:
  - `pandas`
  - `transformers`
  - `requests`

Install these dependencies via:
```bash
pip install pandas transformers requests
```

---

## Notes

- The script includes a rate-limiting mechanism (1-second delay) to avoid hitting the Wikidata SPARQL endpoint's query limit.
- Ensure a stable internet connection for querying the Wikidata endpoint.
