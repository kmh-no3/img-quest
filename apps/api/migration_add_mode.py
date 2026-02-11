#!/usr/bin/env python3
"""
既存のProjectsテーブルにmodeカラムを追加するマイグレーションスクリプト
"""
from sqlalchemy import create_engine, text
from config import get_settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

def migrate():
    """マイグレーション実行"""
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        # modeカラムが存在するかチェック
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='projects' AND column_name='mode'
        """))
        
        if result.fetchone():
            logger.info("Column 'mode' already exists. Skipping migration.")
            return
        
        logger.info("Adding 'mode' column to projects table...")
        
        # ENUM型を作成
        conn.execute(text("""
            DO $$ BEGIN
                CREATE TYPE projectmode AS ENUM ('BEGINNER', 'EXPERT');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))
        conn.commit()
        
        # カラムを追加（デフォルトはEXPERT）
        conn.execute(text("""
            ALTER TABLE projects 
            ADD COLUMN mode projectmode NOT NULL DEFAULT 'EXPERT'
        """))
        conn.commit()
        
        logger.info("Migration completed successfully!")

if __name__ == "__main__":
    migrate()
