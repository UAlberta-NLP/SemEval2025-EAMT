# GPT Translation Module

GPT-based translation and evaluation for the EA-MT pipeline. Translates English sentences to a target language using `gpt-4o-2024-08-06`, optionally augmented with Wikidata or BabelNet named entity translations, and evaluates using COMET and m-ETA.

## Setup

```bash
conda create -n ea-mt-eval python=3.10
conda activate ea-mt-eval
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your OpenAI API key:

```bash
cp .env.example .env
```

## Data Layout

```
data/
├── references/
│   └── validation/        # ground-truth .jsonl per language
├── predictions/
│   └── <model_name>/
│       └── validation/    # output .jsonl per language
├── wikidata/
│   └── validation/        # pre-fetched Wikidata NE translations (.tsv)
└── babelnet/
    └── validation/        # BabelNet NE translations (.tsv)
```

Each prediction `.jsonl` line: `{"id", "source_language", "target_language", "text", "wikidata_id", "prediction"}`

Each reference `.jsonl` line: `{"id", "source", "targets": [{"translation", "mention"}]}`

## Usage

Run all commands from inside `gpt/`.

**Translate and evaluate (validation split):**

```bash
python eval_harmonic.py "French"
```

Supported language names: `Arabic`, `Chinese (Traditional)`, `French`, `German`, `Italian`, `Japanese`, `Korean`, `Spanish`, `Thai`, `Turkish`

**Evaluate only:**

```bash
python eval_comet.py   # COMET score
python eval_meta.py    # m-ETA score
```

## Configuration

Edit the top of `eval_harmonic.py` to toggle knowledge sources and the dataset split:

| Flag | Default | Effect |
|------|---------|--------|
| `WIKI` | `False` | Use Wikidata NE translations |
| `BABELNET` | `False` | Use BabelNet NE translations |
| `TRACK` | `"validation"` | `"validation"` or `"test_without_targets"` |

## Prompt Variants (`prompts.py`)

| Name | Description |
|------|-------------|
| `One_Shot` | Few-shot example only, no external NE knowledge |
| `Soft_NETs_WD` | Soft NE hint from Wikidata (label + aliases) |
| `One_Shot_BN` | Hard NE constraint from BabelNet |
| `Missing_WD` | Fallback when Wikidata translation is absent |

## Files

| File | Description |
|------|-------------|
| `eval_harmonic.py` | Main entry point: translate + compute harmonic score |
| `eval_comet.py` | COMET evaluation using `Unbabel/wmt22-comet-da` |
| `eval_meta.py` | m-ETA (entity substring match accuracy) evaluation |
| `prompts.py` | All prompt variants |
| `examples.py` | One-shot translation examples per language |

## License

Creative Commons Attribution-ShareAlike 4.0 International — see [LICENSE.txt](LICENSE.txt).
