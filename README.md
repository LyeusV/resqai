# ResQAI

Turkce bir chatbot icin ilk proje iskeleti. Simdilik elinizdeki `dataset/dataset.csv` dosyasindan intent siniflandiran hafif bir baseline var.

## Ne var?

- `src/resqai/train.py`: modeli egitir ve `models/intent_model.joblib` olarak kaydeder.
- `src/resqai/api.py`: FastAPI ile `/chat` ve `/health` endpoint'lerini acar.
- `Dockerfile`: model yoksa once egitir, sonra API'yi baslatir.
- `.gitignore`: model ciktilarini ve yerel ortam dosyalarini disarida tutar.

## Kurulum

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -e .
```

## Egitim

```bash
python -m resqai.train
```

## Calistirma

```bash
uvicorn resqai.api:app --reload
```

Ornek istek:

```bash
curl -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" -d "{\"message\": \"Bugun ne yiyorsunuz?\"}"
```

## Docker

```bash
docker build -t resqai .
docker run -p 8000:8000 resqai
```

