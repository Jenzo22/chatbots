# Self-Correcting Enterprise Invoice Agent
FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App
COPY pyproject.toml .
COPY src/ src/
COPY main.py .

# Persistence: mount a volume at /app/data for checkpoints
ENV DB_PATH=/app/data/checkpoints.db
ENV PYTHONPATH=/app/src
RUN mkdir -p /app/data

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "enterprise_invoice_agent.app:app", "--host", "0.0.0.0", "--port", "8000"]
