from __future__ import annotations

from .entities import extract_entities
from .repository import MenuRepository

DEFAULT_FALLBACK = "Bunu tam anlayamadım. Size restoran menüsü, fiyatlar veya alerjen uyarıları hakkında yardımcı olabilirim."

# Repository ornegi
_repo = MenuRepository()


def handle_menu_request(user_message: str, session: dict | None = None) -> str:
    """Menu isteme intentini yanit ver."""
    entities = extract_entities(user_message)
    matched_categories = entities.kategoriler or ([entities.kategori] if entities.kategori else [])

    # Update session memory
    if session is not None and matched_categories:
        session["last_categories"] = matched_categories

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


def handle_price_request(user_message: str, session: dict | None = None) -> str:
    """Fiyat sorma intentini yanit ver."""
    entities = extract_entities(user_message)
    non_food_categories = {"tatli", "kahve", "sicak_icecek", "soguk_icecek"}

    matched_categories = entities.kategoriler or ([entities.kategori] if entities.kategori else [])
    if not matched_categories and session is not None and session.get("last_categories"):
        fallback_cats = session["last_categories"]
        if entities.is_yemek:
            fallback_cats = [c for c in fallback_cats if c not in non_food_categories]
        matched_categories = fallback_cats

    if matched_categories:
        items = []
        for category in matched_categories:
            items.extend(_repo.get_recommendations(
                kategori=category,
                fiyat_min=entities.fiyat_min,
                fiyat_max=entities.fiyat_max
            ))
    else:
        items = _repo.get_by_price_range(entities.fiyat_min, entities.fiyat_max)

    if entities.is_yemek:
        items = [item for item in items if item.get("kategori") not in non_food_categories]

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

    if matched_categories:
        category_display = ", ".join(category.replace("_", " ") for category in matched_categories)
        prefix = f"{category_display.upper()} ICIN {price_info} FIYAT ARALIGINDA ONERILER:\n"
    else:
        if entities.is_yemek:
            prefix = f"{price_info} YEMEK SECENEKLERI ICIN ONERILER:\n"
        else:
            prefix = f"{price_info} FIYAT ARALIGINDA ONERILER:\n"

    menu_text = _repo.format_items_as_text(items)
    return prefix + menu_text


def handle_allergen_request(user_message: str, session: dict | None = None) -> str:
    """Alerjen oneri intentini yanit ver."""
    entities = extract_entities(user_message)
    non_food_categories = {"tatli", "kahve", "sicak_icecek", "soguk_icecek"}

    matched_categories = entities.kategoriler or ([entities.kategori] if entities.kategori else [])
    if not matched_categories and session is not None and session.get("last_categories"):
        fallback_cats = session["last_categories"]
        if entities.is_yemek:
            fallback_cats = [c for c in fallback_cats if c not in non_food_categories]
        matched_categories = fallback_cats

    if not entities.alerjenler:
        return "Alerjen bilgisi yakalanamadi. Lutfen hangi alerjenlerden kacmak istediginizi belirtin."

    allergen_display = ", ".join(entities.alerjenler)
    items = _repo.get_safe_for_allergens(entities.alerjenler)

    if entities.is_yemek:
        items = [item for item in items if item.get("kategori") not in non_food_categories]

    if not matched_categories:
        prefix = f"{allergen_display} alerjisi icin GUVENLI YEMEK SECENEKLERI:\n" if entities.is_yemek else f"{allergen_display} alerjisi icin GUVENLI SECENEKLER:\n"
    else:
        category_display = ", ".join(category.replace("_", " ") for category in matched_categories)
        prefix = f"{allergen_display} alerjisi icin {category_display} KATEGORI SECENEKLERI:\n"
        items = [item for item in items if item.get("kategori") in matched_categories]

    if not items:
        return f"{allergen_display} alerjisi icin bu kategoride guvenli urun bulunamadi."

    menu_text = _repo.format_items_as_text(items)
    return prefix + menu_text



def response_for_intent(intent: str, user_message: str, session: dict | None = None) -> str:
    """Niyete gore cevap uret."""
    if intent == "menu_isteme":
        return handle_menu_request(user_message, session)
    elif intent == "fiyat_sorma":
        return handle_price_request(user_message, session)
    elif intent == "alerjen_oneri_isteme":
        return handle_allergen_request(user_message, session)
    elif intent == "iletisim_saatler":
        return "ResQAI Bistro & Coffee, Kadıköy şubemizde haftanın her günü 08:00 - 23:00 saatleri arasında hizmet vermektedir. Telefon numaramız: 0216 123 45 67, Adresimiz: Caferağa Mah. Moda Cad. No: 42, Kadıköy/İstanbul."
    elif intent == "selamlasma_veda":
        return "Merhaba! Size nasıl yardımcı olabilirim? Menümüz, fiyatlarımız veya alerjen uyarıları hakkında soru sorabilirsiniz."
    elif intent == "siparis_isteme":
        return "Sipariş vermek için web sitemizdeki 'Sepete Ekle' butonlarını kullanabilir veya 0216 123 45 67 numaralı hattımızdan bize ulaşabilirsiniz."
    else:
        return DEFAULT_FALLBACK
