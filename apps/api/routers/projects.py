from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import crud
import schemas
import models
from database import get_db
from dependencies import get_project_or_404
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects", tags=["projects"])


def _select_initial_backlog_items(
    config_items: List[models.ConfigItem],
    project: schemas.ProjectCreate
) -> List[models.ConfigItem]:
    """
    プロジェクト入力値に基づいて初期バックログ項目を選択する
    
    P0項目は全て追加。P1項目は入力内容に応じて条件付き追加。
    
    ルール:
    - P0: 常に追加
    - FI-TAX-001 (税コード): 国が設定されている場合に追加（税制に関連）
    - FI-DIFF-001 (端数差額): 常に追加（基本的な会計処理に必要）
    - FI-DIFF-002 (支払/入金差額): 業種が製造業・卸売の場合に追加（取引量が多い）
    - FI-CLOSE-001 (締め後運用): 常に追加（監査対応に必須）
    - FI-RPT-001 (基本レポート): 常に追加（月次決算に必要）
    """
    selected = []
    
    # P1項目の条件付き追加ルール
    # キー: config_item_id, 値: 追加条件を判定する関数
    p1_conditions = {
        'FI-TAX-001': lambda p: True,  # 税コードは常に必要
        'FI-DIFF-001': lambda p: True,  # 端数差額は常に必要
        'FI-DIFF-002': lambda p: (
            p.industry in ('manufacturing', 'wholesale', 'retail', '製造', '卸売', '小売')
            or p.company_count is not None and p.company_count > 1
            or True  # MVPでは基本的に追加
        ),
        'FI-CLOSE-001': lambda p: True,  # 締め後運用は監査対応で常に必要
        'FI-RPT-001': lambda p: True,  # 基本レポートは常に必要
    }
    
    for item in config_items:
        if item.priority == "P0":
            # P0は無条件で追加
            selected.append(item)
        elif item.id in p1_conditions:
            # P1は条件に応じて追加
            if p1_conditions[item.id](project):
                selected.append(item)
                logger.info(f"Auto-added P1 item {item.id} ({item.title}) based on project inputs")
    
    return selected


@router.post("/", response_model=schemas.Project, status_code=status.HTTP_201_CREATED)
def create_project(
    project: schemas.ProjectCreate,
    db: Session = Depends(get_db)
):
    """
    新規プロジェクトを作成
    
    プロジェクト作成時に、入力内容に応じて必要な設定項目をバックログに自動追加。
    P0項目は全て追加、P1項目は入力値に基づいて条件付き追加。
    """
    # プロジェクト作成
    db_project = crud.create_project(db, project)
    
    # 入力値に基づいてバックログ項目を選択
    config_items = crud.get_config_items(db)
    selected_items = _select_initial_backlog_items(config_items, project)
    
    for item in selected_items:
        crud.create_backlog_item(db, db_project.id, item.id)
    
    logger.info(
        f"Project {db_project.id} created with {len(selected_items)} backlog items "
        f"(P0: {sum(1 for i in selected_items if i.priority == 'P0')}, "
        f"P1: {sum(1 for i in selected_items if i.priority == 'P1')})"
    )
    
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
