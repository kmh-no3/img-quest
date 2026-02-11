from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import crud
import schemas
import models
from database import get_db
from dependencies import get_project_or_404

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("/", response_model=schemas.Project, status_code=status.HTTP_201_CREATED)
def create_project(
    project: schemas.ProjectCreate,
    db: Session = Depends(get_db)
):
    """
    新規プロジェクトを作成
    
    プロジェクト作成時に、P0のConfigItemをバックログに自動追加
    """
    # プロジェクト作成
    db_project = crud.create_project(db, project)
    
    # P0の設定項目をバックログに追加
    config_items = crud.get_config_items(db)
    p0_items = [item for item in config_items if item.priority == "P0"]
    
    for item in p0_items:
        crud.create_backlog_item(db, db_project.id, item.id)
    
    return db_project


@router.get("/", response_model=List[schemas.ProjectWithStats])
def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """プロジェクト一覧を取得（統計情報付き）"""
    projects = crud.get_projects(db, skip=skip, limit=limit)
    
    result = []
    for project in projects:
        # 統計情報を計算
        backlog_items = crud.get_backlog_items(db, project.id)
        answers = crud.get_answers(db, project.id)
        
        # 回答済みの設定項目IDを取得
        answered_config_ids = set(answer.config_item_id for answer in answers)
        
        stats = schemas.ProjectWithStats(
            **project.__dict__,
            total_questions=len(backlog_items),
            answered_questions=len(answered_config_ids),
            backlog_ready=sum(1 for item in backlog_items if item.status == models.BacklogStatus.READY),
            backlog_blocked=sum(1 for item in backlog_items if item.status == models.BacklogStatus.BLOCKED),
            backlog_done=sum(1 for item in backlog_items if item.status == models.BacklogStatus.DONE)
        )
        result.append(stats)
    
    return result


@router.get("/{project_id}", response_model=schemas.ProjectWithStats)
def get_project(
    project: models.Project = Depends(get_project_or_404),
    db: Session = Depends(get_db)
):
    """プロジェクト詳細を取得"""
    # 統計情報を計算
    backlog_items = crud.get_backlog_items(db, project.id)
    answers = crud.get_answers(db, project.id)
    answered_config_ids = set(answer.config_item_id for answer in answers)
    
    return schemas.ProjectWithStats(
        **project.__dict__,
        total_questions=len(backlog_items),
        answered_questions=len(answered_config_ids),
        backlog_ready=sum(1 for item in backlog_items if item.status == models.BacklogStatus.READY),
        backlog_blocked=sum(1 for item in backlog_items if item.status == models.BacklogStatus.BLOCKED),
        backlog_done=sum(1 for item in backlog_items if item.status == models.BacklogStatus.DONE)
    )


@router.put("/{project_id}", response_model=schemas.Project)
def update_project(
    project_update: schemas.ProjectUpdate,
    project: models.Project = Depends(get_project_or_404),
    db: Session = Depends(get_db)
):
    """プロジェクトを更新"""
    updated = crud.update_project(db, project.id, project_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project: models.Project = Depends(get_project_or_404),
    db: Session = Depends(get_db)
):
    """プロジェクトを削除"""
    crud.delete_project(db, project.id)
    return None
