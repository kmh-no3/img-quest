'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { projectsAPI } from '@/lib/api-client';
import { ProjectWithStats } from '@/lib/types';
import HelpButton from '@/components/HelpButton';

export default function HomePage() {
  const router = useRouter();
  const [projects, setProjects] = useState<ProjectWithStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const data = await projectsAPI.list();
      setProjects(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'プロジェクトの読み込みに失敗しました');
    } finally {
      setLoading(false);
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

  if (error) {
    return (
      <div className="card max-w-2xl mx-auto">
        <div className="text-center text-red-600">
          <p className="text-lg font-semibold">エラー</p>
          <p className="mt-2">{error}</p>
          <button
            onClick={loadProjects}
            className="btn btn-primary mt-4"
          >
            再試行
          </button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">プロジェクト</h1>
          <p className="mt-2 text-gray-600">
            FI導入プロジェクトの意思決定を管理します
          </p>
        </div>
        <div className="flex gap-3">
          <HelpButton pageKey="project-list" />
          <button
            onClick={() => router.push('/projects/new')}
            className="btn btn-primary"
          >
            + 新規プロジェクト
          </button>
        </div>
      </div>

      {projects.length === 0 ? (
        <div className="card text-center py-12">
          <div className="text-gray-400 mb-4">
            <svg className="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900">プロジェクトがありません</h3>
          <p className="mt-2 text-gray-600">新規プロジェクトを作成して始めましょう</p>
          <button
            onClick={() => router.push('/projects/new')}
            className="btn btn-primary mt-6"
          >
            最初のプロジェクトを作成
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <div
              key={project.id}
              className="card hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => router.push(`/projects/${project.id}`)}
            >
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                {project.name}
              </h3>
              
              {project.description && (
                <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                  {project.description}
                </p>
              )}
              
              <div className="grid grid-cols-2 gap-2 text-sm mb-4">
                {project.country && (
                  <div>
                    <span className="text-gray-500">国:</span>
                    <span className="ml-2 font-medium">{project.country}</span>
                  </div>
                )}
                {project.currency && (
                  <div>
                    <span className="text-gray-500">通貨:</span>
                    <span className="ml-2 font-medium">{project.currency}</span>
                  </div>
                )}
              </div>
              
              <div className="border-t pt-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-600">進捗</span>
                  <span className="text-sm font-medium">
                    {project.answered_questions} / {project.total_questions}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary-600 h-2 rounded-full transition-all"
                    style={{
                      width: `${project.total_questions > 0 
                        ? (project.answered_questions / project.total_questions) * 100 
                        : 0}%`
                    }}
                  />
                </div>
              </div>
              
              <div className="mt-4 flex gap-2">
                <span className="status-badge status-done">
                  完了: {project.backlog_done}
                </span>
                <span className="status-badge status-ready">
                  対応可: {project.backlog_ready}
                </span>
                <span className="status-badge status-blocked">
                  前の設定が未完了: {project.backlog_blocked}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
