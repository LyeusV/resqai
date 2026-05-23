from __future__ import annotations

import re

# Turkish lowercase character mappings
TURKISH_LOWER_MAP = {
    "I": "ı",
    "İ": "i",
    "Ş": "ş",
    "Ç": "ç",
    "Ğ": "ğ",
    "Ü": "ü",
    "Ö": "ö",
}

# Suffixes ordered roughly by descending length to match composite suffixes first
SUFFIXES = [
    # 5-letter suffixes
    "sınız", "siniz", "sunuz", "sünüz",
    # 4-letter suffixes
    "ımız", "imiz", "umuz", "ümüz",
    "ınız", "iniz", "unuz", "ünüz",
    "ları", "leri",
    # 3-letter suffixes
    "mız", "miz", "muz", "müz",
    "nız", "niz", "nuz", "nüz",
    "dan", "den", "tan", "ten",
    "nın", "nin", "nun", "nün",
    "nda", "nde",
    "lar", "ler",
    "tır", "tir", "tur", "tür",
    "dır", "dir", "dur", "dür",
    "sın", "sin", "sun", "sün",
    "yız", "yiz", "yuz", "yüz",
    "ıcı", "ici", "ucu", "ücü",
    # 2-letter suffixes
    "da", "de", "ta", "te",
    "ya", "ye",
    "yı", "yi", "yu", "yü",
    "ın", "in", "un", "ün",
    "ım", "im", "um", "üm",
    "sı", "si", "su", "sü",
    "cı", "ci", "cu", "cü",
    "mı", "mi", "mu", "mü",
    "ız", "iz", "uz", "üz",
    # 1-letter suffixes
    "a", "e", "ı", "i", "u", "ü", "n", "s"
]

def turkish_lowercase(text: str) -> str:
    """Turkce karakterleri dogru sekilde kucuk harfe cevirir."""
    for upper_char, lower_char in TURKISH_LOWER_MAP.items():
        text = text.replace(upper_char, lower_char)
    return text.lower()

def clean_punctuation(text: str) -> str:
    """Noktalama isaretlerini temizler, rakamlari ve harfleri korur."""
    # Sadece alfanumerik karakterleri ve bosluklari koru
    text = re.sub(r"[^\w\s\d]", " ", text)
    # Birden fazla boslugu tek bosluga indirge
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def stem_word(word: str) -> str:
    """Kelimenin sonundaki Turkce ekleri (kalan kok en az 3 harf olacak sekilde) temizler."""
    if len(word) <= 3:
        return word

    changed = True
    while changed and len(word) > 3:
        changed = False
        for suffix in SUFFIXES:
            if word.endswith(suffix):
                candidate = word[:-len(suffix)]
                if len(candidate) >= 3:
                    word = candidate
                    changed = True
                    break # En uzun eslesen eki sil, donguye bastan basla
    return word

def preprocess_text(text: str) -> str:
    """Metni Turkce kucuk harf yapar, noktalama isaretlerinden arindirir ve kelime koklerini bulur."""
    if not isinstance(text, str):
        return ""
    
    text = turkish_lowercase(text)
    text = clean_punctuation(text)
    
    words = text.split()
    stemmed_words = [stem_word(w) for w in words]
    return " ".join(stemmed_words)
