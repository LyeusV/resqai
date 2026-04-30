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
  - Dataset: dataset/dataset.csv (541 satir, 3 intent sinifi)
  - Model cikti dosyasi: models/intent_model.joblib
- Egitim pipeline:
  - Train/test split (80/20, random_state=42, stratified)
  - Classification report
  - Metrics logging (training_logs/metrics.jsonl)
- Rule-based varlık cikartimi (entities.py):
  - Alerjen keyword matching (fistik, gluten, sut vb.)
  - Kategori matching (kahve, soguk_icecek, yiyecek, tatli)
  - Fiyat regex-based cikarimi
- Menu repository (repository.py):
  - data/menu.json sorgulama
  - Kategori/alerjen/fiyat filtrelemeleri
  - Dinamik metin uretimi
- API katmani:
  - FastAPI ile /health ve /chat endpointleri
  - User message'ine dayali entity-driven cevaplar
- Docker-first calisma:
  - Dockerfile + docker-compose ile calisiyor
- Kalite guvencesi:
  - 24 adet birim test (entity + repository + API)
  - Dataset kalite analiz modulu (duplicates, empty values, class balance)
  - Training metrik logu (timestamp, accuracy, F1, class-wise metrics, model params)

En son alinan metrik (Asama 3 egitimi sonrasi):

- Accuracy: 0.92
- Macro F1: 0.92
- Class F1:
  - alerjen_oneri_isteme: 0.91
  - fiyat_sorma: 0.96
  - menu_isteme: 0.89
- Dataset Kalite: FAIR (210 duplicate var, ama class dagitimi dengeli)

Bu skorlar mevcut veri dagilimi icin iyi bir seviyededir.

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

- Intent confidence esigi ve fallback stratejisi
- Daha genis varlık cikartimi (ornek: kisi/grup boyutu vs.)
- Conversational context (multi-turn chat memory)

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
  - menu.json (urun bilgi bankasi)
- training_logs/
  - metrics.jsonl (egitim metrikleri, tarih+saat bazli)
- src/resqai/
  - api.py
  - model.py
  - train.py
  - preprocess.py (opsiyonel)
  - entities.py (keyword/regex extraction)
  - repository.py (menu.json sorgulama)
  - responses.py (entity-driven responses)
  - metrics.py (training metrics logging)
  - dataset_quality.py (kalite analiz)

Not: Gercek veritabani su an hedef degil. Lokal JSON/CSV ile devam edilecek.

## 7) Kisa Vadeli Uygulama Plani

Asama 1 - Stabil MVP ✅ TAMAMLANDI

- Mevcut model + API akisini koru
- menu.json dosyasini ekle (15 ornek urun)
- responses tarafinda static menu yerine JSON sorgusu kullan

Asama 2 - Rule-based zenginlestirme ✅ TAMAMLANDI

- entities.py ile alerjen/kategori cikarimi (keyword-based)
- alerjen_oneri_isteme niyetinde filtrelenmis liste don
- fiyat_sorma niyetinde urun bazli fiyat yakalama
- repository.py ile menu.json sorgulama ve filtreleme

Asama 3 - Kalite guvencesi ✅ TAMAMLANDI

- Unit test sayisini 5'den 24'e cikart (entity + repository testleri)
- Dataset kalite kontrolu modulu (dataset_quality.py)
  - Duplicate kontrol
  - Bos deger kontrol
  - Class dagitimi analizi
  - Metin uzunluk istatistikleri
  - Genel kalite skoru (GOOD/FAIR/POOR)
- Model metrik logu (metrics.py + metrics.jsonl)
  - Tarih/timestamp
  - Accuracy + macro avg metrikleri
  - Class-wise metrics (precision/recall/f1/support)
  - Dataset boyutu ve train/test split
  - Model parametreleri

## 8) Orta/Uzun Vadeli Yol Haritasi

Asama 4 - React Frontend (Siradaki)

- React ile interaktif web arayuzu
- Kullanici input alanı (mesaj kutusu)
- Response goruntuleme (intent + cevap)
- Opsiyonel: Onerilen urunlerin visual listesi
- API cagrilari (http://localhost:8000/chat POST)

Asama 5 - Deployment + Yayin

- Docker image'i production icin optimize et
- Nginx reverse proxy ile HTTPS
- resqai.lyeusv.com domain'e yayinla
- Let's Encrypt SSL sertifikasi
- CI/CD pipeline (ileride)

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
