from __future__ import annotations

from .menu import sample_menu_text


DEFAULT_FALLBACK = "Bunu tam anlayamadim. Farkli bir sekilde sorabilir misiniz?"

INTENT_RESPONSES: dict[str, str] = {
    "menu_isteme": sample_menu_text(),
    "fiyat_sorma": "Fiyat bilgilerini paylasiyorum. Hangi urunun detayli fiyatini ogretmek istersiniz?",
    "alerjen_oneri_isteme": "Alerjen durumunuza uygun secenekleri kontrol edelim. Hangi alerjenlerden kacmaniz gerekiyor?",
}


def response_for_intent(intent: str) -> str:
    return INTENT_RESPONSES.get(intent, DEFAULT_FALLBACK)
