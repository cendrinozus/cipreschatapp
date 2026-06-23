FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    g++ \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN sed -i 's/\r//' entrypoint.sh && chmod +x entrypoint.sh

RUN mkdir -p uploads chroma_db

EXPOSE 5000

CMD ["./entrypoint.sh"]
