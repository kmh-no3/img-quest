from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Any, Dict
from models import BacklogStatus, ArtifactType, ProjectMode


# ========== Project ==========

class ProjectBase(BaseModel):
    """プロジェクト基本スキーマ"""
    name: str = Field(..., min_length=1, max_length=255)
    mode: ProjectMode = ProjectMode.EXPERT  # デフォルトはEXPERT
    country: Optional[str] = None
    currency: Optional[str] = None
    industry: Optional[str] = None
    company_count: Optional[int] = None
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    """プロジェクト作成スキーマ"""
    pass


class ProjectUpdate(BaseModel):
    """プロジェクト更新スキーマ"""
    name: Optional[str] = None
    mode: Optional[ProjectMode] = None
    country: Optional[str] = None
    currency: Optional[str] = None
    industry: Optional[str] = None
    company_count: Optional[int] = None
    description: Optional[str] = None


class Project(ProjectBase):
    """プロジェクトレスポンススキーマ"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectWithStats(Project):
    """統計情報付きプロジェクト"""
    total_questions: int = 0
    answered_questions: int = 0
    backlog_ready: int = 0
    backlog_blocked: int = 0
    backlog_done: int = 0


# ========== ConfigItem ==========

class ConfigItemInput(BaseModel):
    """設定項目の入力定義"""
    name: str
    type: str  # select, multiselect, string, number
    options: Optional[List[str]] = None


class ConfigItem(BaseModel):
    """設定項目スキーマ"""
    id: str
    title: str
    description: Optional[str] = None
    priority: Optional[str] = None
    inputs: List[Dict[str, Any]]
    depends_on: List[str]
    produces: List[str]
    notes: Optional[List[str]] = None
    
    class Config:
        from_attributes = True


# ========== Answer ==========

class AnswerCreate(BaseModel):
    """回答作成スキーマ"""
    config_item_id: str
    input_name: str
    value: Any  # 文字列、数値、リストなど


class Answer(BaseModel):
    """回答レスポンススキーマ"""
    id: int
    project_id: int
    config_item_id: str
    input_name: str
    value: Any
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== Decision ==========

class DecisionCreate(BaseModel):
    """決定事項作成スキーマ"""
    config_item_id: str
    title: str
    rationale: Optional[str] = None
    impact: Optional[str] = None


class Decision(BaseModel):
    """決定事項レスポンススキーマ"""
    id: int
    project_id: int
    config_item_id: str
    title: str
    rationale: Optional[str] = None
    impact: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ========== BacklogItem ==========

class BacklogItemUpdate(BaseModel):
    """バックログアイテム更新スキーマ"""
    status: Optional[BacklogStatus] = None


class BacklogItem(BaseModel):
    """バックログアイテムレスポンススキーマ"""
    id: int
    project_id: int
    config_item_id: str
    status: BacklogStatus
    answered: bool
    created_at: datetime
    updated_at: datetime
    config_item: Optional[ConfigItem] = None
    
    class Config:
        from_attributes = True


# ========== Artifact ==========

class ArtifactGenerate(BaseModel):
    """成果物生成リクエスト"""
    artifact_types: Optional[List[ArtifactType]] = None  # Noneの場合は全て生成


class Artifact(BaseModel):
    """成果物レスポンススキーマ"""
    id: int
    project_id: int
    artifact_type: ArtifactType
    content: str
    tbd_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== Wizard ==========

class QuestionInput(BaseModel):
    """ウィザード用の質問入力項目"""
    name: str
    type: str
    label: str
    options: Optional[List[str]] = None
    required: bool = True
    recommended: Optional[Any] = None  # 推奨値（初心者モード用）
    option_labels: Optional[Dict[str, str]] = None  # 選択肢のラベル（初心者モード用）


class Question(BaseModel):
    """ウィザード用の質問"""
    config_item_id: str
    title: str
    description: Optional[str] = None
    inputs: List[QuestionInput]
    priority: str
    progress: int  # 現在の進捗（1〜N）
    total: int  # 全質問数
    why: Optional[str] = None  # なぜこの質問が必要か（初心者モード用）


class AnswerSubmit(BaseModel):
    """ウィザード回答送信"""
    config_item_id: str
    answers: Dict[str, Any]  # {input_name: value}
