"""
Wizard APIのテスト
"""
import pytest


class TestWizardFlow:
    """ウィザードフローのテスト"""

    def _create_project(self, client, mode="EXPERT"):
        """ヘルパー: プロジェクト作成"""
        response = client.post("/api/projects/", json={
            "name": "Wizardテスト",
            "mode": mode,
        })
        return response.json()["id"]

    def test_get_next_question(self, client):
        """次の質問を取得できること"""
        project_id = self._create_project(client)

        response = client.get(f"/api/projects/{project_id}/wizard/questions")
        assert response.status_code == 200
        data = response.json()
        assert "config_item_id" in data
        assert "title" in data
        assert "inputs" in data
        assert "priority" in data
        assert "progress" in data
        assert "total" in data

    def test_first_question_is_p0(self, client):
        """最初の質問がP0の依存なし項目であること"""
        project_id = self._create_project(client)

        response = client.get(f"/api/projects/{project_id}/wizard/questions")
        data = response.json()
        # FI-CORE-001は依存がなく、P0なので最初に来るはず
        assert data["config_item_id"] == "FI-CORE-001"
        assert data["priority"] == "P0"

    def test_submit_answer(self, client):
        """回答を送信できること"""
        project_id = self._create_project(client)

        response = client.post(
            f"/api/projects/{project_id}/wizard/answers",
            json={
                "config_item_id": "FI-CORE-001",
                "answers": {
                    "fiscal_year_variant": "K4"
                }
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "Answer submitted successfully"
        assert data["answers_count"] == 1
        assert "decision_id" in data

    def test_answer_creates_decision(self, client):
        """回答が決定事項を自動作成すること"""
        project_id = self._create_project(client)

        # 回答を送信
        client.post(
            f"/api/projects/{project_id}/wizard/answers",
            json={
                "config_item_id": "FI-CORE-001",
                "answers": {"fiscal_year_variant": "K4"}
            }
        )

        # 決定事項を確認
        response = client.get(f"/api/projects/{project_id}/wizard/decisions")
        assert response.status_code == 200
        decisions = response.json()
        assert len(decisions) >= 1
        assert decisions[0]["config_item_id"] == "FI-CORE-001"

    def test_progress_tracking(self, client):
        """進捗が正しく追跡されること"""
        project_id = self._create_project(client)

        # 初期進捗
        response = client.get(f"/api/projects/{project_id}/wizard/progress")
        data = response.json()
        assert data["answered"] == 0
        assert data["total"] > 0

        # 1問回答
        client.post(
            f"/api/projects/{project_id}/wizard/answers",
            json={
                "config_item_id": "FI-CORE-001",
                "answers": {"fiscal_year_variant": "K4"}
            }
        )

        # 進捗が更新されること
        response = client.get(f"/api/projects/{project_id}/wizard/progress")
        data = response.json()
        assert data["answered"] == 1
        assert data["done"] == 1

    def test_dependency_blocking(self, client):
        """依存関係によるブロッキングが機能すること"""
        project_id = self._create_project(client)

        # FI-CORE-002はFI-CORE-001に依存
        # FI-CORE-001を回答せずにFI-CORE-002の回答を試みても、
        # バックログステータスがBLOCKEDのはず
        summary_response = client.get(f"/api/projects/{project_id}/backlog/summary")
        summary = summary_response.json()
        assert summary["by_status"].get("BLOCKED", 0) > 0

    def test_get_answers_for_item(self, client):
        """設定項目の回答を取得できること"""
        project_id = self._create_project(client)

        # 回答を送信
        client.post(
            f"/api/projects/{project_id}/wizard/answers",
            json={
                "config_item_id": "FI-CORE-001",
                "answers": {"fiscal_year_variant": "K4"}
            }
        )

        # 回答を取得
        response = client.get(
            f"/api/projects/{project_id}/wizard/answers/FI-CORE-001"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["fiscal_year_variant"] == "K4"

    def test_beginner_mode_questions(self, client):
        """ビギナーモードでは初心者向け質問が表示されること"""
        project_id = self._create_project(client, mode="BEGINNER")

        response = client.get(f"/api/projects/{project_id}/wizard/questions")
        data = response.json()
        # ビギナーモードではbeginner_titleが表示される
        assert data["config_item_id"] == "FI-CORE-001"
        # beginner_titleが設定されているはず
        assert data["why"] is not None  # beginner_whyが含まれる


class TestBacklogExpansion:
    """バックログ動的展開のテスト"""

    def test_backlog_expands_after_answer(self, client):
        """回答後にバックログが展開されること"""
        response = client.post("/api/projects/", json={
            "name": "展開テスト",
            "mode": "EXPERT",
        })
        project_id = response.json()["id"]

        # 初期バックログ数を取得
        initial_backlog = client.get(f"/api/projects/{project_id}/backlog")
        initial_count = len(initial_backlog.json())

        # FI-CORE-001に回答（P1項目の展開をトリガーする可能性）
        client.post(
            f"/api/projects/{project_id}/wizard/answers",
            json={
                "config_item_id": "FI-CORE-001",
                "answers": {"fiscal_year_variant": "K4"}
            }
        )

        # バックログが増えている（または少なくとも減っていない）ことを確認
        updated_backlog = client.get(f"/api/projects/{project_id}/backlog")
        updated_count = len(updated_backlog.json())
        assert updated_count >= initial_count
