from sqlalchemy.orm import Session
from typing import List, Optional
import models
import schemas


# ========== Project CRUD ==========

def get_project(db: Session, project_id: int) -> Optional[models.Project]:
    """プロジェクトをIDで取得"""
    return db.query(models.Project).filter(models.Project.id == project_id).first()


def get_projects(db: Session, skip: int = 0, limit: int = 100) -> List[models.Project]:
    """プロジェクト一覧を取得"""
    return db.query(models.Project).offset(skip).limit(limit).all()


def create_project(db: Session, project: schemas.ProjectCreate) -> models.Project:
    """プロジェクトを作成"""
    db_project = models.Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def update_project(db: Session, project_id: int, project_update: schemas.ProjectUpdate) -> Optional[models.Project]:
    """プロジェクトを更新"""
    db_project = get_project(db, project_id)
    if not db_project:
        return None
    
    update_data = project_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_project, key, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project


def delete_project(db: Session, project_id: int) -> bool:
    """プロジェクトを削除"""
    db_project = get_project(db, project_id)
    if not db_project:
        return False
    
    db.delete(db_project)
    db.commit()
    return True


# ========== ConfigItem CRUD ==========

def get_config_item(db: Session, config_item_id: str) -> Optional[models.ConfigItem]:
    """設定項目をIDで取得"""
    return db.query(models.ConfigItem).filter(models.ConfigItem.id == config_item_id).first()


def get_config_items(db: Session) -> List[models.ConfigItem]:
    """設定項目一覧を取得"""
    return db.query(models.ConfigItem).all()


def create_config_item(db: Session, config_item_data: dict) -> models.ConfigItem:
    """設定項目を作成"""
    db_item = models.ConfigItem(**config_item_data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def upsert_config_item(db: Session, config_item_data: dict) -> models.ConfigItem:
    """設定項目を作成または更新"""
    existing = get_config_item(db, config_item_data['id'])
    if existing:
        for key, value in config_item_data.items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        return create_config_item(db, config_item_data)


# ========== Answer CRUD ==========

def get_answers(db: Session, project_id: int) -> List[models.Answer]:
    """プロジェクトの回答一覧を取得"""
    return db.query(models.Answer).filter(models.Answer.project_id == project_id).all()


def get_answers_by_config_item(db: Session, project_id: int, config_item_id: str) -> List[models.Answer]:
    """特定の設定項目に対する回答を取得"""
    return db.query(models.Answer).filter(
        models.Answer.project_id == project_id,
        models.Answer.config_item_id == config_item_id
    ).all()


def create_answer(db: Session, project_id: int, answer: schemas.AnswerCreate) -> models.Answer:
    """回答を作成"""
    db_answer = models.Answer(
        project_id=project_id,
        **answer.model_dump()
    )
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    return db_answer


# ========== Decision CRUD ==========

def get_decisions(db: Session, project_id: int) -> List[models.Decision]:
    """プロジェクトの決定事項一覧を取得"""
    return db.query(models.Decision).filter(
        models.Decision.project_id == project_id
    ).order_by(models.Decision.created_at.desc()).all()


def create_decision(db: Session, project_id: int, decision: schemas.DecisionCreate) -> models.Decision:
    """決定事項を作成"""
    db_decision = models.Decision(
        project_id=project_id,
        **decision.model_dump()
    )
    db.add(db_decision)
    db.commit()
    db.refresh(db_decision)
    return db_decision


# ========== BacklogItem CRUD ==========

def get_backlog_items(db: Session, project_id: int) -> List[models.BacklogItem]:
    """プロジェクトのバックログ一覧を取得"""
    return db.query(models.BacklogItem).filter(
        models.BacklogItem.project_id == project_id
    ).all()


def get_backlog_item(db: Session, project_id: int, item_id: int) -> Optional[models.BacklogItem]:
    """バックログアイテムを取得"""
    return db.query(models.BacklogItem).filter(
        models.BacklogItem.project_id == project_id,
        models.BacklogItem.id == item_id
    ).first()


def create_backlog_item(db: Session, project_id: int, config_item_id: str) -> models.BacklogItem:
    """バックログアイテムを作成"""
    db_item = models.BacklogItem(
        project_id=project_id,
        config_item_id=config_item_id,
        status=models.BacklogStatus.PENDING,
        answered=False
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_backlog_item(db: Session, item_id: int, update: schemas.BacklogItemUpdate) -> Optional[models.BacklogItem]:
    """バックログアイテムを更新"""
    db_item = db.query(models.BacklogItem).filter(models.BacklogItem.id == item_id).first()
    if not db_item:
        return None
    
    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item


# ========== Artifact CRUD ==========

def get_artifacts(db: Session, project_id: int) -> List[models.Artifact]:
    """プロジェクトの成果物一覧を取得"""
    return db.query(models.Artifact).filter(
        models.Artifact.project_id == project_id
    ).order_by(models.Artifact.created_at.desc()).all()


def get_artifact_by_type(db: Session, project_id: int, artifact_type: models.ArtifactType) -> Optional[models.Artifact]:
    """特定の種類の成果物を取得（最新）"""
    return db.query(models.Artifact).filter(
        models.Artifact.project_id == project_id,
        models.Artifact.artifact_type == artifact_type
    ).order_by(models.Artifact.created_at.desc()).first()


def create_artifact(db: Session, project_id: int, artifact_type: models.ArtifactType, content: str, tbd_count: int = 0) -> models.Artifact:
    """成果物を作成"""
    db_artifact = models.Artifact(
        project_id=project_id,
        artifact_type=artifact_type,
        content=content,
        tbd_count=tbd_count
    )
    db.add(db_artifact)
    db.commit()
    db.refresh(db_artifact)
    return db_artifact
