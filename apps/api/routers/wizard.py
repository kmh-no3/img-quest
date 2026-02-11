from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import crud
import schemas
import models
from database import get_db
from dependencies import get_project_or_404
from services.dependency_engine import (
    get_next_questions_for_project,
    update_project_backlog
)

router = APIRouter(prefix="/api/projects/{project_id}/wizard", tags=["wizard"])


@router.get("/questions", response_model=schemas.Question)
def get_next_question(
    project: models.Project = Depends(get_project_or_404),
    db: Session = Depends(get_db)
):
    """
    次に回答すべき質問を取得
    
    依存関係を考慮し、READYステータスの質問の中から
    優先度の高いものを1つ返す。
    プロジェクトのmodeに応じてフィルタリングする。
    """
    # プロジェクトのmodeを取得
    mode_filter = project.mode.value if project.mode else 'EXPERT'
    is_beginner = mode_filter == 'BEGINNER'
    
    # バックログステータスを更新（mode_filter を渡して依存関係チェックに反映）
    update_project_backlog(db, project.id, mode_filter=mode_filter)
    
    # プロジェクトのmodeに応じて質問を取得
    next_questions = get_next_questions_for_project(db, project.id, limit=1, mode_filter=mode_filter)
    
    if not next_questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No more questions available. All dependencies satisfied or all questions answered."
        )
    
    config_item = next_questions[0]
    
    # 進捗を計算（初心者モードでは beginner_mode=True の項目のみカウント）
    backlog_items = crud.get_backlog_items(db, project.id)
    if is_beginner:
        # 各バックログアイテムの config_item を参照してフィルタリング
        config_items_map = {item.id: item for item in crud.get_config_items(db)}
        relevant_items = [
            item for item in backlog_items
            if config_items_map.get(item.config_item_id) and config_items_map[item.config_item_id].beginner_mode
        ]
    else:
        relevant_items = backlog_items
    
    answered_count = sum(1 for item in relevant_items if item.answered)
    total_count = len(relevant_items)
    
    # プロジェクトのmodeに応じて表示を切り替え
    display_title = config_item.beginner_title if (is_beginner and config_item.beginner_title) else config_item.title
    display_description = config_item.beginner_description if (is_beginner and config_item.beginner_description) else config_item.description
    
    # 質問スキーマに変換
    question_inputs = []
    for input_def in (config_item.inputs or []):
        # YAMLでYES/NOがbool値に変換される問題への防御
        raw_options = input_def.get('options')
        if raw_options is not None:
            raw_options = [str(opt) if not isinstance(opt, str) else opt for opt in raw_options]
        
        # ラベル取得（初心者モードでは option_labels を使用）
        label = input_def.get('label') or input_def.get('name', '').replace('_', ' ').title()
        
        # 推奨値の取得（初心者モード用）
        recommended = input_def.get('recommended')
        
        question_inputs.append(schemas.QuestionInput(
            name=input_def.get('name', ''),
            type=input_def.get('type', 'string'),
            label=label,
            options=raw_options,
            required=True,
            recommended=recommended,
            option_labels=input_def.get('option_labels')
        ))
    
    return schemas.Question(
        config_item_id=config_item.id,
        title=display_title,
        description=display_description,
        inputs=question_inputs,
        priority=config_item.priority or 'P1',
        progress=answered_count + 1,
        total=total_count,
        why=config_item.beginner_why if is_beginner else None
    )


@router.get("/questions/{config_item_id}", response_model=schemas.Question)
def get_question_by_id(
    config_item_id: str,
    project: models.Project = Depends(get_project_or_404),
    db: Session = Depends(get_db)
):
    """
    指定されたconfig_item_idの質問を取得
    
    既に回答済みの質問を編集する際に使用する。
    モードに応じた表示切替も行う。
    """
    config_item = crud.get_config_item(db, config_item_id)
    if not config_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ConfigItem {config_item_id} not found"
        )
    
    mode_filter = project.mode.value if project.mode else 'EXPERT'
    is_beginner = mode_filter == 'BEGINNER'
    
    # 進捗を計算
    backlog_items = crud.get_backlog_items(db, project.id)
    if is_beginner:
        config_items_map = {item.id: item for item in crud.get_config_items(db)}
        relevant_items = [
            item for item in backlog_items
            if config_items_map.get(item.config_item_id) and config_items_map[item.config_item_id].beginner_mode
        ]
    else:
        relevant_items = backlog_items
    
    answered_count = sum(1 for item in relevant_items if item.answered)
    total_count = len(relevant_items)
    
    # モードに応じた表示切替
    display_title = config_item.beginner_title if (is_beginner and config_item.beginner_title) else config_item.title
    display_description = config_item.beginner_description if (is_beginner and config_item.beginner_description) else config_item.description
    
    # 入力項目を構築
    question_inputs = []
    for input_def in (config_item.inputs or []):
        raw_options = input_def.get('options')
        if raw_options is not None:
            raw_options = [str(opt) if not isinstance(opt, str) else opt for opt in raw_options]
        
        label = input_def.get('label') or input_def.get('name', '').replace('_', ' ').title()
        recommended = input_def.get('recommended')
        
        question_inputs.append(schemas.QuestionInput(
            name=input_def.get('name', ''),
            type=input_def.get('type', 'string'),
            label=label,
            options=raw_options,
            required=True,
            recommended=recommended,
            option_labels=input_def.get('option_labels')
        ))
    
    return schemas.Question(
        config_item_id=config_item.id,
        title=display_title,
        description=display_description,
        inputs=question_inputs,
        priority=config_item.priority or 'P1',
        progress=answered_count,
        total=total_count,
        why=config_item.beginner_why if is_beginner else None
    )


