from __future__ import annotations

SAMPLE_MENU_LINES: list[str] = [
    "ResQAI Coffee - Ornek Menu",
    "",
    "Kahveler:",
    "- Espresso (Single): 85 TL",
    "- Americano: 95 TL",
    "- Latte: 115 TL (sut)",
    "- Cappuccino: 110 TL (sut)",
    "- Mocha: 125 TL (sut, cikolata)",
    "",
    "Soguk Icecekler:",
    "- Iced Americano: 105 TL",
    "- Cold Brew: 120 TL",
    "- Iced Latte: 125 TL (sut)",
    "",
    "Yiyecekler:",
    "- Kruvasan: 95 TL (gluten, yumurta, sut)",
    "- Avokadolu Sandvic: 165 TL (gluten)",
    "- Ton Balikli Salata: 180 TL (balik)",
    "- Muzlu Yulaf Bowl: 150 TL (glutensiz opsiyon)",
    "",
    "Tatli:",
    "- San Sebastian: 170 TL (sut, yumurta)",
    "- Brownie: 145 TL (gluten, yumurta)",
    "- Vegan Hurmali Toplar: 130 TL (seker ilavesiz)",
    "",
    "Not: Alerjen ve sut alternatifleri (laktozsuz, badem, yulaf) icin sorabilirsiniz.",
]


def sample_menu_text() -> str:
    return "\n".join(SAMPLE_MENU_LINES)