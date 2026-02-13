"""
依存関係エンジンのテスト
"""
import pytest
import models
import crud
from services.dependency_engine import DependencyEngine


class TestDependencyEngine:
    """DependencyEngineのユニットテスト"""

    def _setup_catalog_and_project(self, db_session):
        """ヘルパー: カタログとプロジェクトをセットアップ"""
        # カタログ項目を作成
        items_data = [
            {
                "id": "TEST-001",
                "title": "テスト項目1",
                "priority": "P0",
                "inputs": [],
                "depends_on": [],
                "produces": ["DECISION_LOG"],
            },
            {
                "id": "TEST-002",
                "title": "テスト項目2",
                "priority": "P0",
                "inputs": [],
                "depends_on": ["TEST-001"],
                "produces": ["DECISION_LOG"],
            },
            {
                "id": "TEST-003",
                "title": "テスト項目3",
                "priority": "P1",
                "inputs": [],
                "depends_on": ["TEST-001"],
                "produces": ["DECISION_LOG"],
            },
        ]
        for data in items_data:
            crud.upsert_config_item(db_session, data)

        # プロジェクト作成
        from schemas import ProjectCreate
        project = crud.create_project(
            db_session,
            ProjectCreate(name="DependencyTest", mode="EXPERT")
        )

        # バックログにP0を追加
        crud.create_backlog_item(db_session, project.id, "TEST-001")
        crud.create_backlog_item(db_session, project.id, "TEST-002")

        return project

    def test_initial_dependency_satisfied(self, db_session):
        """依存がない項目はsatisfied"""
        project = self._setup_catalog_and_project(db_session)
        engine = DependencyEngine(db_session, project.id)
        assert engine.is_dependency_satisfied("TEST-001") is True

    def test_unsatisfied_dependency(self, db_session):
        """依存が未回答の場合はunsatisfied"""
        project = self._setup_catalog_and_project(db_session)
        engine = DependencyEngine(db_session, project.id)
        assert engine.is_dependency_satisfied("TEST-002") is False

    def test_blocking_dependencies(self, db_session):
        """ブロックしている依存項目を取得"""
        project = self._setup_catalog_and_project(db_session)
        engine = DependencyEngine(db_session, project.id)
        blocking = engine.get_blocking_dependencies("TEST-002")
        assert "TEST-001" in blocking

    def test_backlog_status_update(self, db_session):
        """バックログステータスの更新"""
        project = self._setup_catalog_and_project(db_session)
        engine = DependencyEngine(db_session, project.id)
        engine.update_backlog_statuses()

        items = crud.get_backlog_items(db_session, project.id)
        status_map = {item.config_item_id: item.status for item in items}

        # TEST-001は依存なしのためREADY
        assert status_map["TEST-001"] == models.BacklogStatus.READY
        # TEST-002はTEST-001未回答のためBLOCKED
        assert status_map["TEST-002"] == models.BacklogStatus.BLOCKED

    def test_next_questions(self, db_session):
        """次の質問がREADYのもののみ返されること"""
        project = self._setup_catalog_and_project(db_session)
        engine = DependencyEngine(db_session, project.id)
        engine.update_backlog_statuses()

        next_qs = engine.get_next_questions(limit=5)
        ids = [q.id for q in next_qs]
        assert "TEST-001" in ids
        assert "TEST-002" not in ids  # BLOCKEDなので含まれない

    def test_expand_backlog_from_answer(self, db_session):
        """回答後にP1項目がバックログに展開されること"""
        project = self._setup_catalog_and_project(db_session)

        # TEST-001に回答を追加
        from schemas import AnswerCreate
        crud.create_answer(
            db_session, project.id,
            AnswerCreate(
                config_item_id="TEST-001",
                input_name="test_field",
                value="test_value"
            )
        )

        # エンジンを再構築してexpandを実行
        engine = DependencyEngine(db_session, project.id)
        engine.expand_backlog_from_answer("TEST-001")

        # TEST-003 (P1) がバックログに追加されているはず
        items = crud.get_backlog_items(db_session, project.id)
        item_ids = [item.config_item_id for item in items]
        assert "TEST-003" in item_ids

    def test_dependency_graph(self, db_session):
        """依存関係グラフが正しく構築されること"""
        project = self._setup_catalog_and_project(db_session)
        engine = DependencyEngine(db_session, project.id)
        graph = engine.get_dependency_graph()

        assert "nodes" in graph
        assert "edges" in graph
        assert len(graph["nodes"]) == 2  # P0の2項目のみバックログにある
        # TEST-002 → TEST-001のエッジ
        assert any(
            e["from"] == "TEST-001" and e["to"] == "TEST-002"
            for e in graph["edges"]
        )
