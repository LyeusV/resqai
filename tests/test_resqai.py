from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from resqai.api import app
from resqai.model import load_dataset
from resqai.responses import response_for_intent


def test_dataset_loads_with_expected_columns() -> None:
    dataset_path = Path(__file__).resolve().parents[1] / "dataset" / "dataset.csv"
    data = load_dataset(dataset_path)

    assert not data.empty
    assert set(data.columns) == {"metin", "niyet"}


def test_response_mapping_includes_known_intents() -> None:
    assert response_for_intent("menu_isteme")
    assert response_for_intent("fiyat_sorma")
    assert response_for_intent("alerjen_oneri_isteme")


def test_health_endpoint() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"ok": True}
