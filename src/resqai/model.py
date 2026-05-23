from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from .preprocess import preprocess_text

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET_PATH = PROJECT_ROOT / "dataset" / "dataset.csv"
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "intent_model.joblib"
REQUIRED_COLUMNS = {"metin", "niyet"}


def load_dataset(dataset_path: Path = DEFAULT_DATASET_PATH) -> pd.DataFrame:
    data = pd.read_csv(dataset_path)
    missing_columns = REQUIRED_COLUMNS - set(data.columns)
    if missing_columns:
        raise ValueError(f"Dataset su kolonlari eksik: {', '.join(sorted(missing_columns))}")

    cleaned = data.loc[:, ["metin", "niyet"]].dropna().copy()
    cleaned["metin"] = cleaned["metin"].astype(str).str.strip()
    cleaned["niyet"] = cleaned["niyet"].astype(str).str.strip()
    cleaned = cleaned[(cleaned["metin"] != "") & (cleaned["niyet"] != "")]
    if cleaned.empty:
        raise ValueError("Dataset bos gorunuyor.")
    return cleaned


def build_model() -> Pipeline:
    return Pipeline(
        steps=[
            (
                "vectorizer",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    preprocessor=preprocess_text,
                    lowercase=False,
                ),
            ),
            (
                "classifier",
                LogisticRegression(max_iter=1000, class_weight="balanced"),
            ),
        ]
    )


def train_model(data: pd.DataFrame) -> Pipeline:
    model = build_model()
    model.fit(data["metin"], data["niyet"])
    return model


def save_model(model: Pipeline, model_path: Path = DEFAULT_MODEL_PATH) -> None:
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)


def load_model(model_path: Path = DEFAULT_MODEL_PATH) -> Pipeline:
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model dosyasi bulunamadi: {model_path}. Once `python -m resqai.train` calistirin."
        )
    return joblib.load(model_path)


def predict_intent(model: Pipeline, message: str, threshold: float = 0.45) -> str:
    probs = model.predict_proba([message])[0]
    max_idx = probs.argmax()
    max_prob = probs[max_idx]
    
    if max_prob < threshold:
        return "fallback"
        
    return str(model.classes_[max_idx])
