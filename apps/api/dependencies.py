from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import crud
import models


def get_project_or_404(project_id: int, db: Session = Depends(get_db)) -> models.Project:
    """プロジェクトを取得、存在しない場合は404エラー"""
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    return project


def get_config_item_or_404(config_item_id: str, db: Session = Depends(get_db)) -> models.ConfigItem:
    """設定項目を取得、存在しない場合は404エラー"""
    config_item = crud.get_config_item(db, config_item_id)
    if not config_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ConfigItem with id {config_item_id} not found"
        )
    return config_item
