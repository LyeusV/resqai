from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MENU_PATH = PROJECT_ROOT / "menu" / "menu.json"


class MenuRepository:
    """
    Menu JSON dosyasini okur ve filtreli sorgu yapar.
    """

    def __init__(self, menu_path: Path = DEFAULT_MENU_PATH):
        self.menu_path = menu_path
        self.data = self._load_menu()

    def _load_menu(self) -> dict[str, Any]:
        """Menu JSON dosyasini yükle."""
        if not self.menu_path.exists():
            raise FileNotFoundError(f"Menu dosyasi bulunamadi: {self.menu_path}")

        with open(self.menu_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_all_items(self) -> list[dict]:
        """Tum menu urunlerini getir."""
        return self.data.get("menu", [])

    def get_by_category(self, kategori: str) -> list[dict]:
        """Kategoriye gore menu urunlerini filtrele."""
        items = self.get_all_items()
        return [item for item in items if item.get("kategori") == kategori]

    def get_safe_for_allergens(
        self, alerjenler: list[str]
    ) -> list[dict]:
        """
        Verilen alerjenler icermeyen urunleri getir.
        """
        items = self.get_all_items()
        safe_items = []

        for item in items:
            item_allergens = set(item.get("alerjenler", []))
            user_allergens = set(alerjenler)

            # Eger urunun alerjeninde kullanici alerjenleri varsa, skip et
            if not item_allergens.intersection(user_allergens):
                safe_items.append(item)

        return safe_items

    def get_by_price_range(
        self, min_price: int | None = None, max_price: int | None = None
    ) -> list[dict]:
        """Fiyat araligina gore filtrele."""
        items = self.get_all_items()
        filtered = items

        if min_price is not None:
            filtered = [item for item in filtered if item.get("fiyat", 0) >= min_price]

        if max_price is not None:
            filtered = [item for item in filtered if item.get("fiyat", 0) <= max_price]

        return filtered

    def get_recommendations(
        self,
        kategori: str | None = None,
        alerjenler: list[str] | None = None,
        fiyat_min: int | None = None,
        fiyat_max: int | None = None,
    ) -> list[dict]:
        """
        Kombine filtre ile oneriler getir.
        """
        items = self.get_all_items()

        # Kategori
        if kategori:
            items = [item for item in items if item.get("kategori") == kategori]

        # Alerjen
        if alerjenler:
            safe_items = self.get_safe_for_allergens(alerjenler)
            items = [item for item in items if item in safe_items]

        # Fiyat
        if fiyat_min is not None:
            items = [item for item in items if item.get("fiyat", 0) >= fiyat_min]

        if fiyat_max is not None:
            items = [item for item in items if item.get("fiyat", 0) <= fiyat_max]

        return items

    def format_items_as_text(self, items: list[dict]) -> str:
        """Urunleri okunakli metin olarak formatla."""
        if not items:
            return "Maalesef, uygun urun bulunamadi."

        lines = []
        for item in items:
            isim = item.get("isim", "Bilinmeyen")
            fiyat = item.get("fiyat", 0)
            lines.append(f"- {isim}: {fiyat} TL")

        return "\n".join(lines)
