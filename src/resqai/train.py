from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

from .model import DEFAULT_DATASET_PATH, DEFAULT_MODEL_PATH, load_dataset, save_model, train_model
from .metrics import MetricsLogger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ResQAI intent model egitimi")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET_PATH)
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL_PATH)
    return parser.parse_args()


def split_dataset(data: Any):
    if len(data) < 4 or data["niyet"].nunique() < 2:
        return data, data

    try:
        return train_test_split(
            data,
            test_size=0.2,
            random_state=42,
            stratify=data["niyet"] if data["niyet"].nunique() > 1 else None,
        )
    except ValueError:
        return train_test_split(data, test_size=0.2, random_state=42)


def main() -> None:
    args = parse_args()
    data = load_dataset(args.dataset)

    train_data, test_data = split_dataset(data)

    model = train_model(train_data)
    predictions = model.predict(test_data["metin"])

    # Classification report
    report = classification_report(
        test_data["niyet"],
        predictions,
        zero_division=0,
        output_dict=True,
    )

    print(classification_report(test_data["niyet"], predictions, zero_division=0))

    # Extract metrics
    accuracy = report.get("accuracy", 0.0)
    macro_avg = report.get("macro avg", {})
    macro_f1 = macro_avg.get("f1-score", 0.0)
    macro_precision = macro_avg.get("precision", 0.0)
    macro_recall = macro_avg.get("recall", 0.0)

    # Prepare class-wise metrics
    class_metrics = {}
    for intent in data["niyet"].unique():
        if intent in report:
            class_metrics[intent] = {
                "precision": report[intent].get("precision", 0.0),
                "recall": report[intent].get("recall", 0.0),
                "f1-score": report[intent].get("f1-score", 0.0),
                "support": int(report[intent].get("support", 0)),
            }

    # Log metrics
    logger = MetricsLogger()
    logger.log_training(
        accuracy=accuracy,
        macro_avg_f1=macro_f1,
        macro_avg_precision=macro_precision,
        macro_avg_recall=macro_recall,
        class_metrics=class_metrics,
        dataset_size=len(data),
        train_size=len(train_data),
        test_size=len(test_data),
        model_params={
            "vectorizer": "TfidfVectorizer(ngram_range=(1,2))",
            "classifier": "LogisticRegression(max_iter=1000, class_weight=balanced)",
        },
    )

    save_model(model, args.model_path)
    print(f"Model kaydedildi: {args.model_path}")


if __name__ == "__main__":
    main()
