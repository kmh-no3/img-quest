#!/bin/bash

# IMG-Quest セットアップ確認スクリプト

echo "========================================="
echo "IMG-Quest Setup Verification"
echo "========================================="
echo ""

# カラーコード
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "${RED}✗${NC} $1 (missing)"
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
        return 0
    else
        echo -e "${RED}✗${NC} $1/ (missing)"
        return 1
    fi
}

echo "1. プロジェクト構造確認"
echo "----------------------------------------"

# ルートファイル
check_file "README.md"
check_file "QUICKSTART.md"
check_file "docker-compose.yml"
check_file ".dockerignore"

echo ""

# Docsディレクトリ
check_dir "docs"
check_file "docs/SPEC.md"
check_dir "docs/CATALOGUE"
check_file "docs/CATALOGUE/fi_core.yml"

echo ""

# API
echo "2. Backend (FastAPI) 確認"
echo "----------------------------------------"
check_dir "apps/api"
check_file "apps/api/main.py"
check_file "apps/api/requirements.txt"
check_file "apps/api/Dockerfile"
check_file "apps/api/config.py"
check_file "apps/api/database.py"
check_file "apps/api/models.py"
check_file "apps/api/schemas.py"
check_file "apps/api/crud.py"
check_file "apps/api/dependencies.py"
check_dir "apps/api/routers"
check_file "apps/api/routers/projects.py"
check_file "apps/api/routers/wizard.py"
check_file "apps/api/routers/backlog.py"
check_file "apps/api/routers/artifacts.py"
check_dir "apps/api/services"
check_file "apps/api/services/catalog_loader.py"
check_file "apps/api/services/dependency_engine.py"
check_file "apps/api/services/artifact_generator.py"

echo ""

# Web
echo "3. Frontend (Next.js) 確認"
echo "----------------------------------------"
check_dir "apps/web"
check_file "apps/web/package.json"
check_file "apps/web/tsconfig.json"
check_file "apps/web/next.config.js"
check_file "apps/web/tailwind.config.js"
check_file "apps/web/Dockerfile"
check_dir "apps/web/src"
check_dir "apps/web/src/app"
check_file "apps/web/src/app/layout.tsx"
check_file "apps/web/src/app/page.tsx"
check_dir "apps/web/src/app/projects"
check_file "apps/web/src/app/projects/new/page.tsx"
check_file "apps/web/src/app/projects/[id]/page.tsx"
check_file "apps/web/src/app/projects/[id]/wizard/page.tsx"
check_file "apps/web/src/app/projects/[id]/backlog/page.tsx"
check_file "apps/web/src/app/projects/[id]/artifacts/page.tsx"
check_dir "apps/web/src/lib"
check_file "apps/web/src/lib/api-client.ts"
check_file "apps/web/src/lib/types.ts"
check_dir "apps/web/src/styles"
check_file "apps/web/src/styles/globals.css"

echo ""
echo "========================================="
echo "4. カタログ内容確認"
echo "========================================="

if [ -f "docs/CATALOGUE/fi_core.yml" ]; then
    echo "カタログアイテム数:"
    grep -c "^- id:" docs/CATALOGUE/fi_core.yml || echo "0"
    echo ""
    echo "P0アイテム:"
    grep -A1 "priority: P0" docs/CATALOGUE/fi_core.yml | grep "title:" | sed 's/  title: /  - /' || echo "  (なし)"
fi

echo ""
echo "========================================="
echo "5. 次のステップ"
echo "========================================="
echo ""
echo "セットアップ確認が完了しました！"
echo ""
echo "アプリケーションを起動するには:"
echo -e "${YELLOW}  docker compose up -d${NC}"
echo ""
echo "その後、以下のURLにアクセスしてください:"
echo "  • Web UI:   http://localhost:3000"
echo "  • API Docs: http://localhost:8001/docs"
echo ""
echo "詳細は QUICKSTART.md を参照してください。"
echo ""
