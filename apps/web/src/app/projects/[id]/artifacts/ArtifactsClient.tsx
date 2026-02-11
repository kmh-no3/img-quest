'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { artifactsAPI } from '@/lib/api-client';
import { Artifact, ArtifactType } from '@/lib/types';
import HelpButton from '@/components/HelpButton';

const ARTIFACT_TYPES: { value: ArtifactType; label: string; description: string }[] = [
  {
    value: 'DECISION_LOG',
    label: 'Decision Log',
    description: '決定事項の一覧を時系列で記録'
  },
  {
    value: 'CONFIG_WORKBOOK',
    label: 'Config Workbook',
    description: '必要な設定項目の一覧と現在のステータス'
  },
  {
    value: 'TEST_VIEW',
    label: 'Test View',
    description: 'テスト観点とチェックリスト'
  },
  {
    value: 'MIGRATION_VIEW',
    label: 'Migration View',
    description: '移行対象のマスタデータ一覧'
  },
];

export default function ArtifactsPage() {
  const router = useRouter();
  const params = useParams();
  const projectId = parseInt(params.id as string);

  const [artifacts, setArtifacts] = useState<Record<ArtifactType, Artifact | null>>({
    DECISION_LOG: null,
    CONFIG_WORKBOOK: null,
    TEST_VIEW: null,
    MIGRATION_VIEW: null,
  });
  const [activeTab, setActiveTab] = useState<ArtifactType>('DECISION_LOG');
  const [generating, setGenerating] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadArtifacts();
  }, [projectId]);

  const loadArtifacts = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await artifactsAPI.list(projectId);
      
      // 各タイプの最新成果物を取得
      const artifactMap: Record<ArtifactType, Artifact | null> = {
        DECISION_LOG: null,
        CONFIG_WORKBOOK: null,
        TEST_VIEW: null,
        MIGRATION_VIEW: null,
      };
      
      data.forEach((artifact: Artifact) => {
        if (!artifactMap[artifact.artifact_type] || 
            new Date(artifact.created_at) > new Date(artifactMap[artifact.artifact_type]!.created_at)) {
          artifactMap[artifact.artifact_type] = artifact;
        }
      });
      
      setArtifacts(artifactMap);
    } catch (err: any) {
      setError(err.message || '成果物の読み込みに失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    try {
      setGenerating(true);
      setError(null);
      await artifactsAPI.generate(projectId);
      await loadArtifacts();
    } catch (err: any) {
      setError(err.message || '成果物の生成に失敗しました');
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = (artifactType: ArtifactType) => {
    const url = artifactsAPI.downloadUrl(projectId, artifactType);
    window.open(url, '_blank');
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

  const currentArtifact = artifacts[activeTab];
  const hasAnyArtifact = Object.values(artifacts).some(a => a !== null);

  return (
    <div>
      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">成果物</h1>
          <p className="mt-2 text-gray-600">決定事項と設定一覧をエクスポート</p>
        </div>
        <div className="flex gap-3">
          <HelpButton pageKey="artifacts" />
          <button
            onClick={() => router.push(`/projects/${projectId}`)}
            className="btn btn-secondary"
          >
            ← プロジェクトに戻る
          </button>
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="btn btn-primary"
          >
            {generating ? '生成中...' : hasAnyArtifact ? '再生成' : '成果物を生成'}
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {!hasAnyArtifact ? (
        <div className="card text-center py-12">
          <div className="text-gray-400 mb-4">
            <svg className="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900">成果物がまだ生成されていません</h3>
          <p className="mt-2 text-gray-600">「成果物を生成」ボタンをクリックして作成してください</p>
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="btn btn-primary mt-6"
          >
            {generating ? '生成中...' : '成果物を生成'}
          </button>
        </div>
      ) : (
        <div>
          {/* タブ */}
          <div className="border-b border-gray-200 mb-6">
            <nav className="-mb-px flex space-x-8">
              {ARTIFACT_TYPES.map((type) => (
                <button
                  key={type.value}
                  onClick={() => setActiveTab(type.value)}
                  className={`
                    py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap
                    ${activeTab === type.value
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }
                  `}
                >
                  {type.label}
                  {artifacts[type.value] && (
                    <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                      生成済
                    </span>
                  )}
                </button>
              ))}
            </nav>
          </div>

          {/* コンテンツ */}
          <div className="card">
            {currentArtifact ? (
              <div>
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900">
                      {ARTIFACT_TYPES.find(t => t.value === activeTab)?.label}
                    </h2>
                    <p className="text-sm text-gray-600 mt-1">
                      {ARTIFACT_TYPES.find(t => t.value === activeTab)?.description}
                    </p>
                    <p className="text-xs text-gray-500 mt-2">
                      生成日時: {new Date(currentArtifact.created_at).toLocaleString('ja-JP')}
                    </p>
                    {currentArtifact.tbd_count > 0 && (
                      <div className="mt-2 inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
                        ⚠️ 未決定項目: {currentArtifact.tbd_count} 件
                      </div>
                    )}
                  </div>
                  <button
                    onClick={() => handleDownload(activeTab)}
                    className="btn btn-primary"
                  >
                    📥 ダウンロード
                  </button>
                </div>

                {/* Markdownプレビュー */}
                <div className="border-t pt-6">
                  <div className="bg-gray-50 rounded-lg p-6 max-h-[600px] overflow-y-auto">
                    <pre className="whitespace-pre-wrap font-mono text-sm text-gray-800">
                      {currentArtifact.content}
                    </pre>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500">
                <p>この成果物はまだ生成されていません</p>
                <button
                  onClick={handleGenerate}
                  disabled={generating}
                  className="btn btn-primary mt-4"
                >
                  生成する
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ヘルプ */}
      {hasAnyArtifact && (
        <div className="mt-8 card bg-blue-50 border-blue-200">
          <h3 className="font-semibold text-blue-900 mb-2">💡 成果物の活用方法</h3>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• <strong>Decision Log</strong>: プロジェクトの決定事項を関係者と共有</li>
            <li>• <strong>Config Workbook</strong>: 設定作業のチェックリストとして活用</li>
            <li>• <strong>Test View</strong>: テストケース作成の参考資料に</li>
            <li>• <strong>Migration View</strong>: データ移行計画の策定に活用</li>
          </ul>
        </div>
      )}
    </div>
  );
}
