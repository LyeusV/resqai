from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

from .model import DEFAULT_DATASET_PATH, DEFAULT_MODEL_PATH, load_dataset, save_model, train_model


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

    print(classification_report(test_data["niyet"], predictions, zero_division=0))
    save_model(model, args.model_path)
    print(f"Model kaydedildi: {args.model_path}")


if __name__ == "__main__":
    main()
