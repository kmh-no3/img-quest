/**
 * APIクライアントのテスト
 */

// fetch をモック
const mockFetch = jest.fn();
global.fetch = mockFetch;

// モジュールを動的インポート（環境変数が設定された後に読み込む）
let projectsAPI: any;
let wizardAPI: any;
let backlogAPI: any;
let artifactsAPI: any;
let APIError: any;

beforeAll(async () => {
  const module = await import('../lib/api-client');
  projectsAPI = module.projectsAPI;
  wizardAPI = module.wizardAPI;
  backlogAPI = module.backlogAPI;
  artifactsAPI = module.artifactsAPI;
  APIError = module.APIError;
});

beforeEach(() => {
  mockFetch.mockClear();
});

describe('projectsAPI', () => {
  test('list() は GET /api/projects を呼ぶ', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => [{ id: 1, name: 'Test' }],
    });

    const result = await projectsAPI.list();
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/projects'),
      expect.objectContaining({
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
        }),
      })
    );
    expect(result).toEqual([{ id: 1, name: 'Test' }]);
  });

  test('create() は POST /api/projects を呼ぶ', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 201,
      json: async () => ({ id: 1, name: 'New Project' }),
    });

    const result = await projectsAPI.create({ name: 'New Project', mode: 'EXPERT' });
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/projects'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ name: 'New Project', mode: 'EXPERT' }),
      })
    );
    expect(result.name).toBe('New Project');
  });

  test('delete() は DELETE を呼ぶ', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 204,
    });

    await projectsAPI.delete(1);
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/projects/1'),
      expect.objectContaining({ method: 'DELETE' })
    );
  });
});

describe('wizardAPI', () => {
  test('getNextQuestion() は GET /wizard/questions を呼ぶ', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({ config_item_id: 'FI-CORE-001', title: 'テスト' }),
    });

    const result = await wizardAPI.getNextQuestion(1);
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/projects/1/wizard/questions'),
      expect.any(Object)
    );
    expect(result.config_item_id).toBe('FI-CORE-001');
  });

  test('submitAnswer() は POST を呼ぶ', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 201,
      json: async () => ({ message: 'Answer submitted successfully' }),
    });

    await wizardAPI.submitAnswer(1, {
      config_item_id: 'FI-CORE-001',
      answers: { fiscal_year_variant: 'K4' },
    });
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/projects/1/wizard/answers'),
      expect.objectContaining({ method: 'POST' })
    );
  });
});

describe('artifactsAPI', () => {
  test('exportJsonUrl() は正しいURLを返す', () => {
    const url = artifactsAPI.exportJsonUrl(42);
    expect(url).toContain('/api/projects/42/artifacts/export/json');
  });

  test('exportXlsxUrl() は正しいURLを返す', () => {
    const url = artifactsAPI.exportXlsxUrl(42);
    expect(url).toContain('/api/projects/42/artifacts/export/xlsx');
  });

  test('downloadUrl() は正しいURLを返す', () => {
    const url = artifactsAPI.downloadUrl(1, 'DECISION_LOG');
    expect(url).toContain('/api/projects/1/artifacts/DECISION_LOG/download');
  });
});

describe('エラーハンドリング', () => {
  test('APIエラー時にAPIErrorをスローする', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: async () => ({ detail: 'Not found' }),
    });

    await expect(projectsAPI.get(999)).rejects.toThrow('Not found');
  });

  test('APIErrorがstatus codeを持つ', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({ detail: 'Server error' }),
    });

    try {
      await projectsAPI.list();
    } catch (error: any) {
      expect(error.status).toBe(500);
      expect(error.name).toBe('APIError');
    }
  });
});
