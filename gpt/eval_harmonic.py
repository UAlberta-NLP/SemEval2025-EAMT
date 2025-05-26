import sys
import json
import openai
import logging
import os
import re
import pandas as pd
import csv
import opencc
import argparse

from eval_comet import eval_comet
from eval_meta import eval_meta
from dotenv import load_dotenv
from tqdm import tqdm
from examples import examples
from prompts import prompts


# Disable OpenAI and httpx logging
# Configure logging level for specific loggers by name
logging.getLogger("openai").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)

# simplified to traditional
cc = opencc.OpenCC("s2t.json")

# Task Track: 'validation' or 'test_without_targets'
TRACK = "validation"

# Flags for external data sources
WIKI = False
BABELNET = False

# System name and source language
SYSTEM_NAME = "gpt-4o-2024-08-06"
SOURCE_LANGUAGE = "English"

# Language Codes
LANGUAGES = {
    "Arabic": "ar_AE",
    "English": "en_US",
    "French": "fr_FR",
    "German": "de_DE",
    "Italian": "it_IT",
    "Japanese": "ja_JP",
    "Korean": "ko_KR",
    "Thai": "th_TH",
    "Turkish": "tr_TR",
    "Spanish": "es_ES",
    "Chinese (Traditional)": "zh_TW",
}


# Load TSV file to dictionary
def load_tsv_to_dict(filename, key_column):
    data_dict = {}
    with open(filename, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter="\t")
        for row in reader:
            key = row[key_column]
            data_dict[key] = {col: row[col] for col in row if col != key_column}
    return data_dict


# open the jsonl file and read the content
def read_jsonl(file_path):
    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line))
    return data


# GPT translation function
def gpt_translation_prompt(source_language, target_language, text, wikidata_id, id):
    src_sent = examples[source_language]["source"]
    tgt_sent = examples[target_language]["target"]

    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if BABELNET:
        entity_info = bn_dict.get(id)
        if entity_info is None:
            print("Missing ids in BabelNet TSV:", id)

    elif WIKI:
        entity_info = ne_dict.get(wikidata_id)
        if entity_info is not None:
            if "All Translations" in entity_info:
                all_translations = entity_info["All Translations"]
            else:
                all_translations = "; ".join(
                    [entity_info["Label"], entity_info["Also known as"]]
                )
            if target_language == "Chinese (Traditional)":
                all_translations = cc.convert(all_translations)
        else:
            print("Missing wikidata_id:", wikidata_id)

    if WIKI == False and BABELNET == False:
        # GPT - Our Prompt
        prompt = prompts(
            "One_Shot", source_language, target_language, src_sent, tgt_sent
        )

    elif BABELNET:
        # GPT + NETs with BN
        prompt = prompts(
            "One_Shot_BN",
            source_language,
            target_language,
            src_sent,
            tgt_sent,
            ne_translation=entity_info["Label"],
            entity_info=entity_info,
        )

    else:
        # GPT + NETs with WikiData
        named_entity = entity_info["Named_Entity"]
        if target_language == "Chinese (Traditional)":
            named_entity = cc.convert(named_entity)

        if entity_info["Label"] == "" and entity_info["Also known as"] == "":
            # WikiData translation missing
            print("Missing translations:", wikidata_id)
            prompt = prompts(
                "Missing_WD",
                source_language,
                target_language,
                src_sent,
                tgt_sent,
                named_entity=named_entity,
            )

        else:
            # WikiData translation available
            prompt = prompts(
                "Soft_NETs_WD",
                source_language,
                target_language,
                src_sent,
                tgt_sent,
                ne_translation=entity_info["Label"],
                named_entity=named_entity,
                all_translations=all_translations,
            )

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": text},
    ]

    response = openai.chat.completions.create(
        model="gpt-4o-2024-08-06",
        temperature=0,
        max_tokens=200,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        messages=messages,
    )
    response.choices[0].message.content = re.sub(
        r"\s([?.!])", r"\1", response.choices[0].message.content
    )
    return response.choices[0].message.content.strip()


# Translate and write to file
def translate_and_write(input_file, output_file, source_language, target_language):
    with open(input_file, "r", encoding="utf-8") as f:
        data = [json.loads(line.strip()) for line in f.readlines()]

    translated_data = []

    for entry in tqdm(data):
        text = entry.get("source", "")
        wikidata_id = entry.get("wikidata_id", "")
        id = entry.get("id", "")

        translated_text = gpt_translation_prompt(
            source_language, target_language, text, wikidata_id, id
        )

        if target_language == "Chinese (Traditional)":
            translated_text = cc.convert(translated_text)

        new_entry = {
            "id": entry["id"],
            "source_language": entry["source_locale"],
            "target_language": entry["target_locale"],
            "text": text,
            "wikidata_id": wikidata_id,
            "prediction": translated_text,
        }
        translated_data.append(new_entry)

    with open(output_file, "w", encoding="utf-8") as f:
        for item in translated_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    translated_df = pd.DataFrame(translated_data)
    output_tsv_file = output_file.replace(".jsonl", ".tsv")
    translated_df.to_csv(output_tsv_file, sep="\t", index=False)

    print(f"Translations written to {output_file}")


# Harmonic Evaluation
def eval_harmonic(system_name, language_name, split_name):
    score_comet = eval_comet(system_name, language_name, split_name)
    score_meta = eval_meta(system_name, language_name, split_name)
    score_harmonic = (2 * score_comet * score_meta) / (score_comet + score_meta)

    print(f"comet: {score_comet}, meta: {score_meta}, harmonic: {score_harmonic}")

    return {"comet": score_comet, "meta": score_meta, "harmonic": score_harmonic}


if __name__ == "__main__":
    """
    Target Languages:
    - Arabic
    - Chinese (Traditional)
    - French
    - German
    - Italian
    - Japanese
    - Korean
    - Spanish
    - Thai
    - Turkish
    """

    parser = argparse.ArgumentParser(
        description="Translate and evaluate translations in target language"
    )
    parser.add_argument(
        "language",
        type=str,
        help="Target language to translate to: [Arabic, Chinese (Traditional), French, German, Italian, Japanese, Korean, Spanish, Thai, Turkish]",
    )

    args = parser.parse_args()
    tgt_lan = args.language

    tgt_lan_code = LANGUAGES[tgt_lan]
    input_jsonl = f"./data/references/{TRACK}/{tgt_lan_code}.jsonl"
    output_jsonl = f"./data/predictions/gpt-4o-2024-08-06/{TRACK}/{tgt_lan_code}.jsonl"

    # Wiki data
    if WIKI:
        ne_file = f"./data/wikidata/{TRACK}/{tgt_lan_code}.tsv"
        global ne_dict
        ne_dict = load_tsv_to_dict(ne_file, "wikidata_id")

    # BabelNet
    if BABELNET:
        bn_file = (
            f"./data/babelnet/{TRACK}/BabelNet_NEs_validation.xlsx - {tgt_lan_code}.tsv"
        )
        global bn_dict
        bn_dict = load_tsv_to_dict(bn_file, "id")

    translate_and_write(input_jsonl, output_jsonl, SOURCE_LANGUAGE, tgt_lan)

    if TRACK == "validation":
        d = "validation"
        evaluation = eval_harmonic(SYSTEM_NAME, tgt_lan_code, d)
        h = evaluation["harmonic"]
        print(h)


# Example usage
# python eval_harmonic.py "French"
