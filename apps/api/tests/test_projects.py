"""
Projects APIのテスト
"""
import pytest


class TestProjectsCRUD:
    """プロジェクトのCRUD操作テスト"""

    def test_create_project(self, client):
        """プロジェクトを作成できること"""
        response = client.post("/api/projects/", json={
            "name": "テストプロジェクト",
            "mode": "EXPERT",
            "country": "JP",
            "currency": "JPY",
            "industry": "manufacturing",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "テストプロジェクト"
        assert data["mode"] == "EXPERT"
        assert data["country"] == "JP"
        assert data["id"] is not None

    def test_create_project_beginner_mode(self, client):
        """ビギナーモードでプロジェクトを作成できること"""
        response = client.post("/api/projects/", json={
            "name": "初心者プロジェクト",
            "mode": "BEGINNER",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["mode"] == "BEGINNER"

    def test_list_projects(self, client):
        """プロジェクト一覧を取得できること"""
        # プロジェクトを作成
        client.post("/api/projects/", json={"name": "Project 1"})
        client.post("/api/projects/", json={"name": "Project 2"})

        response = client.get("/api/projects/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_project(self, client):
        """プロジェクト詳細を取得できること"""
        create_response = client.post("/api/projects/", json={
            "name": "詳細テスト",
        })
        project_id = create_response.json()["id"]

        response = client.get(f"/api/projects/{project_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "詳細テスト"
        assert "total_questions" in data
        assert "backlog_ready" in data

    def test_get_project_not_found(self, client):
        """存在しないプロジェクトにアクセスすると404になること"""
        response = client.get("/api/projects/99999")
        assert response.status_code == 404

    def test_update_project(self, client):
        """プロジェクトを更新できること"""
        create_response = client.post("/api/projects/", json={
            "name": "更新前",
        })
        project_id = create_response.json()["id"]

        response = client.put(f"/api/projects/{project_id}", json={
            "name": "更新後",
            "country": "US",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "更新後"
        assert data["country"] == "US"

    def test_delete_project(self, client):
        """プロジェクトを削除できること"""
        create_response = client.post("/api/projects/", json={
            "name": "削除テスト",
        })
        project_id = create_response.json()["id"]

        delete_response = client.delete(f"/api/projects/{project_id}")
        assert delete_response.status_code == 204

        # 削除後にアクセスすると404
        get_response = client.get(f"/api/projects/{project_id}")
        assert get_response.status_code == 404


class TestProjectBacklogInitialization:
    """プロジェクト作成時のバックログ初期化テスト"""

    def test_p0_items_added_on_creation(self, client):
        """プロジェクト作成時にP0項目がバックログに追加されること"""
        create_response = client.post("/api/projects/", json={
            "name": "バックログテスト",
        })
        project_id = create_response.json()["id"]

        backlog_response = client.get(f"/api/projects/{project_id}/backlog")
        assert backlog_response.status_code == 200
        items = backlog_response.json()

        # P0が8項目あるはず
        assert len(items) >= 8

    def test_p1_items_added_conditionally(self, client):
        """P1項目が条件に応じて追加されること"""
        create_response = client.post("/api/projects/", json={
            "name": "P1テスト",
            "country": "JP",
            "industry": "manufacturing",
        })
        project_id = create_response.json()["id"]

        backlog_response = client.get(f"/api/projects/{project_id}/backlog")
        items = backlog_response.json()

        # P0(8) + P1項目が含まれるはず
        assert len(items) > 8
