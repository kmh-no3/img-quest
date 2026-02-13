"""
Alembic マイグレーション環境設定

config.py から DATABASE_URL を取得し、models.py の Base.metadata を使って
自動マイグレーション生成を行う。
"""
import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

# アプリケーションのモデルとデータベース設定をインポート
from database import Base
from config import get_settings
import models  # noqa: F401 — models をインポートして Base.metadata にテーブルを登録

# Alembic Config オブジェクト
config = context.config

# ロギング設定
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# メタデータオブジェクト（autogenerate用）
target_metadata = Base.metadata

# DATABASE_URL を動的に設定
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)


def run_migrations_offline() -> None:
    """
    オフラインモードでマイグレーションを実行

    SQLを直接出力する（DBに接続しない）
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    オンラインモードでマイグレーションを実行

    DBに接続してマイグレーションを適用する
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
