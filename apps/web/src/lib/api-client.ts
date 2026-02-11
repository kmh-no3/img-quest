// APIクライアント

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'APIError';
  }
}

async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_URL}${endpoint}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    let errorMessage = `API Error: ${response.status}`;
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorMessage;
    } catch {
      // JSON解析失敗時はデフォルトメッセージを使用
    }
    throw new APIError(response.status, errorMessage);
  }

  // 204 No Contentの場合はnullを返す
  if (response.status === 204) {
    return null as T;
  }

  return response.json();
}

// ========== Projects ==========

export const projectsAPI = {
  list: () => fetchAPI<any[]>('/api/projects'),
  
  get: (id: number) => fetchAPI<any>(`/api/projects/${id}`),
  
  create: (data: any) =>
    fetchAPI<any>('/api/projects', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  update: (id: number, data: any) =>
    fetchAPI<any>(`/api/projects/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  
  delete: (id: number) =>
    fetchAPI<void>(`/api/projects/${id}`, {
      method: 'DELETE',
    }),
};

// ========== Wizard ==========

export const wizardAPI = {
  getNextQuestion: (projectId: number) =>
    fetchAPI<any>(`/api/projects/${projectId}/wizard/questions`),
  
  getQuestionById: (projectId: number, configItemId: string) =>
    fetchAPI<any>(`/api/projects/${projectId}/wizard/questions/${configItemId}`),
  
  getAnswersForItem: (projectId: number, configItemId: string) =>
    fetchAPI<Record<string, any>>(`/api/projects/${projectId}/wizard/answers/${configItemId}`),
  
  submitAnswer: (projectId: number, data: any) =>
    fetchAPI<any>(`/api/projects/${projectId}/wizard/answers`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  getProgress: (projectId: number) =>
    fetchAPI<any>(`/api/projects/${projectId}/wizard/progress`),
  
  getDecisions: (projectId: number) =>
    fetchAPI<any[]>(`/api/projects/${projectId}/wizard/decisions`),
};

// ========== Backlog ==========

export const backlogAPI = {
  list: (projectId: number, statusFilter?: string) => {
    const params = statusFilter ? `?status_filter=${statusFilter}` : '';
    return fetchAPI<any[]>(`/api/projects/${projectId}/backlog${params}`);
  },
  
  getGraph: (projectId: number) =>
    fetchAPI<any>(`/api/projects/${projectId}/backlog/graph`),
  
  getSummary: (projectId: number) =>
    fetchAPI<any>(`/api/projects/${projectId}/backlog/summary`),
  
  updateItem: (projectId: number, itemId: number, data: any) =>
    fetchAPI<any>(`/api/projects/${projectId}/backlog/${itemId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
};

// ========== Artifacts ==========

export const artifactsAPI = {
  generate: (projectId: number, artifactTypes?: string[]) =>
    fetchAPI<any[]>(`/api/projects/${projectId}/artifacts/generate`, {
      method: 'POST',
      body: JSON.stringify({ artifact_types: artifactTypes }),
    }),
  
  list: (projectId: number) =>
    fetchAPI<any[]>(`/api/projects/${projectId}/artifacts`),
  
  getByType: (projectId: number, artifactType: string) =>
    fetchAPI<any>(`/api/projects/${projectId}/artifacts/${artifactType}`),
  
  downloadUrl: (projectId: number, artifactType: string) =>
    `${API_URL}/api/projects/${projectId}/artifacts/${artifactType}/download`,
};

export { APIError };
