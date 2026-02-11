# IMG-Quest（img-quest）
> "導入の意思決定フロー"を疑似体験し、必要設定・成果物を自動生成する Webアプリ（FI起点）

**Turn decisions into configuration.**

- 目的: 質問に答えるだけで、FI導入に必要な設定を洗い出し、依存関係つきバックログと成果物を生成
- 対象: FIコンサル育成、FI領域リードの漏れ防止、顧客キーマンの論点可視化
- 注意: 本プロジェクトはSAP社とは無関係（教育・支援用途）

## 🚀 Quickstart

### 前提条件
- Docker & Docker Compose がインストールされていること
- ポート 3000, 8001, 5433 が空いていること

### 起動手順

```bash
# 1. Docker Composeで全サービスを起動
docker compose up -d

# 2. ビルドと起動を待つ（初回は数分かかります）
# 完了したら以下のURLにアクセス

# Web UI: http://localhost:3000
# API Docs: http://localhost:8001/docs
# API Health: http://localhost:8001/health
```

### 初回セットアップ

1. ブラウザで `http://localhost:3000` を開く
2. 「新規プロジェクト作成」をクリック
3. プロジェクト情報（名前、国、通貨など）を入力
4. ウィザードで質問に回答していく
5. バックログで依存関係を確認
6. 成果物を生成してダウンロード

詳しくは [QUICKSTART.md](QUICKSTART.md) をご覧ください。

## 📚 ドキュメント

- **[クイックスタートガイド](QUICKSTART.md)** - 5分で始める
- **[仕様書](docs/SPEC.md)** - システム要件と設計
- **[カタログ](docs/CATALOGUE/fi_core.yml)** - FI設定項目マスタ

## 🏗️ アーキテクチャ

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│             │      │             │      │             │
│   Next.js   │─────▶│   FastAPI   │─────▶│ PostgreSQL  │
│  (port 3000)│      │  (port 8001)│      │  (port 5433)│
│             │      │             │      │             │
└─────────────┘      └─────────────┘      └─────────────┘
     Web UI             Backend API         Database
```

## 🗂️ リポジトリ構成

```
img-quest/
├── README.md                    # このファイル
├── QUICKSTART.md                # クイックスタートガイド
├── docker-compose.yml           # Docker Compose設定
├── docs/                        # ドキュメント
│   ├── SPEC.md                 # 仕様書
│   └── CATALOGUE/              # 設定カタログ
│       └── fi_core.yml         # FIコア設定項目
├── apps/
│   ├── api/                    # FastAPI バックエンド
│   │   ├── main.py            # アプリエントリポイント
│   │   ├── models.py          # データモデル
│   │   ├── routers/           # APIルーター
│   │   ├── services/          # ビジネスロジック
│   │   └── Dockerfile         # API用Dockerfile
│   └── web/                    # Next.js フロントエンド
│       ├── src/
│       │   ├── app/           # App Router ページ
│       │   ├── components/    # Reactコンポーネント
│       │   └── lib/           # ユーティリティ
│       └── Dockerfile         # Web用Dockerfile
```

## 🎯 主要機能

### 1. スコープ質問ウィザード
- 依存関係を考慮した質問の自動提示
- 動的フォーム（select/multiselect/text/number）
- 進捗表示とナビゲーション

### 2. 設定カタログ（Config Catalogue）
- P0（最優先）設定項目を自動展開
- YAML形式で管理可能
- 依存関係の定義

### 3. 依存関係エンジン
- `depends_on` による前提条件チェック
- READY/BLOCKED/PENDING/DONE ステータス管理
- 次に決めるべき質問の自動提示
- 推測禁止（未決定は TBD として明示）

### 4. 成果物ジェネレータ
- **Decision Log**: 決定事項の時系列記録
- **Config Workbook**: 設定一覧とステータス
- **Test View**: テスト観点
- **Migration View**: 移行オブジェクト一覧
- Markdown形式でダウンロード可能

## 🛠️ 技術スタック

### Backend
- **FastAPI** 0.110+ - 高速なPython Webフレームワーク
- **SQLAlchemy** 2.0+ - ORM
- **PostgreSQL** 16 - データベース
- **Pydantic** 2.0+ - データバリデーション
- **PyYAML** - カタログ読み込み

### Frontend
- **Next.js** 15 - React フレームワーク（App Router）
- **React** 19 - UIライブラリ
- **TypeScript** - 型安全性
- **Tailwind CSS** 3 - スタイリング
- **SWR** - データフェッチング

### Infrastructure
- **Docker** & **Docker Compose** - コンテナ化

## 🧪 開発

### API開発

```bash
cd apps/api

# 仮想環境作成
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt

# ローカル起動（開発モード）
uvicorn main:app --reload --port 8001
```

### Web開発

```bash
cd apps/web

# 依存関係インストール
npm install

# 開発サーバー起動
npm run dev
```

### カタログ編集

`docs/CATALOGUE/fi_core.yml` を編集後、APIを再起動すると反映されます。

```yaml
- id: FI-CORE-XXX
  title: 設定項目名
  priority: P0
  description: 説明
  inputs:
    - name: input_name
      type: select
      options: [OPTION1, OPTION2]
  depends_on: [FI-CORE-001]
  produces: [DECISION_LOG, CONFIG_WORKBOOK]
```

## 📝 使用例

### 1. プロジェクト作成
```
プロジェクト名: ABC社 FI導入
国: JP
通貨: JPY
業種: 製造業
```

### 2. ウィザードで回答
```
質問1: 会計年度バリアント
→ K4（4月開始）を選択

質問2: 会社コード基本情報
→ 通貨: JPY、国: JP

質問3: 期間オープン/クローズ運用
→ 締め方針: STRICT、締め日数: 5
```

### 3. 成果物生成
- Decision Log をダウンロード → 決定事項を確認
- Config Workbook をダウンロード → 設定作業一覧を確認
- Test View をダウンロード → テストケースを作成
- Migration View をダウンロード → 移行計画を策定

## 🤝 コントリビューション

本プロジェクトは教育・支援目的のオープンソースプロジェクトです。
フィードバックや改善提案を歓迎します。

## 📄 ライセンス

MIT License

## ⚠️ 免責事項

本プロジェクトはSAP社とは無関係の教育・支援用途のツールです。
実際の導入プロジェクトでは、必ず専門家の助言を得てください。
