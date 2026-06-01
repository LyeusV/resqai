# ResQAI

Türkçe restoran/coffee shop chatbotu. Task-oriented NLP, intent sınıflandırması + rule-based varlık çıkarımı.

Detaylı teknik dokuman ve yol haritası için: [docs/PROJE_MIMARISI_VE_YOL_HARITASI.md](docs/PROJE_MIMARISI_VE_YOL_HARITASI.md)

## Temel Özellikler

- **Intent Sınıflandırması:** TF-IDF + Logistic Regression (Accuracy 92%)
- **Varlık Çıkarımı:** Alerjen, kategori, fiyat (keyword/regex-based)
- **Menu Repository:** JSON-based sorgu ve filtreleme
- **Dinamik Cevaplar:** Şablon tabanlı yanıtlar, kullanıcı girişine göre özelleştirilmiş
- **Kalite Güvencesi:** Dataset analiz, training metrik logging, birim testler
- **Frontend:** React + Vite chat arayüzü

## Dosya Yapısı

- `src/resqai/train.py` - Model eğitimi + metrik logu
- `src/resqai/api.py` - FastAPI endpoints (/health, /chat)
- `src/resqai/entities.py` - Rule-based varlık çıkarımı
- `src/resqai/repository.py` - Menu JSON sorgulama
- `src/resqai/responses.py` - Dinamik cevap üretimi
- `src/resqai/metrics.py` - Training metrik logu (metrics.jsonl)
- `src/resqai/dataset_quality.py` - Dataset kalite analizi
- `data/menu.json` - Menu bilgi bankası
- `dataset/dataset.csv` - Eğitim verisi
- `training_logs/metrics.jsonl` - Egitim metrikleri
- `frontend/` - React/Vite web arayüzü

## Hızlı Başlangıç

### Docker Compose (Dev)

```bash
docker compose up --build
```

Bu komut hem backend API'yi hem de React frontend'i ayağa kaldırır:

- API: http://localhost:8000
- Frontend: http://localhost:5173

### Model Eğitimi

```bash
docker exec resqai-api python -m resqai.train
```

### Dataset Kalite Analizi

```bash
docker exec resqai-api python -m resqai.dataset_quality
```
### Unit & Entegrasyon Testleri

```bash
docker exec resqai-api pytest
```

### API Sorgusu

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tatlı menüsü neler?"}'
```

Örnek Çıktı:
```json
{
  "message": "Tatlı menüsü neler?",
  "intent": "menu_isteme",
  "reply": "TATLI SECENEKLERI:\n- San Sebastian: 170 TL\n- Brownie: 145 TL\n- Vegan Hurmali Toplar: 130 TL"
}
```

### Frontend Kullanımı

`frontend/` klasörüne girip bağımsız olarak da çalıştırabilirsin:

```bash
cd frontend
npm install
npm run dev
```

Tarayıcıdan açılacak ekran, chat geçmişini gösterir ve hızlı prompt butonlarıyla test yapmanı sağlar.

## Veri Seti Genişletme

`dataset/dataset.csv` dosyasına yeni örnekler ekleyin (CSV format):

```csv
metin,niyet
Menüde neler var?,menu_isteme
Hamburger ne kadar?,fiyat_sorma
Fıstık alerjim var, ne önerir misiniz?,alerjen_oneri_isteme
```

3 Ana Intent Sınıfı:

- `menu_isteme` - Menu, yemek listesi, seçenekler
- `fiyat_sorma` - Fiyat ve ücretlendirilme soruları
- `alerjen_oneri_isteme` - Allerji, diyetsel tercihler, malzeme bilgileri

Yeniden eğitmek için:

```bash
docker exec resqai-api python -m resqai.train
```


