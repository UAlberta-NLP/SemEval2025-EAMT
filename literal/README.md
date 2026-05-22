# Literal Ensembling Module

Selects the best translation from multiple candidate systems using word alignment and named entity presence. The core metric is **Unaligned Source Words (USW)** — candidates with fewer unaligned content words (excluding NEs and function words) are preferred. If any candidate contains the correct NE translation, those candidates are prioritized first.

## Setup

```bash
conda create -n ea-mt-literal python=3.10
conda activate ea-mt-literal
pip install -r requirements.txt
```

> Must be run from inside the `literal/` directory — `config.py` reads `functional_word_list.txt` using a relative path.

## Usage

```bash
python literalensembling.py \
  --input-file <translations.tsv> \
  --input-cols System1 System2 System3 \
  --source-col Source \
  --output-file <output.tsv> \
  --language fr
```

To enable NE-aware selection, also pass:

```bash
  --ne-file <nes.tsv> \
  --ne-col-src EnglishNE \
  --ne-col-tgt FrenchNE
```

All three NE flags must be provided together.

## Supported Languages

`ar`, `de`, `es`, `fr`, `it`, `ja`, `ko`, `th`, `tr`, `zh`

## Files

| File | Description |
|------|-------------|
| `literalensembling.py` | Main script — `LiteralEnsembler` class and CLI |
| `config.py` | Tokenizers, punctuation set, function word list loader |
| `ne_identification.py` | Token-level NE span detection |
| `functional_word_list.txt` | List of function words used to discount alignment scoring |
