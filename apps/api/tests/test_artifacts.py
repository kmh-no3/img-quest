"""
Artifacts APIのテスト
"""
import json
import pytest


class TestArtifactGeneration:
    """成果物生成のテスト"""

    def _create_project_with_answers(self, client):
        """ヘルパー: プロジェクト作成と回答"""
        response = client.post("/api/projects/", json={
            "name": "成果物テスト",
            "mode": "EXPERT",
        })
        project_id = response.json()["id"]

        # FI-CORE-001に回答
        client.post(
            f"/api/projects/{project_id}/wizard/answers",
            json={
                "config_item_id": "FI-CORE-001",
                "answers": {"fiscal_year_variant": "K4"}
            }
        )
        return project_id

    def test_generate_all_artifacts(self, client):
        """全成果物を生成できること"""
        project_id = self._create_project_with_answers(client)

        response = client.post(
            f"/api/projects/{project_id}/artifacts/generate",
            json={}
        )
        assert response.status_code == 201
        data = response.json()
        # 4種類の成果物が生成される
        assert len(data) == 4
        types = [a["artifact_type"] for a in data]
        assert "DECISION_LOG" in types
        assert "CONFIG_WORKBOOK" in types
        assert "TEST_VIEW" in types
        assert "MIGRATION_VIEW" in types

    def test_generate_specific_artifact(self, client):
        """指定した種類の成果物を生成できること"""
        project_id = self._create_project_with_answers(client)

        response = client.post(
            f"/api/projects/{project_id}/artifacts/generate",
            json={"artifact_types": ["DECISION_LOG"]}
        )
        assert response.status_code == 201
        data = response.json()
        assert len(data) == 1
        assert data[0]["artifact_type"] == "DECISION_LOG"

    def test_artifact_contains_tbd(self, client):
        """未回答項目がTBDとして出力されること"""
        project_id = self._create_project_with_answers(client)

        response = client.post(
            f"/api/projects/{project_id}/artifacts/generate",
            json={"artifact_types": ["CONFIG_WORKBOOK"]}
        )
        data = response.json()
        # 未回答項目があるのでTBDカウントが>0
        assert data[0]["tbd_count"] > 0
        assert "TBD" in data[0]["content"]

    def test_decision_log_content(self, client):
        """Decision Logに決定内容が含まれること"""
        project_id = self._create_project_with_answers(client)

        response = client.post(
            f"/api/projects/{project_id}/artifacts/generate",
            json={"artifact_types": ["DECISION_LOG"]}
        )
        data = response.json()
        content = data[0]["content"]
        assert "Decision Log" in content
        assert "FI-CORE-001" in content

    def test_test_view_has_specific_perspectives(self, client):
        """Test Viewに固有のテスト観点が含まれること"""
        project_id = self._create_project_with_answers(client)

        response = client.post(
            f"/api/projects/{project_id}/artifacts/generate",
            json={"artifact_types": ["TEST_VIEW"]}
        )
        data = response.json()
        content = data[0]["content"]
        # FI-CORE-001固有のテスト観点が含まれるはず
        assert "会計年度" in content
        assert "テストケース総数" in content

    def test_list_artifacts(self, client):
        """成果物一覧を取得できること"""
        project_id = self._create_project_with_answers(client)

        # まず生成
        client.post(
            f"/api/projects/{project_id}/artifacts/generate",
            json={}
        )

        # 一覧取得
        response = client.get(f"/api/projects/{project_id}/artifacts")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4

    def test_download_markdown(self, client):
        """Markdownファイルをダウンロードできること"""
        project_id = self._create_project_with_answers(client)

        client.post(
            f"/api/projects/{project_id}/artifacts/generate",
            json={}
        )

        response = client.get(
            f"/api/projects/{project_id}/artifacts/DECISION_LOG/download"
        )
        assert response.status_code == 200
        assert "text/markdown" in response.headers["content-type"]
        assert "attachment" in response.headers["content-disposition"]

    def test_export_json(self, client):
        """JSONエクスポートが有効なJSONを返すこと"""
        project_id = self._create_project_with_answers(client)

        response = client.get(
            f"/api/projects/{project_id}/artifacts/export/json"
        )
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]

        data = json.loads(response.content)
        assert "project" in data
        assert "decisions" in data
        assert "config_items" in data
        assert "summary" in data
        assert data["project"]["name"] == "成果物テスト"

    def test_export_xlsx(self, client):
        """XLSXエクスポートがバイナリを返すこと"""
        project_id = self._create_project_with_answers(client)

        response = client.get(
            f"/api/projects/{project_id}/artifacts/export/xlsx"
        )
        assert response.status_code == 200
        assert "spreadsheetml" in response.headers["content-type"]
        # XLSXファイルはPKZIPのマジックバイトで始まる
        assert response.content[:2] == b'PK'
