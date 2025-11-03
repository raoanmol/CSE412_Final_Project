FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends postgresql-client && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

COPY backend/startup.sh /app/startup.sh
RUN chmod +x /app/startup.sh

EXPOSE 5000

CMD ["/app/startup.sh"]
