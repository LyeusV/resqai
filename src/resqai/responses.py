from __future__ import annotations

from .entities import extract_entities
from .repository import MenuRepository

DEFAULT_FALLBACK = "Bunu tam anlayamadim. Farkli bir sekilde sorabilir misiniz?"

# Repository ornegi
_repo = MenuRepository()


def handle_menu_request(user_message: str) -> str:
    """Menu isteme intentini yanit ver."""
    entities = extract_entities(user_message)
    matched_categories = entities.kategoriler or ([entities.kategori] if entities.kategori else [])

    # Kategori varsa ona gore filtrele, yoksa tum menuyu goster
    if matched_categories:
        items = []
        for category in matched_categories:
            items.extend(_repo.get_by_category(category))
        category_display = ", ".join(category.replace("_", " ") for category in matched_categories)
        prefix = f"{category_display.upper()} SECENEKLERI:\n"
    else:
        items = _repo.get_all_items()
        prefix = "TUM MENU:\n"

    if not items:
        return "Bu kategoride urun bulunamadi."

    if entities.alerjenler:
        requested = set(entities.alerjenler)
        items = [
            item
            for item in items
            if not requested.intersection(set(item.get("alerjenler", [])))
        ]
        if not items:
            return "Belirttiginiz alerjenlere gore uygun urun bulunamadi."

    if matched_categories:
        menu_text = _repo.format_items_as_text(items)
        return prefix + menu_text

    grouped: dict[str, list[dict]] = {}
    for item in items:
        kategori = item.get("kategori", "diger")
        grouped.setdefault(kategori, []).append(item)

    lines = ["ResQAI Bistro & Coffee - Genis Menu", ""]
    category_titles = {
        "kahve": "Kahveler",
        "sicak_icecek": "Sicak Icecekler",
        "soguk_icecek": "Soguk Icecekler",
        "kahvalti": "Kahvalti",
        "atistirmalik": "Atistirmaliklar",
        "salata": "Salatalar",
        "ana_yemek": "Ana Yemekler",
        "tatli": "Tatlılar",
    }

    for kategori, category_items in grouped.items():
        title = category_titles.get(kategori, kategori.replace("_", " ").title())
        lines.append(f"{title}:")
        for item in category_items:
            lines.append(f"- {item.get('isim', 'Bilinmeyen')}: {item.get('fiyat', 0)} TL")
        lines.append("")

    lines.append("Alerjen veya fiyat bazli filtreleme icin dogrudan sorabilirsiniz.")
    return "\n".join(lines)


def handle_price_request(user_message: str) -> str:
    """Fiyat sorma intentini yanit ver."""
    entities = extract_entities(user_message)

    items = _repo.get_by_price_range(entities.fiyat_min, entities.fiyat_max)

    if not items:
        return "Belirtilen fiyat araliginda urun bulunamadi."

    if entities.fiyat_min and entities.fiyat_max:
        price_info = f"{entities.fiyat_min} - {entities.fiyat_max} TL"
    elif entities.fiyat_min:
        price_info = f"{entities.fiyat_min} TL ve uzeri"
    elif entities.fiyat_max:
        price_info = f"{entities.fiyat_max} TL ve alti"
    else:
        price_info = "Tüm urunler"

    prefix = f"{price_info} FIYAT ARALIGINDA ONERILER:\n"
    menu_text = _repo.format_items_as_text(items)
    return prefix + menu_text


def handle_allergen_request(user_message: str) -> str:
    """Alerjen oneri intentini yanit ver."""
    entities = extract_entities(user_message)
    matched_categories = entities.kategoriler or ([entities.kategori] if entities.kategori else [])

    if not entities.alerjenler:
        return "Alerjen bilgisi yakalanamadi. Lutfen hangi alerjenlerden kacmak istediginizi belirtin."

    allergen_display = ", ".join(entities.alerjenler)
    items = _repo.get_safe_for_allergens(entities.alerjenler)

    if not matched_categories:
        prefix = f"{allergen_display} alerjisi icin GUVENLI SECENEKLER:\n"
    else:
        category_display = ", ".join(category.replace("_", " ") for category in matched_categories)
        prefix = f"{allergen_display} alerjisi icin {category_display} KATEGORI SECENEKLERI:\n"
        items = [item for item in items if item.get("kategori") in matched_categories]

    if not items:
        return f"{allergen_display} alerjisi icin bu kategoride guvenli urun bulunamadi."

    menu_text = _repo.format_items_as_text(items)
    return prefix + menu_text


def response_for_intent(intent: str, user_message: str) -> str:
    """Niyete gore cevap uret."""
    if intent == "menu_isteme":
        return handle_menu_request(user_message)
    elif intent == "fiyat_sorma":
        return handle_price_request(user_message)
    elif intent == "alerjen_oneri_isteme":
        return handle_allergen_request(user_message)
    else:
        return DEFAULT_FALLBACK
