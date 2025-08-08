# SemEval2025-EAMT
This repository is for the paper UAlberta at SemEval-2025 Task 2: Prompting and Ensembling for Entity-Aware Translation. In *Proceedings of the 19th International Workshop on Semantic Evaluation (SemEval-2025)*, pages 1709–1717, Vienna, Austria. Association for Computational Linguistics.

🏆 **1st Place — COMET Track**  

🔗 [Task](https://sapienzanlp.github.io/ea-mt/) | 📊 [Leaderboard](https://huggingface.co/spaces/sapienzanlp/ea-mt-leaderboard)
📄 [Paper](https://aclanthology.org/2025.semeval-1.224/) | 🖼️ [Poster](assets/poster.pdf) | 📑 [Slides]()

---

## 📁 Directory Overview

- `gpt/` – GPT-based Translation Module  
- `trans/` – Other Translation Modules (e.g., Google Cloud)
- `wiki/` – Wiki Retrieval Module  
- `wsd/` – Word Sense Disambiguation Module

(Official submissions can be found in [`assets/submissions/`](assets/submissions/))

---

## 👥 Author

- **Ning Shi** — <mrshininnnnn@gmail.com>

---

## 📚 BibTeX

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