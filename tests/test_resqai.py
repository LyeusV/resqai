from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from resqai.api import app
from resqai.model import load_dataset
from resqai.responses import response_for_intent
from resqai.entities import extract_entities, extract_allergens, extract_category, extract_categories, extract_price_range
from resqai.repository import MenuRepository


def test_dataset_loads_with_expected_columns() -> None:
    dataset_path = Path(__file__).resolve().parents[1] / "dataset" / "dataset.csv"
    data = load_dataset(dataset_path)

    assert not data.empty
    assert set(data.columns) == {"metin", "niyet"}


def test_response_mapping_includes_known_intents() -> None:
    assert response_for_intent("menu_isteme", "Menude neler var?")
    assert response_for_intent("fiyat_sorma", "Ne kadar?")
    assert response_for_intent("alerjen_oneri_isteme", "Fistik alerjim var")


def test_health_endpoint() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"ok": True}


# --- Entity Extraction Tests ---


def test_extract_allergens_finds_fistik() -> None:
    text = "Fistik alerjim var"
    allergens = extract_allergens(text)
    assert "fistik" in allergens


def test_extract_allergens_finds_gluten() -> None:
    text = "Glutensiz secenek istiyorum"
    allergens = extract_allergens(text)
    assert "gluten" in allergens


def test_extract_allergens_finds_sut() -> None:
    text = "Sut icermeyen tatli onerir misiniz?"
    allergens = extract_allergens(text)
    assert "sut" in allergens


def test_extract_allergens_returns_empty_when_none() -> None:
    text = "Menude neler var?"
    allergens = extract_allergens(text)
    assert len(allergens) == 0


def test_extract_category_finds_tatli() -> None:
    category = extract_category("Tatli menusu neler?")
    assert category == "tatli"


def test_extract_category_finds_kahve() -> None:
    category = extract_category("Kahve cesitleri nelerdir?")
    assert category == "kahve"


def test_extract_category_finds_soguk_icecek() -> None:
    category = extract_category("Soguk icecekler var mi?")
    assert category == "soguk_icecek"


def test_extract_category_finds_sicak_icecek() -> None:
    category = extract_category("Sicak icecekler neler var?")
    assert category == "sicak_icecek"


def test_extract_category_finds_ana_yemek() -> None:
    category = extract_category("Ana yemekler neler?")
    assert category == "ana_yemek"


def test_extract_category_finds_atistirmalik() -> None:
    category = extract_category("Atistirmalik olarak ne var?")
    assert category == "atistirmalik"


def test_extract_category_finds_pizza() -> None:
    category = extract_category("Pizza var mi?")
    assert category == "pizza"


def test_extract_category_finds_wrap() -> None:
    category = extract_category("Wrap önerir misiniz?")
    assert category == "wrap"


def test_extract_category_finds_corba() -> None:
    category = extract_category("Corba neler var?")
    assert category == "corba"


def test_extract_category_finds_vegan() -> None:
    category = extract_category("Vegan yemekler nelerdir?")
    assert category == "vegan"


def test_extract_categories_finds_multiple() -> None:
    categories = extract_categories("Pizza ve wrap var mi?")
    assert "pizza" in categories
    assert "wrap" in categories


def test_extract_categories_finds_corba_and_main() -> None:
    categories = extract_categories("Corba ve ana yemekler neler?")
    assert "corba" in categories
    assert "ana_yemek" in categories


def test_extract_category_returns_none_when_none() -> None:
    category = extract_category("Fiyat ne kadar?")
    assert category is None


def test_extract_price_range_finds_single_price() -> None:
    min_p, max_p = extract_price_range("100 lira altinda ne var?")
    assert min_p == 100 or max_p == 100


def test_extract_price_range_finds_price_range() -> None:
    min_p, max_p = extract_price_range("50 ile 150 lira arasinda")
    assert min_p in [50, 150] and max_p in [50, 150]


def test_extract_price_range_returns_none_when_none() -> None:
    min_p, max_p = extract_price_range("Menude neler var?")
    assert min_p is None and max_p is None


def test_extract_entities_combines_all() -> None:
    entities = extract_entities("Fistik alerjim var, tatli onerir misiniz?")
    assert "fistik" in entities.alerjenler
    assert entities.kategori == "tatli"


# --- Repository Tests ---


def test_menu_repository_loads() -> None:
    repo = MenuRepository()
    items = repo.get_all_items()
    assert len(items) > 0


def test_repository_get_by_category_tatli() -> None:
    repo = MenuRepository()
    items = repo.get_by_category("tatli")
    assert len(items) > 0
    assert all(item.get("kategori") == "tatli" for item in items)


def test_repository_get_by_category_kahve() -> None:
    repo = MenuRepository()
    items = repo.get_by_category("kahve")
    assert len(items) > 0
    assert all(item.get("kategori") == "kahve" for item in items)


def test_repository_get_by_category_sicak_icecek() -> None:
    repo = MenuRepository()
    items = repo.get_by_category("sicak_icecek")
    assert len(items) > 0
    assert all(item.get("kategori") == "sicak_icecek" for item in items)


def test_repository_get_by_category_ana_yemek() -> None:
    repo = MenuRepository()
    items = repo.get_by_category("ana_yemek")
    assert len(items) > 0
    assert all(item.get("kategori") == "ana_yemek" for item in items)


def test_repository_get_by_category_pizza() -> None:
    repo = MenuRepository()
    items = repo.get_by_category("pizza")
    assert len(items) > 0
    assert all(item.get("kategori") == "pizza" for item in items)


def test_repository_get_by_category_wrap() -> None:
    repo = MenuRepository()
    items = repo.get_by_category("wrap")
    assert len(items) > 0
    assert all(item.get("kategori") == "wrap" for item in items)


def test_repository_get_by_category_corba() -> None:
    repo = MenuRepository()
    items = repo.get_by_category("corba")
    assert len(items) > 0
    assert all(item.get("kategori") == "corba" for item in items)


def test_repository_get_safe_for_allergens() -> None:
    repo = MenuRepository()
    items = repo.get_safe_for_allergens(["sut"])
    assert len(items) > 0
    # Verify no "sut" allergen in results
    for item in items:
        assert "sut" not in item.get("alerjenler", [])


def test_repository_get_by_price_range_max() -> None:
    repo = MenuRepository()
    items = repo.get_by_price_range(max_price=100)
    assert len(items) > 0
    assert all(item.get("fiyat", 0) <= 100 for item in items)


def test_repository_get_by_price_range_min() -> None:
    repo = MenuRepository()
    items = repo.get_by_price_range(min_price=150)
    assert len(items) > 0
    assert all(item.get("fiyat", 0) >= 150 for item in items)


def test_repository_get_recommendations_combined() -> None:
    repo = MenuRepository()
    items = repo.get_recommendations(
        kategori="tatli",
        alerjenler=["sut"],
    )
    assert len(items) > 0
    for item in items:
        assert item.get("kategori") == "tatli"
        assert "sut" not in item.get("alerjenler", [])


def test_repository_format_items_as_text() -> None:
    repo = MenuRepository()
    items = repo.get_all_items()[:2]
    text = repo.format_items_as_text(items)
    assert len(text) > 0
    assert "TL" in text
