from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
import crud
import schemas
import models
from database import get_db
from dependencies import get_project_or_404
from services.artifact_generator import generate_artifacts, ArtifactGenerator

router = APIRouter(prefix="/api/projects/{project_id}/artifacts", tags=["artifacts"])


@router.post("/generate", response_model=List[schemas.Artifact], status_code=status.HTTP_201_CREATED)
def generate_project_artifacts(
    request: schemas.ArtifactGenerate,
    project: models.Project = Depends(get_project_or_404),
    db: Session = Depends(get_db)
):
    """
    成果物を生成
    
    指定された種類の成果物を生成してDBに保存
    artifact_typesを指定しない場合は全種類を生成
    """
    artifact_types = request.artifact_types if request.artifact_types else None
    
    artifacts = generate_artifacts(db, project.id, artifact_types)
    
    return [schemas.Artifact.model_validate(a) for a in artifacts]


@router.get("/", response_model=List[schemas.Artifact])
def get_artifacts(
    project: models.Project = Depends(get_project_or_404),
    db: Session = Depends(get_db)
):
    """プロジェクトの成果物一覧を取得"""
    artifacts = crud.get_artifacts(db, project.id)
    return [schemas.Artifact.model_validate(a) for a in artifacts]


@router.get("/{artifact_type}", response_model=schemas.Artifact)
def get_artifact_by_type(
    artifact_type: models.ArtifactType,
    project: models.Project = Depends(get_project_or_404),
    db: Session = Depends(get_db)
):
    """特定の種類の成果物を取得（最新）"""
    artifact = crud.get_artifact_by_type(db, project.id, artifact_type)
    
    if not artifact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artifact of type {artifact_type} not found"
        )
    
    return schemas.Artifact.model_validate(artifact)


@router.get("/{artifact_type}/download")
def download_artifact(
    artifact_type: models.ArtifactType,
    project: models.Project = Depends(get_project_or_404),
    db: Session = Depends(get_db)
):
    """成果物をMarkdownファイルとしてダウンロード"""
    artifact = crud.get_artifact_by_type(db, project.id, artifact_type)
    
    if not artifact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artifact of type {artifact_type} not found"
        )
    
    # ファイル名を生成
    filename_map = {
        models.ArtifactType.DECISION_LOG: "decision_log.md",
        models.ArtifactType.CONFIG_WORKBOOK: "config_workbook.md",
        models.ArtifactType.TEST_VIEW: "test_view.md",
        models.ArtifactType.MIGRATION_VIEW: "migration_view.md"
    }
    filename = filename_map.get(artifact_type, "artifact.md")
    
    return Response(
        content=artifact.content,
        media_type="text/markdown",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/export/xlsx")
def export_xlsx(
    project: models.Project = Depends(get_project_or_404),
    db: Session = Depends(get_db)
):
    """
    設定ワークブックをXLSX形式でエクスポート
    
    複数シートに分けてサマリー・設定項目・決定事項・テスト観点を出力
    """
    generator = ArtifactGenerator(db, project.id)
    xlsx_content = generator.generate_xlsx_export()
    
    filename = f"imgquest_workbook_{project.id}.xlsx"
    
    return Response(
        content=xlsx_content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/export/json")
def export_json(
    project: models.Project = Depends(get_project_or_404),
    db: Session = Depends(get_db)
):
    """
    全決定事項・設定・回答をJSON形式でエクスポート
    
    LedgerForge連携を想定した構造化データ出力
    """
    generator = ArtifactGenerator(db, project.id)
    json_content = generator.generate_json_export()
    
    filename = f"imgquest_export_{project.id}.json"
    
    return Response(
        content=json_content,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
