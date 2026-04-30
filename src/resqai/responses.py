from __future__ import annotations


DEFAULT_FALLBACK = "Bunu tam anlayamadim. Farkli bir sekilde sorabilir misiniz?"

INTENT_RESPONSES: dict[str, str] = {
    "menu_isteme": "Menuyu paylasiyorum. Isterseniz fiyatlari da ayri olarak gosterebilirim.",
    "fiyat_sorma": "Fiyat bilgilerini paylasiyorum. Hangi urunle ilgili bilgi istiyorsunuz?",
    "alerjen_oneri_isteme": "Alerjen durumunuza uygun secenekleri kontrol edelim. Isterseniz icerik listesini baz alarak oneriler sunabilirim.",
}


def response_for_intent(intent: str) -> str:
    return INTENT_RESPONSES.get(intent, DEFAULT_FALLBACK)
