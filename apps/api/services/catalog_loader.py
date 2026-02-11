import yaml
from pathlib import Path
from typing import List, Dict, Any
import logging
from database import SessionLocal
import crud

logger = logging.getLogger(__name__)


def load_catalog_file(catalog_path: str) -> List[Dict[str, Any]]:
    """
    YAMLカタログファイルを読み込む
    
    Args:
        catalog_path: カタログファイルのパス
        
    Returns:
        設定項目のリスト
    """
    try:
        path = Path(catalog_path)
        if not path.exists():
            logger.error(f"Catalog file not found: {catalog_path}")
            return []
        
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not isinstance(data, list):
            logger.error(f"Invalid catalog format: expected list, got {type(data)}")
            return []
        
        logger.info(f"Loaded {len(data)} config items from catalog")
        return data
    
    except Exception as e:
        logger.error(f"Error loading catalog: {e}")
        return []


def normalize_config_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    カタログアイテムをDBスキーマに正規化
    
    Args:
        item: YAMLから読み込んだアイテム
        
    Returns:
        正規化されたアイテム
    """
    return {
        'id': item.get('id'),
        'title': item.get('title', ''),
        'description': item.get('description', ''),
        'priority': item.get('priority', 'P1'),
        'inputs': item.get('inputs', []),
        'depends_on': item.get('depends_on', []),
        'produces': item.get('produces', []),
        'notes': item.get('notes', []),
        # 初心者モード対応
        'beginner_mode': item.get('beginner_mode', True),
        'beginner_title': item.get('beginner_title'),
        'beginner_description': item.get('beginner_description'),
        'beginner_why': item.get('beginner_why')
    }


def load_catalog(catalog_path: str = None) -> int:
    """
    カタログをデータベースにロード
    
    Args:
        catalog_path: カタログファイルのパス（省略時は設定から取得）
        
    Returns:
        ロードされた項目数
    """
    if catalog_path is None:
        from config import get_settings
        settings = get_settings()
        catalog_path = settings.catalog_path
    
    # カタログファイルを読み込み
    items = load_catalog_file(catalog_path)
    if not items:
        logger.warning("No config items loaded from catalog")
        return 0
    
    # データベースに保存
    db = SessionLocal()
    try:
        count = 0
        for item in items:
            try:
                normalized = normalize_config_item(item)
                if not normalized['id']:
                    logger.warning(f"Skipping item without id: {item}")
                    continue
                
                crud.upsert_config_item(db, normalized)
                count += 1
            except Exception as e:
                logger.error(f"Error saving config item {item.get('id')}: {e}")
        
        logger.info(f"Successfully loaded {count} config items into database")
        return count
    
    finally:
        db.close()


def get_catalog_stats() -> Dict[str, Any]:
    """
    カタログの統計情報を取得
    
    Returns:
        統計情報（総数、優先度別など）
    """
    db = SessionLocal()
    try:
        items = crud.get_config_items(db)
        
        stats = {
            'total': len(items),
            'by_priority': {},
            'ids': [item.id for item in items]
        }
        
        for item in items:
            priority = item.priority or 'UNKNOWN'
            stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
        
        return stats
    
    finally:
        db.close()
