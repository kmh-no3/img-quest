"""
テスト用のフィクスチャと設定

SQLiteのインメモリDBを使ってテストを高速に実行する。
"""
import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# テスト用の設定を環境変数で上書き
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["CATALOG_PATH"] = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "docs", "CATALOGUE", "fi_core.yml"
)

from database import Base
from main import app
from database import get_db


# テスト用SQLiteエンジン
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """テスト用のDBセッションを提供"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db_session():
    """
    各テスト関数ごとにクリーンなDBセッションを提供

    テーブルを毎回再作成してテスト間の副作用を防ぐ
    """
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPIのテストクライアント"""
    from fastapi.testclient import TestClient
    with TestClient(app) as c:
        yield c
