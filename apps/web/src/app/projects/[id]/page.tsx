'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { projectsAPI, wizardAPI } from '@/lib/api-client';
import { ProjectWithStats, WizardProgress } from '@/lib/types';
import HelpButton from '@/components/HelpButton';

export default function ProjectDetailPage() {
  const router = useRouter();
  const params = useParams();
  const projectId = parseInt(params.id as string);

  const [project, setProject] = useState<ProjectWithStats | null>(null);
  const [progress, setProgress] = useState<WizardProgress | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProject();
    loadProgress();
  }, [projectId]);

  const loadProject = async () => {
    try {
      setLoading(true);
      const data = await projectsAPI.get(projectId);
      setProject(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'プロジェクトの読み込みに失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const loadProgress = async () => {
    try {
      const data = await wizardAPI.getProgress(projectId);
      setProgress(data);
    } catch (err) {
      console.error('Progress loading error:', err);
    }
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

  if (error || !project) {
    return (
      <div className="card max-w-2xl mx-auto">
        <div className="text-center text-red-600">
          <p className="text-lg font-semibold">エラー</p>
          <p className="mt-2">{error || 'プロジェクトが見つかりません'}</p>
          <button onClick={() => router.push('/')} className="btn btn-primary mt-4">
            プロジェクト一覧に戻る
          </button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{project.name}</h1>
            {project.description && (
              <p className="mt-2 text-gray-600">{project.description}</p>
            )}
          </div>
          <div className="flex gap-3">
            <HelpButton pageKey="project-detail" />
            <button
              onClick={() => router.push('/')}
              className="btn btn-secondary"
            >
              ← 一覧に戻る
            </button>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
          {project.country && (
            <div className="card">
              <div className="text-sm text-gray-500">国/地域</div>
              <div className="mt-1 font-semibold">{project.country}</div>
            </div>
          )}
          {project.currency && (
            <div className="card">
              <div className="text-sm text-gray-500">通貨</div>
              <div className="mt-1 font-semibold">{project.currency}</div>
            </div>
          )}
          {project.industry && (
            <div className="card">
              <div className="text-sm text-gray-500">業種</div>
              <div className="mt-1 font-semibold">{project.industry}</div>
            </div>
          )}
          {project.company_count && (
            <div className="card">
              <div className="text-sm text-gray-500">会社数</div>
              <div className="mt-1 font-semibold">{project.company_count}</div>
            </div>
          )}
        </div>
      </div>

      {progress && (
        <div className="card mb-8">
          <h2 className="text-xl font-semibold mb-4">進捗状況</h2>
          <div className="mb-4">
            <div className="flex justify-between text-sm mb-2">
              <span>全体の進捗</span>
              <span className="font-medium">{progress.progress_percentage}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-primary-600 h-3 rounded-full transition-all"
                style={{ width: `${progress.progress_percentage}%` }}
              />
            </div>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
            <div>
              <div className="text-sm text-gray-500">全体</div>
              <div className="text-2xl font-bold">{progress.total}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">回答済み</div>
              <div className="text-2xl font-bold text-green-600">{progress.answered}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">対応可能</div>
              <div className="text-2xl font-bold text-blue-600">{progress.ready}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">前の設定が未完了</div>
              <div className="text-2xl font-bold text-red-600">{progress.blocked}</div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div
          className="card hover:shadow-lg transition-shadow cursor-pointer"
          onClick={() => router.push(`/projects/${projectId}/wizard`)}
        >
          <div className="text-primary-600 mb-3">
            <svg className="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold mb-2">ウィザード</h3>
          <p className="text-gray-600 text-sm">質問に答えて設定を決定</p>
        </div>

        <div
          className="card hover:shadow-lg transition-shadow cursor-pointer"
          onClick={() => router.push(`/projects/${projectId}/backlog`)}
        >
          <div className="text-primary-600 mb-3">
            <svg className="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold mb-2">バックログ</h3>
          <p className="text-gray-600 text-sm">設定項目と依存関係を確認</p>
        </div>

        <div
          className="card hover:shadow-lg transition-shadow cursor-pointer"
          onClick={() => router.push(`/projects/${projectId}/artifacts`)}
        >
          <div className="text-primary-600 mb-3">
            <svg className="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold mb-2">成果物</h3>
          <p className="text-gray-600 text-sm">決定事項・設定一覧をエクスポート</p>
        </div>

        <div className="card bg-gray-50">
          <div className="text-gray-400 mb-3">
            <svg className="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold mb-2 text-gray-400">設定</h3>
          <p className="text-gray-400 text-sm">プロジェクト設定（将来実装）</p>
        </div>
      </div>
    </div>
  );
}
