from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ExtractedEntities:
    alerjenler: list[str]
    kategori: str | None
    fiyat_min: int | None
    fiyat_max: int | None


# Alerjen esilestirme sozlugu
ALLERGEN_KEYWORDS = {
    "fistik": ["fistik", "yer fistigi"],
    "gluten": ["gluten", "un"],
    "sut": ["sut", "yogurt", "peynir", "krem", "kremali"],
    "yumurta": ["yumurta"],
    "balik": ["balik", "ton", "somon"],
    "kabuklu": ["karides", "istiridye"],
    "yulaf": ["yulaf"],
    "hindistan_cevizi": ["hindistan cevizi", "hindistancevizi"],
    "cikolata": ["cikolata", "kakao"],
}

# Kategori eslestirme sozlugu
CATEGORY_KEYWORDS = {
    "kahve": ["kahve", "espresso", "latte", "cappuccino"],
    "soguk_icecek": ["soguk", "buz", "ice", "cold"],
    "yiyecek": ["sandvic", "salata", "yulaf"],
    "tatli": ["tatli", "dessert", "kek", "brownie"],
}


def extract_allergens(text: str) -> list[str]:
    """
    Metinden alerjen isimleri cikar.
    Cikti: liste (Ornek: ["fistik", "gluten"])
    """
    text_lower = text.lower()
    found_allergens = set()

    for allergen_key, keywords in ALLERGEN_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                found_allergens.add(allergen_key)
                break

    return sorted(list(found_allergens))


def extract_category(text: str) -> str | None:
    """
    Metinden kategori cikart.
    Cikti: kategori adi veya None
    """
    text_lower = text.lower()

    for category_key, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                return category_key

    return None


def extract_price_range(text: str) -> tuple[int | None, int | None]:
    """
    Metinden fiyat araligini cikar.
    Cikti: (min_fiyat, max_fiyat)
    """
    # Basit regex ile fiyat sayilari bul
    numbers = re.findall(r"\b\d+\b", text)

    if not numbers:
        return None, None

    numbers_int = sorted([int(n) for n in numbers])

    if len(numbers_int) == 1:
        return numbers_int[0], numbers_int[0]
    else:
        return numbers_int[0], numbers_int[-1]


def extract_entities(text: str) -> ExtractedEntities:
    """
    Metni analiz et ve varligalari cikar.
    Cikti: ExtractedEntities nesnesi
    """
    alerjenler = extract_allergens(text)
    kategori = extract_category(text)
    fiyat_min, fiyat_max = extract_price_range(text)

    return ExtractedEntities(
        alerjenler=alerjenler,
        kategori=kategori,
        fiyat_min=fiyat_min,
        fiyat_max=fiyat_max,
    )
