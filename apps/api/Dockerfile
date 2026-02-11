FROM python:3.11-slim

WORKDIR /app

# システムパッケージの更新とPostgreSQLクライアントのインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# カタログディレクトリを作成
RUN mkdir -p /app/catalogue

# ポート公開
EXPOSE 8001

# アプリケーション起動
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
