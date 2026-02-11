from sqlalchemy.orm import Session
from typing import List, Set, Dict, Optional
import logging
import crud
import models

logger = logging.getLogger(__name__)


class DependencyEngine:
    """
    依存関係エンジン
    
    設定項目の依存関係を管理し、次に回答すべき質問を提示する
    """
    
    def __init__(self, db: Session, project_id: int, mode_filter: str = None):
        self.db = db
        self.project_id = project_id
        self.mode_filter = mode_filter
        self._load_state()
    
    def _load_state(self):
        """現在の状態を読み込む"""
        # プロジェクトの回答を取得
        self.answers = crud.get_answers(self.db, self.project_id)
        
        # 回答済みの設定項目IDセット
        self.answered_config_ids: Set[str] = set(
            answer.config_item_id for answer in self.answers
        )
        
        # バックログアイテムを取得
        self.backlog_items = crud.get_backlog_items(self.db, self.project_id)
        
        # 設定項目マスタを取得
        self.config_items = {
            item.id: item 
            for item in crud.get_config_items(self.db)
        }
    
    def is_dependency_satisfied(self, config_item_id: str, _visited: Set[str] = None) -> bool:
        """
        依存関係が満たされているかチェック
        
        初心者モードでは、beginner_mode=false の依存先はスキップするが、
        スキップした項目自身の依存関係は引き継いで再帰的にチェックする。
        
        例: FI-APAR-003 → FI-APAR-001(skip) → FI-CORE-002(check)
        
        Args:
            config_item_id: チェックする設定項目ID
            _visited: 循環参照防止用（内部使用）
            
        Returns:
            全ての依存が満たされている場合True
        """
        if _visited is None:
            _visited = set()
        if config_item_id in _visited:
            return True  # 循環参照を防止
        _visited.add(config_item_id)
        
        config_item = self.config_items.get(config_item_id)
        if not config_item:
            return False
        
        depends_on = config_item.depends_on or []
        
        for dep_id in depends_on:
            if dep_id in self.answered_config_ids:
                continue
            
            # 初心者モードでは beginner_mode=false の依存先をスキップ
            # ただし、スキップした項目の依存関係は引き継いでチェック
            if self.mode_filter == 'BEGINNER':
                dep_item = self.config_items.get(dep_id)
                if dep_item and not dep_item.beginner_mode:
                    # スキップする項目の依存関係を再帰チェック
                    if not self.is_dependency_satisfied(dep_id, _visited):
                        return False
                    continue
            
            return False
        
        return True
    
    def get_blocking_dependencies(self, config_item_id: str) -> List[str]:
        """
        ブロックしている依存項目のIDリストを取得
        
        Args:
            config_item_id: チェックする設定項目ID
            
        Returns:
            未回答の依存項目IDリスト
        """
        config_item = self.config_items.get(config_item_id)
        if not config_item:
            return []
        
        depends_on = config_item.depends_on or []
        
        return [
            dep_id 
            for dep_id in depends_on 
            if dep_id not in self.answered_config_ids
        ]
    
    def update_backlog_statuses(self):
        """
        バックログアイテムのステータスを更新
        
        - 回答済み → DONE
        - 依存関係満たされている → READY
        - 依存関係満たされていない → BLOCKED
        """
        for item in self.backlog_items:
            new_status = None
            new_answered = item.config_item_id in self.answered_config_ids
            
            if new_answered and item.status != models.BacklogStatus.DONE:
                new_status = models.BacklogStatus.DONE
            elif not new_answered:
                if self.is_dependency_satisfied(item.config_item_id):
                    if item.status != models.BacklogStatus.READY:
                        new_status = models.BacklogStatus.READY
                else:
                    if item.status != models.BacklogStatus.BLOCKED:
                        new_status = models.BacklogStatus.BLOCKED
            
            # 更新が必要な場合のみ更新
            if new_status or item.answered != new_answered:
                item.answered = new_answered
                if new_status:
                    item.status = new_status
                self.db.commit()
    
    def get_next_questions(self, limit: int = 5, mode_filter: str = None) -> List[models.ConfigItem]:
        """
        次に回答すべき質問を取得
        
        Args:
            limit: 取得する質問の最大数
            mode_filter: モードフィルタ（'BEGINNER' の場合は beginner_mode=True のみ）
            
        Returns:
            次に回答すべき設定項目のリスト（優先度順）
        """
        # READYステータスのバックログアイテムを取得
        ready_items = [
            item for item in self.backlog_items 
            if item.status == models.BacklogStatus.READY and not item.answered
        ]
        
        # 設定項目を取得して優先度でソート
        next_items = []
        for item in ready_items:
            config_item = self.config_items.get(item.config_item_id)
            if config_item:
                # モードフィルタ適用
                if mode_filter == 'BEGINNER':
                    # 初心者モードでは beginner_mode=True のみ
                    if not config_item.beginner_mode:
                        continue
                next_items.append(config_item)
        
        # 優先度でソート（P0 > P1 > ...）
        priority_order = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
        next_items.sort(
            key=lambda x: (
                priority_order.get(x.priority or 'P3', 99),
                x.id
            )
        )
        
        return next_items[:limit]
    
    def get_dependency_graph(self) -> Dict[str, any]:
        """
        依存関係グラフを取得（フロントエンド用）
        
        Returns:
            ノードとエッジを含むグラフデータ
        """
        nodes = []
        edges = []
        
        for item in self.backlog_items:
            config_item = self.config_items.get(item.config_item_id)
            if not config_item:
                continue
            
            # ノード作成
            nodes.append({
                'id': config_item.id,
                'label': config_item.title,
                'priority': config_item.priority,
                'status': item.status.value,
                'answered': item.answered
            })
            
            # エッジ作成（依存関係）
            for dep_id in (config_item.depends_on or []):
                edges.append({
                    'from': dep_id,
                    'to': config_item.id
                })
        
        return {
            'nodes': nodes,
            'edges': edges
        }
    
    def expand_backlog_from_answer(self, config_item_id: str):
        """
        回答に基づいてバックログを展開
        
        特定の回答により、新しい設定項目が必要になる場合がある
        （現在のMVPでは全てのP0項目を最初から追加しているため、
        この機能は将来の拡張用）
        
        Args:
            config_item_id: 回答された設定項目ID
        """
        # 将来の拡張: 回答の内容に応じて新しい設定項目を追加
        # 例: 外貨使用を選択した場合、為替関連の設定を追加
        pass


