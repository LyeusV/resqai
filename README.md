# ResQAI

Turkce bir chatbot icin ilk proje iskeleti. Simdilik elinizdeki `dataset/dataset.csv` dosyasindan intent siniflandiran hafif bir baseline var.

## Ne var?

- `src/resqai/train.py`: modeli egitir ve `models/intent_model.joblib` olarak kaydeder.
- `src/resqai/api.py`: FastAPI ile `/chat` ve `/health` endpoint'lerini acar.
- `src/resqai/menu.py`: ornek coffee menu icerigini tutar.
- `Dockerfile`: model yoksa once egitir, sonra API'yi baslatir.
- `.gitignore`: model ciktilarini ve yerel ortam dosyalarini disarida tutar.

## Calistirma

```bash
docker build -t resqai .
docker run -p 8000:8000 resqai
```

## Docker Compose (Development)

```bash
docker compose up --build
```

Volume mapping sayesinde dosyalari degistirince container otomatik reload yapıyor:
- `src/` degisiklikleri direkt container'da gorunur
- `dataset/dataset.csv` okunur ve model yeniden egitilir (manuel olarak)
- `models/` klasoru kalici hale getirilir

Ornek istek:

```bash
curl -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" -d "{\"message\": \"Bugun ne yiyorsunuz?\"}"
```

## Veri Seti Genisletme

`dataset/dataset.csv` dosyasina yeni ornekler ekleyin, her satir bir mesaj ve intent icermeli:

```csv
metin,niyet
Menude neler var?,menu_isteme
Hamburger ne kadar?,fiyat_sorma
Fistik alerjim var ne onerisiz?,alerjen_oneri_isteme
```

3 ana intent sinifi:
- `menu_isteme`: Menu, yemek listesi, seçenekler
- `fiyat_sorma`: Fiyat ve ücretlendirilme soruları
- `alerjen_oneri_isteme`: Allerji, diyetsel tercihler, malzeme bilgileri

Veri ekledikten sonra modeli yeniden egitmek icin:

```bash
docker exec resqai-api python -m resqai.train
```

