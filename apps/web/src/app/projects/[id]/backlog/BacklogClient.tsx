'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { backlogAPI } from '@/lib/api-client';
import { BacklogItem, BacklogStatus } from '@/lib/types';
import HelpButton from '@/components/HelpButton';

export default function BacklogPage() {
  const router = useRouter();
  const params = useParams();
  const projectId = parseInt(params.id as string);

  const [items, setItems] = useState<BacklogItem[]>([]);
  const [filteredItems, setFilteredItems] = useState<BacklogItem[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadBacklog();
  }, [projectId]);

  useEffect(() => {
    // フィルタリング
    if (statusFilter === 'ALL') {
      setFilteredItems(items);
    } else {
      setFilteredItems(items.filter(item => item.status === statusFilter));
    }
  }, [statusFilter, items]);

  const loadBacklog = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await backlogAPI.list(projectId);
      setItems(data);
    } catch (err: any) {
      setError(err.message || 'バックログの読み込みに失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadgeClass = (status: BacklogStatus) => {
    switch (status) {
      case 'DONE':
        return 'status-badge status-done';
      case 'READY':
        return 'status-badge status-ready';
      case 'BLOCKED':
        return 'status-badge status-blocked';
      case 'PENDING':
        return 'status-badge status-pending';
      default:
        return 'status-badge';
    }
  };

  const getStatusText = (status: BacklogStatus) => {
    switch (status) {
      case 'DONE':
        return '✅ 完了';
      case 'READY':
        return '🟢 対応可能';
      case 'BLOCKED':
        return '🔴 前の設定が未完了';
      case 'PENDING':
        return '⚪ 保留';
      default:
        return status;
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
          <button onClick={loadBacklog} className="btn btn-primary mt-4">
            再試行
          </button>
        </div>
      </div>
    );
  }

  const stats = {
    total: items.length,
    done: items.filter(i => i.status === 'DONE').length,
    ready: items.filter(i => i.status === 'READY').length,
    blocked: items.filter(i => i.status === 'BLOCKED').length,
    pending: items.filter(i => i.status === 'PENDING').length,
  };

  return (
    <div>
      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">バックログ</h1>
          <p className="mt-2 text-gray-600">設定項目の一覧と依存関係</p>
        </div>
        <div className="flex gap-3">
          <HelpButton pageKey="backlog" />
          <button
            onClick={() => router.push(`/projects/${projectId}`)}
            className="btn btn-secondary"
          >
            ← プロジェクトに戻る
          </button>
        </div>
      </div>

      {/* 統計 */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
        <div className="card">
          <div className="text-sm text-gray-500">全体</div>
          <div className="text-2xl font-bold">{stats.total}</div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-500">完了</div>
          <div className="text-2xl font-bold text-green-600">{stats.done}</div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-500">対応可能</div>
          <div className="text-2xl font-bold text-blue-600">{stats.ready}</div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-500">前の設定が未完了</div>
          <div className="text-2xl font-bold text-red-600">{stats.blocked}</div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-500">保留</div>
          <div className="text-2xl font-bold text-gray-600">{stats.pending}</div>
        </div>
      </div>

      {/* フィルタ */}
      <div className="mb-6">
        <div className="flex gap-2">
          {['ALL', 'READY', 'BLOCKED', 'PENDING', 'DONE'].map((filter) => (
            <button
              key={filter}
              onClick={() => setStatusFilter(filter)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                statusFilter === filter
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {filter === 'ALL' ? 'すべて' : filter === 'BLOCKED' ? '前の設定が未完了' : filter}
            </button>
          ))}
        </div>
      </div>

      {/* テーブル */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  タイトル
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  優先度
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ステータス
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  依存関係
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  操作
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredItems.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                    該当する項目がありません
                  </td>
                </tr>
              ) : (
                filteredItems.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">
                      {item.config_item_id}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      <div className="font-medium">{item.config_item?.title}</div>
                      {item.config_item?.description && (
                        <div className="text-gray-500 text-xs mt-1 line-clamp-2">
                          {item.config_item.description}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        item.config_item?.priority === 'P0'
                          ? 'bg-red-100 text-red-800'
                          : item.config_item?.priority === 'P1'
                          ? 'bg-orange-100 text-orange-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {item.config_item?.priority || 'N/A'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={getStatusBadgeClass(item.status)}>
                        {getStatusText(item.status)}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {item.config_item?.depends_on && item.config_item.depends_on.length > 0 ? (
                        <div className="space-y-1">
                          {item.config_item.depends_on.map((dep) => (
                            <div key={dep} className="text-xs font-mono">{dep}</div>
                          ))}
                        </div>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {item.answered ? (
                        <button
                          onClick={() => router.push(`/projects/${projectId}/wizard?edit=${item.config_item_id}`)}
                          className="inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-md text-amber-700 bg-amber-50 hover:bg-amber-100 border border-amber-200 transition-colors"
                        >
                          <svg className="w-3.5 h-3.5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                          編集
                        </button>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 次に進むアクション */}
      {stats.ready > 0 && (
        <div className="mt-8 card bg-blue-50 border-blue-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-blue-900">
                対応可能な質問が {stats.ready} 件あります
              </h3>
              <p className="text-sm text-blue-700 mt-1">
                ウィザードで回答を進めましょう
              </p>
            </div>
            <button
              onClick={() => router.push(`/projects/${projectId}/wizard`)}
              className="btn btn-primary"
            >
              ウィザードを続ける
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