def update_project_backlog(db: Session, project_id: int, mode_filter: str = None):
    """
    プロジェクトのバックログステータスを更新
    
    Args:
        db: データベースセッション
        project_id: プロジェクトID
        mode_filter: モードフィルタ（'BEGINNER' / 'EXPERT'）
    """
    engine = DependencyEngine(db, project_id, mode_filter=mode_filter)
    engine.update_backlog_statuses()


def get_next_questions_for_project(db: Session, project_id: int, limit: int = 5, mode_filter: str = None) -> List[models.ConfigItem]:
    """
    プロジェクトの次の質問を取得
    
    Args:
        db: データベースセッション
        project_id: プロジェクトID
        limit: 取得する質問の最大数
        mode_filter: モードフィルタ（'BEGINNER' / 'EXPERT'）
        
    Returns:
        次に回答すべき設定項目のリスト
    """
    engine = DependencyEngine(db, project_id, mode_filter=mode_filter)
    engine.update_backlog_statuses()
    return engine.get_next_questions(limit, mode_filter)


def get_dependency_graph_for_project(db: Session, project_id: int, mode_filter: str = None) -> Dict[str, any]:
    """
    プロジェクトの依存関係グラフを取得
    
    Args:
        db: データベースセッション
        project_id: プロジェクトID
        mode_filter: モードフィルタ（'BEGINNER' / 'EXPERT'）
        
    Returns:
        グラフデータ
    """
    engine = DependencyEngine(db, project_id, mode_filter=mode_filter)
    engine.update_backlog_statuses()
    return engine.get_dependency_graph()
