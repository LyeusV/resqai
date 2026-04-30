from __future__ import annotations

from .entities import extract_entities
from .repository import MenuRepository

DEFAULT_FALLBACK = "Bunu tam anlayamadim. Farkli bir sekilde sorabilir misiniz?"

# Repository ornegi
_repo = MenuRepository()


def handle_menu_request(user_message: str) -> str:
    """Menu isteme intentini yanit ver."""
    entities = extract_entities(user_message)

    # Kategori varsa ona gore filtrele, yoksa tum menuyu goster
    if entities.kategori:
        items = _repo.get_by_category(entities.kategori)
        category_display = entities.kategori.replace("_", " ")
        prefix = f"{category_display.upper()} SECENEKLERI:\n"
    else:
        items = _repo.get_all_items()
        prefix = "TÜNN MENU:\n"

    if not items:
        return "Bu kategoride urun bulunamadi."

    menu_text = _repo.format_items_as_text(items)
    return prefix + menu_text


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

    if not entities.alerjenler:
        return "Alerijen bilgisi yakalanamamistir. Lutfen hangi alerjenlerden kacmak istediginizi belirtin."

    allergen_display = ", ".join(entities.alerjenler)
    items = _repo.get_safe_for_allergens(entities.alerjenler)

    if not entities.kategori:
        prefix = f"{allergen_display} alerjisi icin GUVENLI SECEEKLER:\n"
    else:
        category_display = entities.kategori.replace("_", " ")
        prefix = f"{allergen_display} alerjisi icin {category_display} KATEGORI SECENEKLERI:\n"
        items = [item for item in items if item.get("kategori") == entities.kategori]

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
