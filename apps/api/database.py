from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from config import get_settings

settings = get_settings()

# SQLAlchemyエンジン作成
_engine_kwargs = dict(
    pool_pre_ping=True,
    echo=settings.debug,
)
# SQLite用の設定
if settings.database_url.startswith("sqlite"):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
    _engine_kwargs.pop("pool_pre_ping")  # SQLiteではpool_pre_pingは不要

engine = create_engine(settings.database_url, **_engine_kwargs)

# セッションファクトリ
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ベースクラス
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """データベースセッションを取得する依存関係"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """データベースを初期化（テーブル作成）"""
    Base.metadata.create_all(bind=engine)
