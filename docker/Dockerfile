FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml .
COPY src ./src
RUN pip install --no-cache-dir -e .[dev]

COPY . .

RUN mkdir -p models

EXPOSE 8000

CMD ["sh", "-c", "if [ ! -f models/intent_model.joblib ]; then python -m resqai.train; fi && uvicorn resqai.api:app --host 0.0.0.0 --port 8000"]
