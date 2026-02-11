from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum


class ProjectMode(str, enum.Enum):
    """プロジェクトモード"""
    BEGINNER = "BEGINNER"  # カンタン設定ver（初学者向け）
    EXPERT = "EXPERT"      # 完全マニュアルver（玄人向け）


class BacklogStatus(str, enum.Enum):
    """バックログアイテムのステータス"""
    PENDING = "PENDING"
    BLOCKED = "BLOCKED"
    READY = "READY"
    DONE = "DONE"


class ArtifactType(str, enum.Enum):
    """成果物の種類"""
    DECISION_LOG = "DECISION_LOG"
    CONFIG_WORKBOOK = "CONFIG_WORKBOOK"
    TEST_VIEW = "TEST_VIEW"
    MIGRATION_VIEW = "MIGRATION_VIEW"


class Project(Base):
    """プロジェクト"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    mode = Column(SQLEnum(ProjectMode), default=ProjectMode.EXPERT, nullable=False)  # プロジェクトモード
    country = Column(String(50))
    currency = Column(String(10))
    industry = Column(String(100))
    company_count = Column(Integer)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーション
    answers = relationship("Answer", back_populates="project", cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="project", cascade="all, delete-orphan")
    backlog_items = relationship("BacklogItem", back_populates="project", cascade="all, delete-orphan")
    artifacts = relationship("Artifact", back_populates="project", cascade="all, delete-orphan")


class ConfigItem(Base):
    """設定項目マスタ（カタログから読込）"""
    __tablename__ = "config_items"
    
    id = Column(String(50), primary_key=True)  # FI-CORE-001など
    title = Column(String(255), nullable=False)
    description = Column(Text)
    priority = Column(String(10))  # P0, P1など
    inputs = Column(JSON)  # 入力項目定義
    depends_on = Column(JSON)  # 依存する設定項目IDのリスト
    produces = Column(JSON)  # 生成する成果物のリスト
    notes = Column(JSON)  # 備考
    
    # 初心者モード対応フィールド
    beginner_mode = Column(Boolean, default=True)  # 初心者モードで表示するか
    beginner_title = Column(String(255))  # 初心者向けタイトル
    beginner_description = Column(Text)  # 初心者向け説明
    beginner_why = Column(Text)  # なぜこの質問が必要か
    
    # リレーション
    backlog_items = relationship("BacklogItem", back_populates="config_item")


class Answer(Base):
    """回答"""
    __tablename__ = "answers"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    config_item_id = Column(String(50), ForeignKey("config_items.id"), nullable=False)
    input_name = Column(String(100), nullable=False)  # 入力項目名
    value = Column(JSON, nullable=False)  # 回答値（文字列、リストなど）
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # リレーション
    project = relationship("Project", back_populates="answers")


class Decision(Base):
    """決定事項"""
    __tablename__ = "decisions"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    config_item_id = Column(String(50), ForeignKey("config_items.id"), nullable=False)
    title = Column(String(255), nullable=False)
    rationale = Column(Text)  # 根拠
    impact = Column(Text)  # 影響範囲
    status = Column(String(50), default="DECIDED")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーション
    project = relationship("Project", back_populates="decisions")


class BacklogItem(Base):
    """バックログアイテム（プロジェクトに紐づく設定項目）"""
    __tablename__ = "backlog_items"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    config_item_id = Column(String(50), ForeignKey("config_items.id"), nullable=False)
    status = Column(SQLEnum(BacklogStatus), default=BacklogStatus.PENDING)
    answered = Column(Boolean, default=False)  # 回答済みか
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーション
    project = relationship("Project", back_populates="backlog_items")
    config_item = relationship("ConfigItem", back_populates="backlog_items")


class Artifact(Base):
    """成果物"""
    __tablename__ = "artifacts"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    artifact_type = Column(SQLEnum(ArtifactType), nullable=False)
    content = Column(Text, nullable=False)  # Markdown内容
    tbd_count = Column(Integer, default=0)  # 未決項目数
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # リレーション
    project = relationship("Project", back_populates="artifacts")
