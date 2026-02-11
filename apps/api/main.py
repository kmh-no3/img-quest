from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from database import init_db, engine, Base
from config import get_settings
from routers import projects
import logging
import traceback

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーション起動時・終了時の処理"""
    # 起動時
    logger.info("Initializing database...")
    init_db()
    
    # カタログローダーを読み込む（次のフェーズで実装）
    logger.info("Loading catalog...")
    try:
        from services.catalog_loader import load_catalog
        load_catalog()
        logger.info("Catalog loaded successfully")
    except Exception as e:
        logger.warning(f"Catalog loading skipped: {e}")
    
    yield
    
    # 終了時
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    未処理の例外をキャッチしてJSON形式で返す。
    これによりCORSミドルウェアがレスポンスヘッダーを
    正しく付与できるようになる。
    """
    logger.error(f"Unhandled exception: {exc}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# ルーター登録
app.include_router(projects.router)

# ウィザードルーター
try:
    from routers import wizard
    app.include_router(wizard.router)
except ImportError:
    logger.warning("Wizard router not available")

# バックログルーター
try:
    from routers import backlog
    app.include_router(backlog.router)
except ImportError:
    logger.warning("Backlog router not available")

# 成果物ルーター
try:
    from routers import artifacts
    app.include_router(artifacts.router)
except ImportError:
    logger.warning("Artifacts router not available")

@app.get('/health')
def health():
    """ヘルスチェック"""
    return {'status': 'ok'}


@app.get('/')
def root():
    """ルート"""
    return {
        'name': settings.app_name,
        'version': '0.1.0',
        'docs': '/docs'
    }
