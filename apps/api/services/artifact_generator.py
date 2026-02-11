from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict, Any
import crud
import models


class ArtifactGenerator:
    """成果物生成エンジン"""
    
    def __init__(self, db: Session, project_id: int):
        self.db = db
        self.project_id = project_id
        self._load_data()
    
    def _load_data(self):
        """必要なデータを読み込む"""
        self.project = crud.get_project(self.db, self.project_id)
        self.decisions = crud.get_decisions(self.db, self.project_id)
        self.backlog_items = crud.get_backlog_items(self.db, self.project_id)
        self.answers = crud.get_answers(self.db, self.project_id)
        
        # 設定項目マスタ
        all_config_items = crud.get_config_items(self.db)
        self.config_items = {item.id: item for item in all_config_items}
        
        # 回答済み設定項目
        self.answered_config_ids = set(answer.config_item_id for answer in self.answers)
        
        # 回答をconfig_item_id別に整理
        self.answers_by_config = {}
        for answer in self.answers:
            if answer.config_item_id not in self.answers_by_config:
                self.answers_by_config[answer.config_item_id] = []
            self.answers_by_config[answer.config_item_id].append(answer)
    
    def _count_tbd(self, content: str) -> int:
        """TBD（未決定）の数をカウント"""
        return content.count('TBD') + content.count('未決定')
    
    def generate_decision_log(self) -> str:
        """
        Decision Log（決定事項ログ）を生成
        
        全ての決定事項を時系列で記録
        """
        lines = [
            "# Decision Log（決定事項ログ）",
            "",
            f"**プロジェクト**: {self.project.name}",
            f"**生成日時**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
            "",
            "---",
            ""
        ]
        
        if not self.decisions:
            lines.append("## まだ決定事項がありません")
            lines.append("")
            lines.append("ウィザードで質問に回答すると、ここに決定事項が記録されます。")
        else:
            lines.append("## 決定事項一覧")
            lines.append("")
            
            for i, decision in enumerate(self.decisions, 1):
                config_item = self.config_items.get(decision.config_item_id)
                
                lines.append(f"### {i}. {decision.title}")
                lines.append("")
                lines.append(f"- **設定項目ID**: {decision.config_item_id}")
                if config_item:
                    lines.append(f"- **優先度**: {config_item.priority}")
                lines.append(f"- **決定日時**: {decision.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                lines.append(f"- **ステータス**: {decision.status}")
                lines.append("")
                
                if decision.rationale:
                    lines.append("**決定内容**:")
                    lines.append("")
                    lines.append(decision.rationale)
                    lines.append("")
                
                if decision.impact:
                    lines.append("**影響範囲**:")
                    lines.append("")
                    lines.append(decision.impact)
                    lines.append("")
                
                lines.append("---")
                lines.append("")
        
        return "\n".join(lines)
    
    def generate_config_workbook(self) -> str:
        """
        Config Workbook（設定作業一覧）を生成
        
        必要な設定項目を一覧表示（ID、タイトル、ステータス、依存関係）
        """
        lines = [
            "# Config Workbook（設定作業一覧）",
            "",
            f"**プロジェクト**: {self.project.name}",
            f"**生成日時**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
            "",
            "---",
            ""
        ]
        
        # サマリー
        total = len(self.backlog_items)
        done = sum(1 for item in self.backlog_items if item.status == models.BacklogStatus.DONE)
        ready = sum(1 for item in self.backlog_items if item.status == models.BacklogStatus.READY)
        blocked = sum(1 for item in self.backlog_items if item.status == models.BacklogStatus.BLOCKED)
        
        lines.append("## サマリー")
        lines.append("")
        lines.append(f"- **全設定項目数**: {total}")
        lines.append(f"- **完了**: {done} ({round(done/total*100, 1) if total > 0 else 0}%)")
        lines.append(f"- **対応可能**: {ready}")
        lines.append(f"- **ブロック中**: {blocked}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # 優先度別に整理
        items_by_priority = {}
        for item in self.backlog_items:
            config_item = self.config_items.get(item.config_item_id)
            if config_item:
                priority = config_item.priority or 'UNKNOWN'
                if priority not in items_by_priority:
                    items_by_priority[priority] = []
                items_by_priority[priority].append((item, config_item))
        
        # 優先度順に出力
        for priority in ['P0', 'P1', 'P2', 'P3']:
            if priority not in items_by_priority:
                continue
            
            lines.append(f"## 優先度: {priority}")
            lines.append("")
            lines.append("| ID | タイトル | ステータス | 依存関係 | 設定値 |")
            lines.append("|---|---|---|---|---|")
            
            for backlog_item, config_item in items_by_priority[priority]:
                status_emoji = {
                    models.BacklogStatus.DONE: "✅",
                    models.BacklogStatus.READY: "🟢",
                    models.BacklogStatus.BLOCKED: "🔴",
                    models.BacklogStatus.PENDING: "⚪"
                }.get(backlog_item.status, "❓")
                
                # 依存関係
                depends = config_item.depends_on or []
                depends_str = ", ".join(depends) if depends else "-"
                
                # 設定値
                if backlog_item.answered:
                    answers = self.answers_by_config.get(config_item.id, [])
                    value_parts = []
                    for ans in answers:
                        val = ans.value
                        if isinstance(val, list):
                            val = ", ".join(str(v) for v in val)
                        value_parts.append(f"{ans.input_name}={val}")
                    value_str = "; ".join(value_parts) if value_parts else "設定済み"
                else:
                    value_str = "**TBD（未決定）**"
                
                lines.append(
                    f"| {config_item.id} | {config_item.title} | "
                    f"{status_emoji} {backlog_item.status.value} | {depends_str} | {value_str} |"
                )
            
            lines.append("")
        
        return "\n".join(lines)
    
    def generate_test_view(self) -> str:
        """
        Test View（テスト観点）を生成
        
        各設定項目の検証ポイントを提示
        """
        lines = [
            "# Test View（テスト観点）",
            "",
            f"**プロジェクト**: {self.project.name}",
            f"**生成日時**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
            "",
            "---",
            "",
            "## テスト観点一覧",
            ""
        ]
        
        tested_count = 0
        
        for item in self.backlog_items:
            config_item = self.config_items.get(item.config_item_id)
            if not config_item:
                continue
            
            lines.append(f"### {config_item.id}: {config_item.title}")
            lines.append("")
            
            if item.answered:
                lines.append("**ステータス**: ✅ 設定済み")
                lines.append("")
                
                # テスト観点の生成
                lines.append("**テストケース**:")
                lines.append("")
                
                # 基本的なテストケースを生成
                answers = self.answers_by_config.get(config_item.id, [])
                for ans in answers:
                    lines.append(f"1. **{ans.input_name}** の設定値 `{ans.value}` が正しく反映されているか確認")
                
                # 説明から追加のテスト観点を生成
                if config_item.description:
                    lines.append(f"2. {config_item.description}に基づく動作確認")
                
                lines.append("3. 関連する画面/機能での動作確認")
                lines.append("")
                
                tested_count += 1
            else:
                lines.append("**ステータス**: ⚠️ 未決定（TBD）")
                lines.append("")
                lines.append("設定が完了後、テスト観点を生成します。")
                lines.append("")
            
            lines.append("---")
            lines.append("")
        
        # サマリーを先頭に追加
        summary = [
            "## サマリー",
            "",
            f"- **テスト対象項目数**: {tested_count}/{len(self.backlog_items)}",
            f"- **未決定項目数**: {len(self.backlog_items) - tested_count}",
            "",
            "---",
            ""
        ]
        
        lines = lines[:7] + summary + lines[7:]
        
        return "\n".join(lines)
    
    def generate_migration_view(self) -> str:
        """
        Migration View（移行観点）を生成
        
        移行が必要なオブジェクトを一覧化
        """
        lines = [
            "# Migration View（移行観点）",
            "",
            f"**プロジェクト**: {self.project.name}",
            f"**生成日時**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
            "",
            "---",
            "",
            "## 移行対象オブジェクト",
            ""
        ]
        
        migration_items = []
        
        for item in self.backlog_items:
            config_item = self.config_items.get(item.config_item_id)
            if not config_item:
                continue
            
            # MIGRATION_VIEWを生成する設定項目のみ
            produces = config_item.produces or []
            if 'MIGRATION_VIEW' not in produces:
                continue
            
            migration_items.append((item, config_item))
        
        if not migration_items:
            lines.append("移行対象のマスタデータはありません。")
        else:
            lines.append("| 設定項目 | 移行オブジェクト | ステータス | 備考 |")
            lines.append("|---|---|---|---|")
            
            for backlog_item, config_item in migration_items:
                status = "✅ 設定済み" if backlog_item.answered else "⚠️ TBD（未決定）"
                
                # 移行オブジェクト名を推定
                migration_object = self._estimate_migration_object(config_item)
                
                # 備考
                notes = []
                if backlog_item.answered:
                    answers = self.answers_by_config.get(config_item.id, [])
                    for ans in answers:
                        notes.append(f"{ans.input_name}={ans.value}")
                note_str = "; ".join(notes) if notes else "-"
                
                lines.append(
                    f"| {config_item.title} | {migration_object} | {status} | {note_str} |"
                )
        
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## 移行手順")
        lines.append("")
        lines.append("1. マスタデータの抽出（旧システム）")
        lines.append("2. データクレンジング・変換")
        lines.append("3. テストデータ投入")
        lines.append("4. 整合性確認")
        lines.append("5. 本番データ移行")
        lines.append("")
        
        return "\n".join(lines)
    
    def _estimate_migration_object(self, config_item: models.ConfigItem) -> str:
        """移行オブジェクト名を推定"""
        title_lower = config_item.title.lower()
        
        if '会社' in config_item.title:
            return '会社コードマスタ'
        elif '勘定科目' in config_item.title:
            return '勘定科目マスタ'
        elif 'bp' in title_lower or '得意先' in config_item.title or '仕入先' in config_item.title:
            return 'ビジネスパートナーマスタ'
        elif '年度' in config_item.title:
            return '会計年度設定'
        else:
            return config_item.title
    
    def generate_all(self) -> Dict[models.ArtifactType, tuple[str, int]]:
        """
        全ての成果物を生成
        
        Returns:
            {ArtifactType: (content, tbd_count)} の辞書
        """
        artifacts = {}
        
        # Decision Log
        decision_log = self.generate_decision_log()
        artifacts[models.ArtifactType.DECISION_LOG] = (
            decision_log,
            self._count_tbd(decision_log)
        )
        
        # Config Workbook
        config_workbook = self.generate_config_workbook()
        artifacts[models.ArtifactType.CONFIG_WORKBOOK] = (
            config_workbook,
            self._count_tbd(config_workbook)
        )
        
        # Test View
        test_view = self.generate_test_view()
        artifacts[models.ArtifactType.TEST_VIEW] = (
            test_view,
            self._count_tbd(test_view)
        )
        
        # Migration View
        migration_view = self.generate_migration_view()
        artifacts[models.ArtifactType.MIGRATION_VIEW] = (
            migration_view,
            self._count_tbd(migration_view)
        )
        
        return artifacts


def generate_artifacts(db: Session, project_id: int, artifact_types: List[models.ArtifactType] = None) -> List[models.Artifact]:
    """
    成果物を生成してDBに保存
    
    Args:
        db: データベースセッション
        project_id: プロジェクトID
        artifact_types: 生成する成果物の種類（Noneの場合は全て）
        
    Returns:
        生成された成果物のリスト
    """
    generator = ArtifactGenerator(db, project_id)
    all_artifacts = generator.generate_all()
    
    # 指定された種類のみフィルタ
    if artifact_types:
        all_artifacts = {k: v for k, v in all_artifacts.items() if k in artifact_types}
    
    # DBに保存
    saved_artifacts = []
    for artifact_type, (content, tbd_count) in all_artifacts.items():
        artifact = crud.create_artifact(db, project_id, artifact_type, content, tbd_count)
        saved_artifacts.append(artifact)
    
    return saved_artifacts
