from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """アプリケーション設定"""
    
    # データベース
    database_url: str = "postgresql://postgres:postgres@db:5432/imgquest"
    
    # アプリケーション
    app_name: str = "IMG-Quest API"
    debug: bool = True
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://web:3000"]
    
    # カタログ
    catalog_path: str = "/app/catalogue/fi_core.yml"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """設定のシングルトンインスタンスを取得"""
    return Settings()