@router.get("/answers/{config_item_id}")
def get_answers_for_item(
    config_item_id: str,
    project: models.Project = Depends(get_project_or_404),
    db: Session = Depends(get_db)
):
    """
    指定されたconfig_item_idの回答を取得
    
    {input_name: value} の辞書形式で返す。
    回答が存在しない場合は空の辞書を返す。
    """
    answers = crud.get_answers_by_config_item(db, project.id, config_item_id)
    return {answer.input_name: answer.value for answer in answers}


@router.post("/answers", status_code=status.HTTP_201_CREATED)
def submit_answer(
    answer_data: schemas.AnswerSubmit,
    project: models.Project = Depends(get_project_or_404),
    db: Session = Depends(get_db)
):
    """
    ウィザードの回答を送信
    
    複数の入力項目に対する回答を一度に保存し、
    自動的にDecisionを作成する
    """
    # 設定項目が存在するか確認
    config_item = crud.get_config_item(db, answer_data.config_item_id)
    if not config_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ConfigItem {answer_data.config_item_id} not found"
        )
    
    # 既存の回答を削除（上書き）
    existing_answers = crud.get_answers_by_config_item(
        db, project.id, answer_data.config_item_id
    )
    for existing in existing_answers:
        db.delete(existing)
    db.commit()
    
    # 回答を保存
    saved_answers = []
    for input_name, value in answer_data.answers.items():
        answer = schemas.AnswerCreate(
            config_item_id=answer_data.config_item_id,
            input_name=input_name,
            value=value
        )
        db_answer = crud.create_answer(db, project.id, answer)
        saved_answers.append(db_answer)
    
    # Decisionを作成
    rationale_parts = []
    for input_name, value in answer_data.answers.items():
        if isinstance(value, list):
            value_str = ', '.join(str(v) for v in value)
        else:
            value_str = str(value)
        rationale_parts.append(f"{input_name}: {value_str}")
    
    decision = schemas.DecisionCreate(
        config_item_id=answer_data.config_item_id,
        title=f"{config_item.title}の決定",
        rationale="; ".join(rationale_parts),
        impact=config_item.description
    )
    db_decision = crud.create_decision(db, project.id, decision)
    
    # バックログステータスを更新
    mode_filter = project.mode.value if project.mode else 'EXPERT'
    update_project_backlog(db, project.id, mode_filter=mode_filter)
    
    return {
        'message': 'Answer submitted successfully',
        'answers_count': len(saved_answers),
        'decision_id': db_decision.id
    }


@router.get("/decisions", response_model=List[schemas.Decision])
def get_decisions(
    project: models.Project = Depends(get_project_or_404),
    db: Session = Depends(get_db)
):
    """プロジェクトの全決定事項を取得"""
    return crud.get_decisions(db, project.id)


@router.get("/progress")
def get_progress(
    project: models.Project = Depends(get_project_or_404),
    db: Session = Depends(get_db)
):
    """
    ウィザードの進捗状況を取得
    
    プロジェクトのmodeに応じてカウント対象をフィルタリングする
    """
    mode_filter = project.mode.value if project.mode else 'EXPERT'
    is_beginner = mode_filter == 'BEGINNER'
    
    backlog_items = crud.get_backlog_items(db, project.id)
    
    if is_beginner:
        config_items_map = {item.id: item for item in crud.get_config_items(db)}
        backlog_items = [
            item for item in backlog_items
            if config_items_map.get(item.config_item_id) and config_items_map[item.config_item_id].beginner_mode
        ]
    
    total = len(backlog_items)
    answered = sum(1 for item in backlog_items if item.answered)
    ready = sum(1 for item in backlog_items if item.status == models.BacklogStatus.READY and not item.answered)
    blocked = sum(1 for item in backlog_items if item.status == models.BacklogStatus.BLOCKED)
    done = sum(1 for item in backlog_items if item.status == models.BacklogStatus.DONE)
    
    return {
        'total': total,
        'answered': answered,
        'ready': ready,
        'blocked': blocked,
        'done': done,
        'progress_percentage': round((answered / total * 100) if total > 0 else 0, 1)
    }
