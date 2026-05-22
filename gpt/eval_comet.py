import json
import logging
import os
from datasets import load_dataset
from comet import download_model, load_from_checkpoint
import zipfile

logger = logging.getLogger(__name__)

COMET_MODEL_NAME = "Unbabel/wmt22-comet-da"
DATASET_NAME = "sapienzanlp/ea-mt-benchmark"
DATASET_SPLIT_KEY = "en-zh"
BATCH_SIZE = 32
NUM_GPUS = 1


def eval_comet(system_name, language_name, split_name):
    SOURCE_LANGUAGE = "en_US"
    DATA_DIR = "./data"

    # Load references
    references = {}
    if split_name == "test_without_targets":
        dataset = load_dataset(DATASET_NAME, DATASET_SPLIT_KEY)
        references = {
            ex["id"]: {"id": ex["id"], "source": ex["source"], "targets": ex["targets"]}
            for ex in dataset["test"]
        }
    else:
        PATH_TO_REFERENCES = os.path.join(
            DATA_DIR, "references", split_name, f"{language_name}.jsonl"
        )
        with open(PATH_TO_REFERENCES, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                references[data["id"]] = data

    # Load predictions
    if split_name == "test_without_targets":
        zip_path = os.path.join(DATA_DIR, f"predictions", f"{split_name}.zip")
        extract_path = os.path.join(DATA_DIR, f"predictions", split_name)

        if not os.path.exists(extract_path):
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_path)

        PATH_TO_PREDICTIONS = os.path.join(
            extract_path, split_name, f"{language_name}.jsonl"
        )
        predictions = {}
        with open(PATH_TO_PREDICTIONS, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                predictions[data["id"]] = data
    else:
        PATH_TO_PREDICTIONS = os.path.join(
            DATA_DIR, "predictions", system_name, split_name, f"{language_name}.jsonl"
        )
        predictions = {}
        with open(PATH_TO_PREDICTIONS, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                predictions[data["id"]] = data

    # Match references and predictions
    ids = set(references.keys()) & set(predictions.keys())
    logger.info(f"Found {len(ids)} matching instances.")
    num_missing_predictions = len(references) - len(ids)

    # Prepare instances for COMET evaluation
    instances = []
    instance_ids = {}
    current_index = 0
    for id in sorted(list(ids)):
        reference = references[id]
        prediction = predictions[id]
        for target in reference["targets"]:
            instances.append(
                {
                    "src": reference["source"],
                    "ref": target["translation"],
                    "mt": prediction["prediction"],
                }
            )
        instance_ids[id] = [current_index, current_index + len(reference["targets"])]
        current_index += len(reference["targets"])

    logger.info(f"Loaded {len(instances)} instances.")

    # Load COMET model and evaluate
    model_path = download_model(COMET_MODEL_NAME)
    model = load_from_checkpoint(model_path)
    if len(instances) == 0:
        print("❌ ERROR: No instances to evaluate! Check dataset loading.")
        return 0.0
    outputs = model.predict(instances, batch_size=BATCH_SIZE, gpus=NUM_GPUS)
    scores = outputs.scores

    # Compute system score
    max_scores = [
        max(scores[indices[0] : indices[1]]) for id, indices in instance_ids.items()
    ]
    system_score = sum(max_scores) / (len(max_scores) + num_missing_predictions)

    return system_score


if __name__ == "__main__":
    print(eval_comet("gpt-4o-2024-08-06", "fr_FR", "test_without_targets"))
