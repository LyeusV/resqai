from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


@dataclass
class ExtractedEntities:
    alerjenler: list[str]
    kategori: str | None
    kategoriler: list[str]
    fiyat_min: int | None
    fiyat_max: int | None
    is_yemek: bool = False



# Alerjen esilestirme sozlugu
ALLERGEN_KEYWORDS = {
    "fistik": ["fistik", "yer fistigi"],
    "gluten": ["gluten", "un"],
    "sut": ["sut", "sutsuz", "laktozsuz", "yogurt", "peynir", "krem", "kremali"],
    "yumurta": ["yumurta"],
    "balik": ["balik", "ton", "somon"],
    "hindistan_cevizi": ["hindistan cevizi", "hindistancevizi"],
    "cikolata": ["cikolata", "kakao"],
    "susam": ["susam", "tahin"],
    "soya": ["soya", "soya sutu", "soya sosu"],
    "kuruyemis": ["kuruyemis", "ceviz", "findik", "badem", "kaju"],
    "mantar": ["mantar", "mantarli"],
}


def normalize_text(text: str) -> str:
    """
    Turkce karakterleri ve aksanli harfleri normalize ederek
    kurallarin daha stabil calismasini saglar.
    """
    lowered = text.lower().replace("ı", "i")
    normalized = unicodedata.normalize("NFKD", lowered)
    ascii_text = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return ascii_text


# Kategori eslestirme sozlugu
CATEGORY_KEYWORDS = {
    "kahve": ["kahve", "espresso", "latte", "cappuccino", "americano", "mocha", "macchiato", "flat white", "filtre kahve"],
    "sicak_icecek": ["sicak icecek", "sıcak içecek", "sicak içecek", "çay", "cay", "salep", "hot chocolate", "sicak cikolata", "bitki çayı", "bitki cayi", "türk kahvesi", "turk kahvesi"],
    "soguk_icecek": ["soğuk içecek", "soguk icecek", "iced", "cold brew", "smoothie", "limonata", "ayran", "ice tea", "iced tea", "buzlu"],
    "kahvalti": ["kahvalti", "kahvaltı", "serpme", "omlet", "menemen", "tost", "yumurta", "brunch"],
    "atistirmalik": ["atistirmalik", "atıştırmalık", "snack", "patates", "soğan halkası", "sogan halkasi", "nachos", "bruschetta", "mozzarella"],
    "salata": ["salata", "sezar", "roka", "coban", "çoban", "akdeniz"],
    "ana_yemek": ["ana yemek", "ızgara", "izgara", "burger", "köfte", "kofte", "tavuk sis", "tavuk şiş", "somon", "fajita", "makarna", "noodle"],
    "tatli": ["tatli", "tatlı", "dessert", "kek", "brownie", "cheesecake", "tiramisu", "waffle", "profiterol", "dondurma", "sorbe"],
    "pizza": ["pizza", "margherita", "pepperoni"],
    "wrap": ["wrap", "dürüm", "durum"],
    "corba": ["çorba", "corba", "mercimek", "domates çorbası", "domates corbasi", "mantar çorbası", "tavuk suyu"],
    "cocuk_menu": ["çocuk menüsü", "cocuk menusu", "kids", "çocuk", "cocuk"],
    "vegan": ["vegan", "buddha bowl", "vegan burger", "vegan wrap"],
    "burger": ["burger", "cheeseburger", "bbq burger", "double burger"],
    "makarna": ["makarna", "pesto", "fettucine", "penne", "alfredo"],
}


def extract_allergens(text: str) -> list[str]:
    """
    Metinden alerjen isimleri cikar.
    Cikti: liste (Ornek: ["fistik", "gluten"])
    """
    text_lower = normalize_text(text)
    found_allergens = set()

    for allergen_key, keywords in ALLERGEN_KEYWORDS.items():
        for keyword in keywords:
            if normalize_text(keyword) in text_lower:
                found_allergens.add(allergen_key)
                break

    return sorted(list(found_allergens))


def extract_category(text: str) -> str | None:
    """
    Metinden kategori cikart.
    Cikti: kategori adi veya None
    """
    text_lower = normalize_text(text)

    for category_key, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if normalize_text(keyword) in text_lower:
                return category_key

    return None


def extract_categories(text: str) -> list[str]:
    """
    Metinden birden fazla kategori cikart.
    Cikti: kategori listesi
    """
    text_lower = normalize_text(text)
    found_categories = []

    for category_key, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if normalize_text(keyword) in text_lower:
                found_categories.append(category_key)
                break

    # Sirayi koruyup tekrar edenleri temizle
    deduped = []
    for category in found_categories:
        if category not in deduped:
            deduped.append(category)

    return deduped


def extract_price_range(text: str) -> tuple[int | None, int | None]:
    """
    Metinden fiyat araligini cikar.
    'altinda', 'ucuz' gibi kelimelerle baglamsal analiz yapar.
    Cikti: (min_fiyat, max_fiyat)
    """
    normalized = normalize_text(text)

    # Sayilari bul (₺ ve TL yanindakiler dahil)
    numbers = re.findall(r"\d+", normalized)

    if not numbers:
        # Sayi yok ama ucuz/pahali gibi anahtar kelimeler var mi?
        under_words = ["ucuz", "uygun", "hesapli", "butce"]
        over_words = ["pahali", "luks", "premium"]
        if any(w in normalized for w in under_words):
            return None, 150  # Default ucuz esigi
        if any(w in normalized for w in over_words):
            return 200, None  # Default pahali esigi
        return None, None

    numbers_int = sorted([int(n) for n in numbers if int(n) >= 10])  # 10 altini filtrele

    if not numbers_int:
        return None, None

    # Baglam analizi icin anahtar kelimeler
    under_words = ["altinda", "alti", "asagi", "ucuz", "uygun", "butce", "kadar", "gecmesin"]
    over_words = ["ustunde", "ustu", "uzeri", "uzerinde", "yukari", "pahali"]
    around_words = ["civarinda", "civari", "dolaylarinda", "yaklasik"]

    has_under = any(w in normalized for w in under_words)
    has_over = any(w in normalized for w in over_words)
    has_around = any(w in normalized for w in around_words)

    if len(numbers_int) == 1:
        val = numbers_int[0]
        if has_under:
            return None, val
        elif has_over:
            return val, None
        elif has_around:
            margin = max(int(val * 0.2), 20)
            return max(0, val - margin), val + margin
        else:
            # Varsayilan: tek sayi varsa "altinda" olarak yorumla
            return None, val
    else:
        return numbers_int[0], numbers_int[-1]


def extract_entities(text: str) -> ExtractedEntities:
    """
    Metni analiz et ve varligalari cikar.
    Cikti: ExtractedEntities nesnesi
    """
    alerjenler = extract_allergens(text)
    kategori = extract_category(text)
    kategoriler = extract_categories(text)
    fiyat_min, fiyat_max = extract_price_range(text)

    # "yemek", "yiyecek" kelimelerini kontrol et (tatli ve icecekleri ayirt etmek icin)
    normalized = normalize_text(text)
    is_yemek = any(w in normalized for w in ["yemek", "yiyecek", "atistiracak", "tuzlu"])

    return ExtractedEntities(
        alerjenler=alerjenler,
        kategori=kategori,
        kategoriler=kategoriler,
        fiyat_min=fiyat_min,
        fiyat_max=fiyat_max,
        is_yemek=is_yemek,
    )

