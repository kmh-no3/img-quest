from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import crud
import schemas
import models
from database import get_db
from dependencies import get_project_or_404
from services.dependency_engine import (
    update_project_backlog,
    get_dependency_graph_for_project
)

router = APIRouter(prefix="/api/projects/{project_id}/backlog", tags=["backlog"])


@router.get("/", response_model=List[schemas.BacklogItem])
def get_backlog(
    project: models.Project = Depends(get_project_or_404),
    status_filter: Optional[str] = Query(None, description="Filter by status: PENDING, BLOCKED, READY, DONE"),
    db: Session = Depends(get_db)
):
    """
    プロジェクトのバックログ一覧を取得
    
    オプションでステータスによるフィルタリングが可能
    """
    # バックログステータスを更新
    update_project_backlog(db, project.id)
    
    # バックログアイテムを取得
    items = crud.get_backlog_items(db, project.id)
    
    # ステータスフィルタリング
    if status_filter:
        try:
            status_enum = models.BacklogStatus(status_filter.upper())
            items = [item for item in items if item.status == status_enum]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )
    
    # ConfigItemを結合
    result = []
    for item in items:
        config_item = crud.get_config_item(db, item.config_item_id)
        backlog_item = schemas.BacklogItem.model_validate(item)
        if config_item:
            backlog_item.config_item = schemas.ConfigItem.model_validate(config_item)
        result.append(backlog_item)
    
    # 優先度でソート
    priority_order = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
    result.sort(
        key=lambda x: (
            priority_order.get(x.config_item.priority if x.config_item else 'P3', 99),
            x.config_item_id if x.config_item else ''
        )
    )
    
    return result


@router.get("/graph")
def get_dependency_graph(
    project: models.Project = Depends(get_project_or_404),
    db: Session = Depends(get_db)
):
    """
    依存関係グラフデータを取得
    
    フロントエンドでの可視化用に、ノードとエッジの情報を返す
    """
    graph = get_dependency_graph_for_project(db, project.id)
    return graph


@router.patch("/{item_id}", response_model=schemas.BacklogItem)
def update_backlog_item_status(
    item_id: int,
    update_data: schemas.BacklogItemUpdate,
    project: models.Project = Depends(get_project_or_404),
    db: Session = Depends(get_db)
):
    """
    バックログアイテムのステータスを更新
    
    手動でステータスを変更する場合に使用
    """
    # バックログアイテムを取得
    item = crud.get_backlog_item(db, project.id, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"BacklogItem {item_id} not found"
        )
    
    # 更新
    updated = crud.update_backlog_item(db, item_id, update_data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update backlog item"
        )
    
    # ConfigItemを結合
    config_item = crud.get_config_item(db, updated.config_item_id)
    result = schemas.BacklogItem.model_validate(updated)
    if config_item:
        result.config_item = schemas.ConfigItem.model_validate(config_item)
    
    return result


@router.get("/summary")
def get_backlog_summary(
    project: models.Project = Depends(get_project_or_404),
    db: Session = Depends(get_db)
):
    """
    バックログのサマリー情報を取得
    
    ステータス別の件数、優先度別の件数などを返す
    """
    # バックログステータスを更新
    update_project_backlog(db, project.id)
    
    items = crud.get_backlog_items(db, project.id)
    
    # ステータス別集計
    by_status = {
        'PENDING': 0,
        'BLOCKED': 0,
        'READY': 0,
        'DONE': 0
    }
    for item in items:
        by_status[item.status.value] += 1
    
    # 優先度別集計
    by_priority = {}
    for item in items:
        config_item = crud.get_config_item(db, item.config_item_id)
        if config_item:
            priority = config_item.priority or 'UNKNOWN'
            by_priority[priority] = by_priority.get(priority, 0) + 1
    
    return {
        'total': len(items),
        'by_status': by_status,
        'by_priority': by_priority,
        'completion_percentage': round((by_status['DONE'] / len(items) * 100) if len(items) > 0 else 0, 1)
    }
