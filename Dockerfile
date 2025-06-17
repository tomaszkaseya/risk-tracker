FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libsqlite3-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN if [ ! -f .env ]; then echo ".env not found, copying from example"; cp config.env.example .env; fi

ENV PYTHONUNBUFFERED=1

CMD ["python", "run.py"]