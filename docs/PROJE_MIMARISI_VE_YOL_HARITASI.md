# ResQAI - Proje Mimarisi ve Yol Haritasi

Bu dokuman, projeyi sifirdan devralan bir insanin da bir yapay zeka ajaninin da hizla anlayabilmesi icin hazirlandi.
Amac, mevcut sistemi netlestirmek, paylastigin spesifikasyon ile karsilastirmak ve sonraki adimlari tek yerde toplamak.

## 1) Proje Amaci

ResQAI, restoran/coffee shop odakli bir task-oriented chatbot projesidir.
Sistemin temel hedefleri:

- Kullanicinin niyetini siniflandirmak (intent classification)
- Menu bilgisini paylasmak
- Fiyat sorularini yanitlamak
- Alerjen kisitlarina gore guvenli secenek onermek

Kisa vadeli hedef:

- Modeli lokal veri ile egitmek
- Modelden anlamli intent tahmini alip uygun cevap dondurmek
- Tum sistemi Docker icinde calistirmak

## 2) Teknik Ilkeler ve Kisıtlar

Bu projede kabul edilen teknik cerceve:

- Harici LLM API yok (OpenAI, Gemini vb. kullanilmiyor)
- Derin ogrenme yok (LSTM/Transformer yok)
- Geleneksel ML + rule-based yaklasim
- Python tabanli backend
- Veritabani yerine lokal dosyalar (CSV/JSON)

## 3) Mevcut Durum (Neler Bitti?)

Asagidaki bolumler aktif durumda:

- Intent modeli:
  - TfidfVectorizer (1-2 gram) + LogisticRegression
  - Dataset: dataset/dataset.csv
  - Model cikti dosyasi: models/intent_model.joblib
- Egitim pipeline:
  - Train/test split + classification report
- API katmani:
  - FastAPI ile /health ve /chat endpointleri
- Docker-first calisma:
  - Dockerfile + docker-compose ile calisiyor
- Ornek menu donusu:
  - menu_isteme intentinde ornek coffee menu metni donduruluyor

En son alinan metrik (paylasilan ciktiya gore):

- Accuracy: 0.92
- Macro F1: 0.92
- Class F1:
  - alerjen_oneri_isteme: 0.91
  - fiyat_sorma: 0.96
  - menu_isteme: 0.89

Bu skorlar mevcut veri dagilimi icin baseline ustunde iyi bir seviyededir.

## 4) Spesifikasyon ile Karsilastirma

### 4.1 Uyumlu Olanlar

- Task-oriented mimari hedefiyle uyumlu
- Geleneksel ML (scikit-learn) kullanimi uyumlu
- Intent siniflari uyumlu:
  - menu_isteme
  - fiyat_sorma
  - alerjen_oneri_isteme
- Lokal dosya temelli ilerleme uyumlu

### 4.2 Kismi Uyumlu Olanlar

- On isleme:
  - Kucuk harfe cevirme vectorizer tarafinda var
  - Noktalama temizligi su anda acik/ayri bir adim olarak yok
- Bilgi bankasi:
  - Menu su anda Python icinde statik metin olarak var
  - Hedefte menu.json tabanli sorgu/filtreleme isteniyor

### 4.3 Henuz Eksik Olanlar

- Entity extraction modulu (keyword/regex)
- menu.json semasina dayali gercek filtreleme mantigi
- Alerjen bazli dinamik sorgu + cevap uretimi
- Intent confidence esigi ve fallback stratejisi
- Egitim metriklerini kalici loglama

## 5) Hedef Mimarinin Net Tanimı

Hedef mimari asagidaki akisla calisacak:

1. Girdi Alimi ve On Isleme
- Kullanici metni normalize edilir (kucuk harf, noktalama temizligi, bosluk duzenleme)

2. Vektorization
- TfidfVectorizer ile ozellik cikarimi

3. Intent Classification
- LogisticRegression (veya alternatif: LinearSVC / MultinomialNB)

4. Entity Extraction (Rule-based)
- Regex + keyword listeleri ile parametre yakalama
- Ornek varliklar:
  - kategori: tatli, icecek, ana_yemek
  - alerjen: fistik, gluten, sut, yumurta vb.

5. Veri Sorgusu (Lokal JSON)
- menu.json dosyasi uzerinde filtreleme
- Ornek kosul:
  - kategori == "tatli"
  - "fistik" not in alerjenler

6. Yanit Uretimi
- Sablon tabanli, niyete gore dinamik metin

## 6) Onerilen Dosya Yapisı (Hedef)

Asagidaki yapi, mevcut projeyi bozmadan gelistirme icin onerilir:

- dataset/
  - dataset.csv
- data/
  - menu.json
  - entity_lexicon.json (opsiyonel)
- src/resqai/
  - api.py
  - model.py
  - train.py
  - preprocess.py
  - entities.py
  - rules.py
  - repository.py
  - responses.py

Not: Gercek veritabani su an hedef degil. Lokal JSON/CSV ile devam edilecek.

## 7) Kisa Vadeli Uygulama Plani

Asama 1 - Stabil MVP (simdi)

- Mevcut model + API akisini koru
- menu.json dosyasini ekle
- responses tarafinda static menu yerine JSON sorgusu kullan

Asama 2 - Rule-based zenginlestirme

- entities.py ile alerjen/kategori cikarimi
- alerjen_oneri_isteme niyetinde filtrelenmis liste don
- fiyat_sorma niyetinde urun bazli fiyat yakalama

Asama 3 - Kalite guvencesi

- Unit test sayisini artir
- Dataset kalite kontrolu (tekrarlanan/supheli etiket)
- Model metrik logu (her egitimde tarih + skor)

## 8) Orta/Uzun Vadeli Yol Haritasi

Frontend:

- React ile web arayuzu gelistirilecek
- Chat kutusu + intent sonucu + onerilen urun listesi gosterilecek

Backend:

- Ana backend tercihi FastAPI olarak sabitlendi
- Django (veya Django + DRF) su an icin alternatif secenek olarak tutuluyor
- Django gecisi kesin plan degil; yalnizca ileride teknik/urun ihtiyaci olursa degerlendirilecek

Yayin:

- Hedef: gercek web sitesi olarak yayina almak
- Planlanan alan adi: resqai.lyeusv.com
- Onerilen temel adimlar:
  - Reverse proxy (Nginx)
  - HTTPS (Let's Encrypt)
  - Docker tabanli deployment
  - CI/CD (ileride)

## 9) Mimari Kararlar (Netlestirilmis)

- LLM API yok
- Deep learning yok
- ML + Rule-based hibrit mimari
- Veri kaynagi olarak lokal CSV + JSON
- Ana backend FastAPI (Django yalnizca alternatif)
- Kisa vadede egitim + dogru cevap uretimi odak
- Uzun vadede React arayuz + canli domain yayini

## 10) Bu Dokumanin Kullanimi

Yeni bir kisi veya ajan projeye girdiginde once bu dosyayi okumali.
Bu dosya, su sorularin toplu cevabini verir:

- Proje ne amacli?
- Su an ne tamamlandi?
- Hedef mimari ne?
- Eksik parcilar neler?
- Hangi sira ile ilerlenmeli?

Bu dokuman yasayan bir dosyadir; her mimari karar degisikliginde guncellenmelidir.
