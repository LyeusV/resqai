from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_METRICS_LOG_PATH = PROJECT_ROOT / "training_logs" / "metrics.jsonl"


class MetricsLogger:
    """
    Model egitim metriklerini tarih + timestamp ile log dosyasina kaydeder.
    """

    def __init__(self, log_path: Path = DEFAULT_METRICS_LOG_PATH):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_training(
        self,
        accuracy: float,
        macro_avg_f1: float,
        macro_avg_precision: float,
        macro_avg_recall: float,
        class_metrics: dict[str, dict[str, float]],
        dataset_size: int,
        train_size: int,
        test_size: int,
        model_params: dict[str, Any] | None = None,
    ) -> None:
        """
        Egitim metriklerini log dosyasina kaydet.
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "accuracy": accuracy,
            "macro_avg": {
                "f1": macro_avg_f1,
                "precision": macro_avg_precision,
                "recall": macro_avg_recall,
            },
            "class_metrics": class_metrics,
            "dataset": {
                "total_size": dataset_size,
                "train_size": train_size,
                "test_size": test_size,
            },
            "model_params": model_params or {},
        }

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        print(f"Metrikler kaydedildi: {self.log_path}")

    def get_latest_metrics(self) -> dict[str, Any] | None:
        """
        Son kaydedilen metrikleri oku.
        """
        if not self.log_path.exists():
            return None

        last_line = None
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                last_line = line

        if last_line:
            return json.loads(last_line)

        return None

    def get_all_metrics(self) -> list[dict[str, Any]]:
        """
        Tum kaydedilen metrikleri oku.
        """
        if not self.log_path.exists():
            return []

        records = []
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                records.append(json.loads(line))

        return records
