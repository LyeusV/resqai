from __future__ import annotations


DEFAULT_FALLBACK = "Bunu tam anlayamadim. Farkli bir sekilde sorabilir misiniz?"

INTENT_RESPONSES: dict[str, str] = {
    "menu_isteme": "Menuyu paylasiyorum. Isterseniz fiyatlari da ayri olarak gosterebilirim.",
    "fiyat_sorma": "Fiyat bilgilerini paylasiyorum. Hangi urunle ilgili bilgi istiyorsunuz?",
    "alerjen_oneri_isteme": "Alerjen durumunuza uygun secenekleri kontrol edelim. Isterseniz icerik listesini baz alarak oneriler sunabilirim.",
    "masa_rezervasyonu": "Masa ayirtmak icin secim yapiniz. Tarih, saat ve kisi sayisini belirleyiniz.",
    "acilis_saatleri": "Iletisim bilgilerimiz: Pazartesi-Cuma 11:00-23:00, Cumartesi 10:00-23:30, Pazar 10:00-22:00",
    "iletisim": "Bize ulasmak icin: Tel: +90 212 123 4567, Adres: Kadikoy, Istanbul",
    "odeme_yontemi": "Nakit, Kredi Karti, Debit Karti, Mobil Odeme ve EFT kabul ediyoruz.",
}


def response_for_intent(intent: str) -> str:
    return INTENT_RESPONSES.get(intent, DEFAULT_FALLBACK)
