FROM node:20-alpine

WORKDIR /app

# 依存関係のインストール
COPY package.json ./
RUN npm install

# アプリケーションコードをコピー
COPY . .

# publicディレクトリを保証
RUN mkdir -p public

# Next.jsのビルド
RUN npm run build

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"
ENV NODE_ENV=production

CMD ["npm", "start"]
