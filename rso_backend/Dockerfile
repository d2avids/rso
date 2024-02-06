FROM python:3.10-alpine
WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "5", "rso_backend.wsgi"]
