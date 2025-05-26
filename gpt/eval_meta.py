import json
import os
import re
import zipfile
from typing import Dict, List, Set
from datasets import load_dataset


def load_references(
    split_name: str, language_name: str, data_dir: str, entity_types: List[str]
) -> List[dict]:
    """
    Load references from the dataset or JSONL files.

    Args:
        split_name (str): Dataset split name.
        language_name (str): Language code.
        data_dir (str): Directory containing data.
        entity_types (List[str]): Entity types for filtering.

    Returns:
        List[dict]: References as a list of dictionaries.
    """
    references = {}
    if split_name == "test_without_targets":
        dataset = load_dataset("sapienzanlp/ea-mt-benchmark", "en-zh")
        references = {
            ex["id"]: {"id": ex["id"], "source": ex["source"], "targets": ex["targets"]}
            for ex in dataset["test"]
        }
        print(f"Loaded {len(references)} references from dataset.")
    else:
        ref_path = os.path.join(
            data_dir, "references", split_name, f"{language_name}.jsonl"
        )
        with open(ref_path, encoding="utf-8") as f:
            for line in f:
                line_data = json.loads(line.strip())
                references[line_data["id"]] = line_data

    return references


def load_predictions(
    system_name: str, language_name: str, split_name: str, data_dir: str
) -> Dict[str, str]:
    """
    Load predictions from JSONL files or extracted zip files.

    Args:
        system_name (str): Name of the system.
        language_name (str): Language code.
        split_name (str): Dataset split name.
        data_dir (str): Directory containing data.

    Returns:
        Dict[str, str]: Predictions as a dictionary.
    """
    predictions = {}
    if split_name == "test_without_targets":
        zip_path = os.path.join(data_dir, "predictions", f"{split_name}.zip")
        extract_path = os.path.join(data_dir, "predictions", split_name)
        if not os.path.exists(extract_path):
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_path)
        pred_path = os.path.join(extract_path, split_name, f"{language_name}.jsonl")
    else:
        pred_path = os.path.join(
            data_dir, "predictions", system_name, split_name, f"{language_name}.jsonl"
        )

    with open(pred_path, "r", encoding="utf-8") as f:
        for line in f:
            line_data = json.loads(line.strip())
            if split_name != "test_without_targets":
                match = re.match(r"Q[0-9]+_[0-9]", line_data["id"])
                if not match:
                    raise ValueError(f"Invalid instance ID: {line_data['id']}")
                predictions[match.group(0)] = line_data["prediction"]
            else:
                predictions[line_data["id"]] = line_data["prediction"]

    return predictions


def compute_entity_name_translation_accuracy(
    predictions: Dict[str, str], mentions: Dict[str, Set[str]], verbose: bool = False
) -> dict:
    """
    Compute translation accuracy for entity names.

    Args:
        predictions (Dict[str, str]): Model predictions.
        mentions (Dict[str, Set[str]]): Ground truth mentions.
        verbose (bool): Print details for mismatches.

    Returns:
        dict: Accuracy metrics.
    """
    correct, total = 0, len(mentions)
    for instance_id, instance_mentions in mentions.items():
        if instance_id not in predictions:
            if verbose:
                print(f"No prediction for instance {instance_id}")
            continue
        if any(
            m.casefold() in predictions[instance_id].casefold()
            for m in instance_mentions
        ):
            correct += 1
    return {
        "correct": correct,
        "total": total,
        "accuracy": correct / total if total > 0 else 0.0,
    }


def get_mentions_from_references(data: List[dict]) -> Dict[str, Set[str]]:
    """
    Extract entity mentions from references.

    Args:
        data (List[dict]): Reference data.

    Returns:
        Dict[str, Set[str]]: Mentions grouped by instance ID.
    """
    mentions = {}
    for instance in data.values():
        instance_id = instance["id"]
        instance_mentions = {target["mention"] for target in instance["targets"]}
        mentions[instance_id] = instance_mentions
    return mentions


def eval_meta(system_name, language_name, split_name):
    """
    Evaluate entity name translation accuracy.

    Args:
        system_name (str): Name of the system.
        language_name (str): Language code.
        split_name (str): Dataset split name.

    Returns:
        float: Accuracy score.
    """
    VERBOSE = False
    ENTITY_TYPES = [
        "Musical work",
        "Artwork",
        "Food",
        "Animal",
        "Plant",
        "Book",
        "Book series",
        "Fictional entity",
        "Landmark",
        "Movie",
        "Place of worship",
        "Natural place",
        "TV series",
        "Person",
    ]
    DATA_DIR = "./data"

    reference_data = load_references(split_name, language_name, DATA_DIR, ENTITY_TYPES)
    mentions = get_mentions_from_references(reference_data)
    prediction_data = load_predictions(system_name, language_name, split_name, DATA_DIR)
    accuracy_data = compute_entity_name_translation_accuracy(
        prediction_data, mentions, verbose=VERBOSE
    )

    print(f"\nEvaluation results in {language_name}")
    print(f"Correct instances   = {accuracy_data['correct']}")
    print(f"Total instances     = {accuracy_data['total']}")
    print(f"m-ETA               = {accuracy_data['accuracy']:.2f}\n")

    return accuracy_data["accuracy"]


if __name__ == "__main__":
    print(eval_meta("gpt-4o-2024-08-06", "fr_FR", "test_without_targets"))
