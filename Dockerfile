
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-production.txt .

RUN pip install --no-cache-dir -r requirements-production.txt

COPY . .

EXPOSE 10000

CMD ["sh", "-c", "uvicorn src.api:app --host 0.0.0.0 --port ${PORT:-10000}"]
