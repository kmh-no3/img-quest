#!/usr/bin/env python3
"""
ConfigItemsテーブルにbeginner関連カラムを追加するマイグレーションスクリプト
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
        # beginner_modeカラムが存在するかチェック
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='config_items' AND column_name='beginner_mode'
        """))
        
        if result.fetchone():
            logger.info("Beginner columns already exist. Skipping migration.")
            return
        
        logger.info("Adding beginner columns to config_items table...")
        
        # カラムを追加
        conn.execute(text("""
            ALTER TABLE config_items 
            ADD COLUMN beginner_mode BOOLEAN DEFAULT TRUE,
            ADD COLUMN beginner_title VARCHAR(255),
            ADD COLUMN beginner_description TEXT,
            ADD COLUMN beginner_why TEXT
        """))
        conn.commit()
        
        logger.info("Migration completed successfully!")

if __name__ == "__main__":
    migrate()
