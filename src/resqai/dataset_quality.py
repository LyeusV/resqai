from __future__ import annotations

from pathlib import Path
import pandas as pd
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET_PATH = PROJECT_ROOT / "dataset" / "dataset.csv"


class DatasetQualityAnalyzer:
    """
    Dataset kalitesini analiz eder: duplicate, bos degerler, class imbalance vb.
    """

    def __init__(self, dataset_path: Path = DEFAULT_DATASET_PATH):
        self.dataset_path = dataset_path
        self.data = pd.read_csv(dataset_path)

    def check_duplicates(self) -> dict:
        """Duplicate satirlari kontrol et."""
        duplicates_count = self.data.duplicated().sum()
        duplicates_text = self.data.duplicated(subset=["metin"]).sum()

        return {
            "total_duplicates": int(duplicates_count),
            "text_duplicates": int(duplicates_text),
            "has_issues": duplicates_count > 0 or duplicates_text > 0,
        }

    def check_empty_values(self) -> dict:
        """Bos veya null degerler kontrol et."""
        empty_metin = self.data["metin"].isna().sum() + (
            self.data["metin"].astype(str).str.strip() == ""
        ).sum()
        empty_niyet = self.data["niyet"].isna().sum() + (
            self.data["niyet"].astype(str).str.strip() == ""
        ).sum()

        return {
            "empty_metin": int(empty_metin),
            "empty_niyet": int(empty_niyet),
            "has_issues": empty_metin > 0 or empty_niyet > 0,
        }

    def check_class_distribution(self) -> dict:
        """Intent siniflari dagilim kontrol et."""
        class_counts = Counter(self.data["niyet"])
        total = len(self.data)

        distribution = {
            intent: {
                "count": count,
                "percentage": round((count / total) * 100, 2),
            }
            for intent, count in class_counts.items()
        }

        # Imbalance kontrolu: eger bir sinif %50'den fazla ise flag et
        max_percentage = max(d["percentage"] for d in distribution.values())
        has_imbalance = max_percentage > 50

        return {
            "distribution": distribution,
            "has_imbalance": has_imbalance,
            "max_percentage": round(max_percentage, 2),
        }

    def check_text_length(self) -> dict:
        """Metin uzunluk istatistikleri."""
        text_lengths = self.data["metin"].astype(str).str.len()

        return {
            "min_length": int(text_lengths.min()),
            "max_length": int(text_lengths.max()),
            "avg_length": round(text_lengths.mean(), 2),
            "median_length": int(text_lengths.median()),
        }

    def generate_report(self) -> dict:
        """Tum kalite kontrolleri yap ve rapor olustur."""
        report = {
            "dataset_file": str(self.dataset_path),
            "total_rows": len(self.data),
            "unique_intents": self.data["niyet"].nunique(),
            "duplicates": self.check_duplicates(),
            "empty_values": self.check_empty_values(),
            "class_distribution": self.check_class_distribution(),
            "text_statistics": self.check_text_length(),
            "overall_quality": "GOOD",
        }

        # Kalite skoru hesapla
        issues = 0
        if report["duplicates"]["has_issues"]:
            issues += 1
        if report["empty_values"]["has_issues"]:
            issues += 1
        if report["class_distribution"]["has_imbalance"]:
            issues += 1

        if issues >= 2:
            report["overall_quality"] = "POOR"
        elif issues == 1:
            report["overall_quality"] = "FAIR"

        return report

    def print_report(self) -> None:
        """Raporu yazdır."""
        report = self.generate_report()

        print("\n" + "=" * 60)
        print("DATASET KALITE RAPORU")
        print("=" * 60)
        print(f"Dosya: {report['dataset_file']}")
        print(f"Toplam satır: {report['total_rows']}")
        print(f"Benzersiz intent: {report['unique_intents']}")

        print("\n--- Duplicate Kontrol ---")
        dup = report["duplicates"]
        print(f"Toplam duplicate: {dup['total_duplicates']}")
        print(f"Metin duplicate: {dup['text_duplicates']}")
        print(f"Durum: {'✗ SORUN' if dup['has_issues'] else '✓ TEMIZ'}")

        print("\n--- Bos Degerler ---")
        empty = report["empty_values"]
        print(f"Bos metin: {empty['empty_metin']}")
        print(f"Bos niyet: {empty['empty_niyet']}")
        print(f"Durum: {'✗ SORUN' if empty['has_issues'] else '✓ TEMIZ'}")

        print("\n--- Class Dagitimi ---")
        dist = report["class_distribution"]
        for intent, info in dist["distribution"].items():
            print(f"  {intent}: {info['count']} ({info['percentage']}%)")
        imbalance_flag = "✗ IMBALANCED" if dist["has_imbalance"] else "✓ DENGELI"
        print(f"Durum: {imbalance_flag}")

        print("\n--- Metin Istatistikleri ---")
        stats = report["text_statistics"]
        print(f"Min uzunluk: {stats['min_length']}")
        print(f"Max uzunluk: {stats['max_length']}")
        print(f"Ort uzunluk: {stats['avg_length']}")
        print(f"Medyan uzunluk: {stats['median_length']}")

        print("\n--- Genel Kalite ---")
        print(f"Kalite Seviyesi: {report['overall_quality']}")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    analyzer = DatasetQualityAnalyzer()
    analyzer.print_report()
