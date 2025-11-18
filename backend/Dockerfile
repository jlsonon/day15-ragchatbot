FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY app/ ./app
COPY app/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# Use PORT from environment (Render sets this dynamically)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


