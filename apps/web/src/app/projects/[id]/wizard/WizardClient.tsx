'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter, useParams, useSearchParams } from 'next/navigation';
import { wizardAPI } from '@/lib/api-client';
import { Question } from '@/lib/types';
import HelpButton from '@/components/HelpButton';

export default function WizardPage() {
  const router = useRouter();
  const params = useParams();
  const searchParams = useSearchParams();
  const projectId = parseInt(params.id as string);

  // 編集モード: ?edit=FI-CORE-001 のようにクエリパラメータで指定
  const editConfigItemId = searchParams.get('edit');
  const isEditMode = !!editConfigItemId;

  const [question, setQuestion] = useState<Question | null>(null);
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [completed, setCompleted] = useState(false);

  // 質問履歴スタック（戻るボタン用）
  const [questionHistory, setQuestionHistory] = useState<string[]>([]);

  // 特定の質問を読み込む（回答プリフィル付き）
  const loadQuestionById = useCallback(async (configItemId: string) => {
    try {
      setLoading(true);
      setError(null);
      const [questionData, answersData] = await Promise.all([
        wizardAPI.getQuestionById(projectId, configItemId),
        wizardAPI.getAnswersForItem(projectId, configItemId),
      ]);
      setQuestion(questionData);
      setAnswers(answersData || {});
    } catch (err: any) {
      setError(err.message || '質問の読み込みに失敗しました');
      setQuestion(null);
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  // 次の質問を読み込む（通常フロー）
  const loadNextQuestion = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await wizardAPI.getNextQuestion(projectId);
      setQuestion(data);
      setAnswers({});
    } catch (err: any) {
      if (err.status === 404) {
        setCompleted(true);
      } else {
        setError(err.message || '質問の読み込みに失敗しました');
      }
      setQuestion(null);
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  // 初回ロード
  useEffect(() => {
    if (isEditMode) {
      loadQuestionById(editConfigItemId);
    } else {
      loadNextQuestion();
    }
  }, [projectId, editConfigItemId, isEditMode, loadQuestionById, loadNextQuestion]);

  // 回答送信
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!question) return;

    const missingRequired = question.inputs.filter(
      input => input.required && !answers[input.name]
    );
    if (missingRequired.length > 0) {
      setError('すべての必須項目に回答してください');
      return;
    }

    try {
      setSubmitting(true);
      setError(null);
      await wizardAPI.submitAnswer(projectId, {
        config_item_id: question.config_item_id,
        answers: answers,
      });

      if (isEditMode) {
        // 編集モード: バックログに戻る
        router.push(`/projects/${projectId}/backlog`);
      } else {
        // 通常フロー: 現在の質問を履歴にプッシュして次へ
        setQuestionHistory(prev => [...prev, question.config_item_id]);
        await loadNextQuestion();
      }
    } catch (err: any) {
      setError(err.message || '回答の送信に失敗しました');
    } finally {
      setSubmitting(false);
    }
  };

  // 前の質問に戻る
  const handleGoBack = async () => {
    if (questionHistory.length === 0) return;

    const previousConfigItemId = questionHistory[questionHistory.length - 1];
    setQuestionHistory(prev => prev.slice(0, -1));
    await loadQuestionById(previousConfigItemId);
  };

  const handleInputChange = (name: string, value: any) => {
    setAnswers({ ...answers, [name]: value });
  };

  const useRecommended = (inputName: string, recommendedValue: any) => {
    setAnswers({ ...answers, [inputName]: recommendedValue });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">読み込み中...</p>
        </div>
      </div>
    );
  }

  if (completed) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="card text-center py-12">
          <div className="text-green-500 mb-4">
            <svg className="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">ウィザード完了！</h2>
          <p className="text-gray-600 mb-8">
            全ての質問に回答しました。<br />
            バックログと成果物を確認できます。
          </p>
          <div className="flex gap-4 justify-center">
            <button
              onClick={() => router.push(`/projects/${projectId}/backlog`)}
              className="btn btn-primary"
            >
              バックログを見る
            </button>
            <button
              onClick={() => router.push(`/projects/${projectId}/artifacts`)}
              className="btn btn-secondary"
            >
              成果物を生成
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (error && !question) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="card">
          <div className="text-center text-red-600">
            <p className="text-lg font-semibold">エラー</p>
            <p className="mt-2">{error}</p>
            <button onClick={() => router.push(`/projects/${projectId}`)} className="btn btn-primary mt-4">
              プロジェクトに戻る
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!question) {
    return null;
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-900">ウィザード</h1>
            {isEditMode && (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-800 border border-amber-200">
                回答を編集中
              </span>
            )}
          </div>
          <div className="flex gap-3">
            <HelpButton pageKey="wizard" />
            <button
              onClick={() => isEditMode ? router.push(`/projects/${projectId}/backlog`) : router.push(`/projects/${projectId}`)}
              className="btn btn-secondary text-sm"
            >
              {isEditMode ? 'バックログに戻る' : '後で続ける'}
            </button>
          </div>
        </div>

        {/* 進捗バー（編集モード時は非表示） */}
        {!isEditMode && (
          <div className="mb-2">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>質問 {question.progress} / {question.total}</span>
              <span>{Math.round((question.progress / question.total) * 100)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-primary-600 h-2 rounded-full transition-all"
                style={{ width: `${(question.progress / question.total) * 100}%` }}
              />
            </div>
          </div>
        )}
      </div>

      <div className="card">
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
              {question.priority}
            </span>
            <span className="text-sm text-gray-500">{question.config_item_id}</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            {question.title}
          </h2>
          {question.description && (
            <p className="text-gray-600">{question.description}</p>
          )}
          {question.why && (
            <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start">
                <svg className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div className="ml-2">
                  <div className="text-sm font-medium text-blue-900">なぜこの質問が必要？</div>
                  <div className="text-sm text-blue-800 mt-1">{question.why}</div>
                </div>
              </div>
            </div>
          )}
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="space-y-6">
            {question.inputs.map((input) => (
              <div key={input.name}>
                <div className="flex items-center justify-between mb-2">
                  <label className="label mb-0">
                    {input.label}
                    {input.required && <span className="text-red-500 ml-1">*</span>}
                  </label>
                  {input.recommended && (
                    <button
                      type="button"
                      onClick={() => useRecommended(input.name, input.recommended)}
                      className="text-xs text-primary-600 hover:text-primary-700 font-medium"
                    >
                      推奨値を使用
                    </button>
                  )}
                </div>

                {input.type === 'select' && (
                  <select
                    className="input"
                    value={answers[input.name] || ''}
                    onChange={(e) => handleInputChange(input.name, e.target.value)}
                    required={input.required}
                  >
                    <option value="">選択してください</option>
                    {input.options?.map((option) => {
                      const label = input.option_labels?.[option] || option;
                      const isRecommended = input.recommended === option;
                      return (
                        <option key={option} value={option}>
                          {label} {isRecommended ? '（推奨）' : ''}
                        </option>
                      );
                    })}
                  </select>
                )}

                {input.type === 'multiselect' && (
                  <div className="space-y-2">
                    {input.options?.map((option) => {
                      const label = input.option_labels?.[option] || option;
                      const isRecommended = Array.isArray(input.recommended) && input.recommended.includes(option);
                      return (
                        <label key={option} className="flex items-center">
                          <input
                            type="checkbox"
                            className="mr-2 h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                            checked={(answers[input.name] || []).includes(option)}
                            onChange={(e) => {
                              const current = answers[input.name] || [];
                              if (e.target.checked) {
                                handleInputChange(input.name, [...current, option]);
                              } else {
                                handleInputChange(input.name, current.filter((v: string) => v !== option));
                              }
                            }}
                          />
                          <span>
                            {label}
                            {isRecommended && (
                              <span className="ml-2 text-xs text-primary-600 font-medium">（推奨）</span>
                            )}
                          </span>
                        </label>
                      );
                    })}
                  </div>
                )}

                {input.type === 'string' && (
                  <input
                    type="text"
                    className="input"
                    value={answers[input.name] || ''}
                    onChange={(e) => handleInputChange(input.name, e.target.value)}
                    required={input.required}
                    placeholder={input.recommended ? `推奨: ${input.recommended}` : ''}
                  />
                )}

                {input.type === 'number' && (
                  <input
                    type="number"
                    className="input"
                    value={answers[input.name] || ''}
                    onChange={(e) => handleInputChange(input.name, parseInt(e.target.value) || '')}
                    required={input.required}
                    placeholder={input.recommended ? `推奨: ${input.recommended}` : ''}
                  />
                )}
              </div>
            ))}
          </div>

          <div className="mt-8 flex gap-4">
            {/* 前の質問に戻る（通常フローで履歴がある場合のみ） */}
            {!isEditMode && questionHistory.length > 0 && (
              <button
                type="button"
                onClick={handleGoBack}
                className="btn btn-secondary"
                disabled={submitting}
              >
                <svg className="w-4 h-4 mr-1 inline-block" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                前の質問
              </button>
            )}
            <button
              type="button"
              onClick={() => isEditMode ? router.push(`/projects/${projectId}/backlog`) : router.push(`/projects/${projectId}`)}
              className="btn btn-secondary flex-1"
              disabled={submitting}
            >
              {isEditMode ? 'キャンセル' : '後で'}
            </button>
            <button
              type="submit"
              className="btn btn-primary flex-1"
              disabled={submitting}
            >
              {submitting ? '送信中...' : isEditMode ? '更新' : '次へ'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
