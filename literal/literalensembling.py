import argparse
import sys
from config import SUPPORTED_LANGUAGES, FUNCTION_WORDS, is_punctuation, TOKENIZERS
import csv
from simalign import SentenceAligner
import pandas as pd
import random
from ne_identification import part_of_ne

GLOBAL_ALIGNER = SentenceAligner(model="xlmr", layer=8, token_type="bpe", matching_methods="mai")

class LiteralEnsembler:
    def __init__(self, csv_file_path, source_column, ne_file_path, src_ne_column, tar_ne_column, translation_cols, language, using_nes):
        self.language = language
        self.source_col = source_column
        self.using_nes = using_nes
        self.function_words = FUNCTION_WORDS
        self.aligner = GLOBAL_ALIGNER

        self.raw_sent = {col: {} for col in translation_cols + [source_column]}
        self.has_ne = {col: {} for col in translation_cols}
        self.translations = []
        self.entities_s = {}
        self.entities_t = {}

        self.import_translations(csv_file_path, translation_cols, source_column)

        if self.using_nes:
            self.import_named_entities(csv_file_path, source_column, ne_file_path, src_ne_column, tar_ne_column)

    def import_translations(self, filepath, translation_columns, source_column):
        with open(filepath, 'r', encoding='utf-8') as csvfile:
            csvreader = csv.DictReader(csvfile, delimiter="\t")
            for j, row in enumerate(csvreader):
                row_tokens = {}
                for key in translation_columns:
                    doc = TOKENIZERS[self.language](row[key])
                    row_tokens[key] = [t.text for t in doc if t.text.strip()]
                    self.raw_sent[key][j] = row[key]
                doc = TOKENIZERS['en'](row[source_column])
                row_tokens[source_column] = [t.text for t in doc if t.text.strip()]
                self.raw_sent[source_column][j] = row[source_column]
                self.translations.append(row_tokens)

    def import_named_entities(self, csv_file_path, src_sentence_column, ne_file_path, srclang_ne_column, tarlang_ne_column):
        df = pd.read_csv(ne_file_path, sep='\t')
        for _, row in df.iterrows():
            self.entities_s[row[src_sentence_column]] = row[srclang_ne_column]
            self.entities_t[row[src_sentence_column]] = row[tarlang_ne_column]

    def get_english_entity(self, index):
        return self.entities_s.get(self.raw_sent[self.source_col][index], "<TOKENSAYINGTHEREISNONAMEDENTITY>")

    def is_function_word(self, word):
        return word in self.function_words

    def token_should_be_ignored(self, tok, idx, sent, sent_idx):
        return (
            (self.using_nes and part_of_ne(tok, idx, sent, self.raw_sent[self.source_col][sent_idx], self.get_english_entity(sent_idx), False)) or
            is_punctuation(tok) or
            self.is_function_word(tok)
        )

    def nonnes_nonfunctions_len(self, sent, sent_idx):
        return sum(1 for j, tok in enumerate(sent) if not self.token_should_be_ignored(tok, j, sent, sent_idx))

    def discount_unaligned(self, unaligned_list, s1, x):
        return [j for j in unaligned_list if not self.token_should_be_ignored(s1[j], j, s1, x)]

    def align(self, s1, s2):
        return self.aligner.get_word_aligns(s1, s2)['itermax']

    def usw(self, sent1, sent2, x, key):
        alignments = self.align(sent1, sent2)
        aligned_src_indices = {pair[0] for pair in alignments}
        unaligned = [i for i in range(len(sent1)) if i not in aligned_src_indices]
        unaligned = self.discount_unaligned(unaligned, sent1, x)
        true_len = self.nonnes_nonfunctions_len(sent1, x)
        return len(unaligned) / true_len if true_len > 0 else 0

    def score_pair(self, eng_sent, tar_sent, index, col):
        return 1 - self.usw(eng_sent, tar_sent, index, col),

    def check_for_ne(self, key, index):
        if not self.using_nes:
            return False
        translation = self.raw_sent[key][index].lower()
        source = self.raw_sent[self.source_col][index]
        entities = self.entities_t.get(source, "").split(';')
        return any(entity.strip().lower() in translation for entity in entities)

    def score_all(self):
        self.scores_asw = []
        for i, row in enumerate(self.translations):
            for key in row:
                if key != self.source_col:
                    self.has_ne[key][i] = self.check_for_ne(key, i)
        for i, row in enumerate(self.translations):
            row_scores = {}
            print(i)
            for key in row:
                if key != self.source_col:
                    row_scores[key] = (0 if self.language == "th" and key == "DeepL"
                                       else self.score_pair(row[self.source_col], row[key], i, key))
            self.scores_asw.append(row_scores)

    def choose(self, index):
        keys = [k for k in self.translations[0] if k != self.source_col]
        candidates = [k for k in keys if self.has_ne[k][index]]
        if not candidates:
            candidates = keys.copy()
        values = [
            self.scores_asw[index][c] for c in candidates
            if not (self.language == 'th' and c == 'DeepL')
        ]
        best_value = max(values)
        best = [
            c for c in candidates
            if (self.language != 'th' or c != 'DeepL') and self.scores_asw[index][c] == best_value
        ]
        was_tie = int(len(best) > 1)
        return self.raw_sent[random.choice(best)][index], best[0], was_tie

    def write_choices(self, output_file):
        total, ties = 0, 0
        keys = [k for k in self.translations[0] if k != self.source_col]
        header = ["Choice", "Choice System"]
        for k in keys:
            header += [f"{k} ASW Score", f"{k} Has NE", f"{k} Translation"]
        lines = [header]
        for i, _ in enumerate(self.translations):
            total += 1
            choice, system, tie = self.choose(i)
            ties += tie
            row = [choice, system]
            for k in keys:
                row += [self.scores_asw[i][k], self.has_ne[k][i], self.raw_sent[k][i]]
            lines.append(row)
        self.tie_proportion = (ties * 100) // total
        with open(output_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerows(lines)





def parse_arguments():
    parser = argparse.ArgumentParser(description="Process alignment and NE files for a given language.")

    parser.add_argument(
        "--input-file", "-i",
        type=str,
        required=True,
        help="Path to the input file"
    )
    parser.add_argument(
    "--input-cols", "-c",
    nargs="+",
    type=str,
    required=True,
    help="List of input column names"
)
    parser.add_argument(
        "--output-file", "-o",
        type=str,
        required=True,
        help="Path to the output file"
    )
    parser.add_argument(
        "--source-col", "-s",
        type=str,
        required=True,
        help="Name of the column containing the source sentence."
    )
    parser.add_argument(
        "--ne-file", "-n",
        type=str,
        required=False,
        help="Path to the Named Entity (NE) file"
    )
    parser.add_argument(
        "--ne-col-src", "-e",
        type=str,
        required=False,
        help="Column name where the English-language NE is found"
    )
    parser.add_argument(
        "--ne-col-tgt", "-t",
        type=str,
        required=False,
        help="Column name where the Target-language NE is found"
    )
    parser.add_argument(
        "--language", "-l",
        type=str,
        required=True,
        choices=sorted(SUPPORTED_LANGUAGES),
        help="Two-letter language code (e.g., 'fr', 'zh')"
    )

    args = parser.parse_args()
    if args.ne_file and args.ne_col_src and args.ne_col_tgt:
        using_nes = True
        ne_file = args.ne_file
        ne_col_t = args.ne_col_tgt
        ne_col_s = args.ne_col_src
    elif args.ne_file or args.ne_col_tgt or args.ne_col_src:
        parser.error("--ne-file and --ne-col-target and --ne-col-source must be provided together.")
    else:
        print("Skipping NE logic. ")
        using_nes = False
        ne_file = ''
        ne_col_t = ''
        ne_col_s = ''
    
    

    return args, using_nes, ne_file, ne_col_t, ne_col_s

def main():
    args, using_nes, ne_file, ne_col_t, ne_col_s = parse_arguments()
    print(f"Parsed arguments: {args}")
    
    le = LiteralEnsembler(args.input_file, args.source_col, ne_file, ne_col_s, ne_col_t, args.input_cols, args.language, using_nes)
    le.score_all()
    le.write_choices(args.output_file)

if __name__ == "__main__":
    main()