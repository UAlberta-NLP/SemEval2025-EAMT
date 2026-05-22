# UAlberta at SemEval-2025 Task 2: Entity-Aware Machine Translation

> **Prompting and Ensembling for Entity-Aware Translation**  
> *Proceedings of SemEval-2025, Vienna, Austria. Association for Computational Linguistics.*

🏆 **1st Place — COMET Track**

[![Paper](https://img.shields.io/badge/Paper-ACL%20Anthology-red)](https://aclanthology.org/2025.semeval-1.224/)
[![Task](https://img.shields.io/badge/Task-EA--MT-blue)](https://sapienzanlp.github.io/ea-mt/)
[![Leaderboard](https://img.shields.io/badge/Leaderboard-HuggingFace-yellow)](https://huggingface.co/spaces/sapienzanlp/ea-mt-leaderboard)

---

## Overview

We present the UAlberta system for [SemEval-2025 Task 2](https://sapienzanlp.github.io/ea-mt/) on Entity-Aware Machine Translation (EA-MT). The task requires translating English sentences into 10 target languages while correctly translating named entities (NEs).

Our approach combines:
- **Prompt engineering** with GPT-4o, including retrieval-augmented generation using Wikidata and BabelNet NE translations
- **Literal ensembling** to select the best translation across multiple systems using word alignment and NE presence

**Target languages:** Arabic, Chinese (Traditional), French, German, Italian, Japanese, Korean, Spanish, Thai, Turkish

---

## Repository Structure

| Directory | Description |
|-----------|-------------|
| [`gpt/`](gpt/) | GPT-based translation and evaluation — main pipeline |
| [`wiki/`](wiki/) | Wikidata NE retrieval and translation |
| [`literal/`](literal/) | Literal ensembling across multiple translation systems |
| [`trans/`](trans/) | Alternative translation backends (Google Translate) |
| [`assets/`](assets/) | Paper, poster, figures, and official competition submissions |

---

## Quick Start

**GPT translation module** (requires `OPENAI_API_KEY`):

```bash
conda create -n ea-mt-eval python=3.10 && conda activate ea-mt-eval
pip install -r gpt/requirements.txt
cp gpt/.env.example gpt/.env  # add your OpenAI key
cd gpt && python eval_harmonic.py "French"
```

**Literal ensembling module:**

```bash
conda create -n ea-mt-literal python=3.10 && conda activate ea-mt-literal
pip install -r literal/requirements.txt
cd literal && python literalensembling.py --input-file <translations.tsv> \
  --input-cols System1 System2 --source-col Source \
  --output-file output.tsv --language fr
```

See each module's README for full usage details.

---

## Author

Ning Shi — mrshininnnnn@gmail.com

---

## Citation

```bibtex
@inproceedings{shi-etal-2025-ualberta,
    title = "{UA}lberta at {S}em{E}val-2025 Task 2: Prompting and Ensembling for Entity-Aware Translation",
    author = "Shi, Ning  and
      Basil, David  and
      Hauer, Bradley  and
      Nawal, Noshin  and
      Riley, Jai  and
      Teodorescu, Daniela  and
      Zhang, John  and
      Kondrak, Grzegorz",
    editor = "Rosenthal, Sara  and
      Ros{\'a}, Aiala  and
      Ghosh, Debanjan  and
      Zampieri, Marcos",
    booktitle = "Proceedings of the 19th International Workshop on Semantic Evaluation (SemEval-2025)",
    month = jul,
    year = "2025",
    address = "Vienna, Austria",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2025.semeval-1.224/",
    pages = "1709--1717",
    ISBN = "979-8-89176-273-2",
    abstract = "We describe the methods used by our UAlberta team for the SemEval-2025 Task 2 on Entity-Aware Machine Translation (EA-MT). Our methods leverage large language models with prompt engineering strategies suited to this task, including retrieval augmented generation and in-context learning. Our best results overall are obtained with ensembles of multiple models, leveraging named entity knowledge in the dataset. Finally, we provide proof-of-concept experiments showing that lexico-semantic knowledge can be used to identify high-quality translations. We further demonstrate that our methods can function even without gold named entity translations, by using an alternative knowledge base such as BabelNet."
}
```
