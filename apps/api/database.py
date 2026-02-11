from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from config import get_settings

settings = get_settings()

# SQLAlchemyエンジン作成
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=settings.debug
)

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
