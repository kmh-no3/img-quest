'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { projectsAPI } from '@/lib/api-client';
import { ProjectCreate, ProjectMode } from '@/lib/types';
import HelpButton from '@/components/HelpButton';

export default function NewProjectPage() {
  const router = useRouter();
  const [formData, setFormData] = useState<ProjectCreate>({
    name: '',
    mode: 'BEGINNER',  // デフォルトは初心者モード
    country: 'JP',
    currency: 'JPY',
    industry: '',
    company_count: 1,
    description: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim()) {
      setError('プロジェクト名を入力してください');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const project = await projectsAPI.create(formData);
      // ウィザードへ遷移
      router.push(`/projects/${project.id}/wizard`);
    } catch (err: any) {
      setError(err.message || 'プロジェクトの作成に失敗しました');
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8 flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">新規プロジェクト作成</h1>
          <p className="mt-2 text-gray-600">
            基本情報を入力してプロジェクトを作成します
          </p>
        </div>
        <HelpButton pageKey="project-create" />
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="card">
        <div className="space-y-6">
          {/* モード選択 */}
          <div>
            <label className="label">
              設定モード <span className="text-red-500">*</span>
            </label>
            <p className="text-sm text-gray-600 mb-3">
              あなたのSAP経験に合わせてモードを選択してください
            </p>
            <div className="grid grid-cols-2 gap-4">
              {/* 初心者モード */}
              <button
                type="button"
                onClick={() => setFormData({ ...formData, mode: 'BEGINNER' })}
                className={`p-4 border-2 rounded-lg text-left transition-all ${
                  formData.mode === 'BEGINNER'
                    ? 'border-primary-600 bg-primary-50'
                    : 'border-gray-200 bg-white hover:border-gray-300'
                }`}
              >
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    {formData.mode === 'BEGINNER' ? (
                      <div className="w-5 h-5 rounded-full bg-primary-600 flex items-center justify-center">
                        <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 12 12">
                          <path d="M3.707 5.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4a1 1 0 00-1.414-1.414L5 6.586 3.707 5.293z" />
                        </svg>
                      </div>
                    ) : (
                      <div className="w-5 h-5 rounded-full border-2 border-gray-300"></div>
                    )}
                  </div>
                  <div className="ml-3">
                    <div className="font-semibold text-gray-900">カンタン設定ver</div>
                    <div className="text-sm text-gray-600 mt-1">
                      SAP初学者向け。わかりやすい説明と推奨設定で迷わず進められます。
                    </div>
                    <div className="mt-2 inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800">
                      おすすめ
                    </div>
                  </div>
                </div>
              </button>

              {/* 玄人モード */}
              <button
                type="button"
                onClick={() => setFormData({ ...formData, mode: 'EXPERT' })}
                className={`p-4 border-2 rounded-lg text-left transition-all ${
                  formData.mode === 'EXPERT'
                    ? 'border-primary-600 bg-primary-50'
                    : 'border-gray-200 bg-white hover:border-gray-300'
                }`}
              >
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    {formData.mode === 'EXPERT' ? (
                      <div className="w-5 h-5 rounded-full bg-primary-600 flex items-center justify-center">
                        <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 12 12">
                          <path d="M3.707 5.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4a1 1 0 00-1.414-1.414L5 6.586 3.707 5.293z" />
                        </svg>
                      </div>
                    ) : (
                      <div className="w-5 h-5 rounded-full border-2 border-gray-300"></div>
                    )}
                  </div>
                  <div className="ml-3">
                    <div className="font-semibold text-gray-900">完全マニュアルver</div>
                    <div className="text-sm text-gray-600 mt-1">
                      玄人向け。全ての設定項目を細かくカスタマイズできます。
                    </div>
                    <div className="mt-2 inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
                      上級者向け
                    </div>
                  </div>
                </div>
              </button>
            </div>
          </div>

          <div>
            <label className="label">
              プロジェクト名 <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              className="input"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="例: XYZ社 FI導入プロジェクト"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">国/地域</label>
              <select
                className="input"
                value={formData.country || ''}
                onChange={(e) => setFormData({ ...formData, country: e.target.value })}
              >
                <option value="JP">日本</option>
                <option value="US">アメリカ</option>
                <option value="EU">EU</option>
                <option value="OTHER">その他</option>
              </select>
            </div>

            <div>
              <label className="label">通貨</label>
              <select
                className="input"
                value={formData.currency || ''}
                onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
              >
                <option value="JPY">JPY（日本円）</option>
                <option value="USD">USD（米ドル）</option>
                <option value="EUR">EUR（ユーロ）</option>
                <option value="OTHER">その他</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">業種</label>
              <input
                type="text"
                className="input"
                value={formData.industry || ''}
                onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                placeholder="例: 製造業"
              />
            </div>

            <div>
              <label className="label">会社数</label>
              <input
                type="number"
                className="input"
                value={formData.company_count || 1}
                onChange={(e) => setFormData({ ...formData, company_count: parseInt(e.target.value) || 1 })}
                min="1"
              />
            </div>
          </div>

          <div>
            <label className="label">説明</label>
            <textarea
              className="input"
              rows={4}
              value={formData.description || ''}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="プロジェクトの概要や目的を記入してください"
            />
          </div>
        </div>

        <div className="mt-8 flex gap-4">
          <button
            type="button"
            onClick={() => router.push('/')}
            className="btn btn-secondary flex-1"
            disabled={loading}
          >
            キャンセル
          </button>
          <button
            type="submit"
            className="btn btn-primary flex-1"
            disabled={loading}
          >
            {loading ? '作成中...' : '作成してウィザードを開始'}
          </button>
        </div>
      </form>
    </div>
  );
}
