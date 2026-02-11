// API型定義

export type ProjectMode = 'BEGINNER' | 'EXPERT';

export interface Project {
  id: number;
  name: string;
  mode: ProjectMode;
  country: string | null;
  currency: string | null;
  industry: string | null;
  company_count: number | null;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProjectWithStats extends Project {
  total_questions: number;
  answered_questions: number;
  backlog_ready: number;
  backlog_blocked: number;
  backlog_done: number;
}

export interface ProjectCreate {
  name: string;
  mode: ProjectMode;
  country?: string;
  currency?: string;
  industry?: string;
  company_count?: number;
  description?: string;
}

export interface ConfigItem {
  id: string;
  title: string;
  description: string | null;
  priority: string | null;
  inputs: ConfigItemInput[];
  depends_on: string[];
  produces: string[];
  notes: string[] | null;
}

export interface ConfigItemInput {
  name: string;
  type: string;
  options?: string[];
}

export interface QuestionInput {
  name: string;
  type: string;
  label: string;
  options: string[] | null;
  required: boolean;
  recommended?: any;  // 推奨値（初心者モード用）
  option_labels?: Record<string, string>;  // 選択肢のラベル（初心者モード用）
}

export interface Question {
  config_item_id: string;
  title: string;
  description: string | null;
  inputs: QuestionInput[];
  priority: string;
  progress: number;
  total: number;
  why?: string | null;  // なぜこの質問が必要か（初心者モード用）
}

export interface AnswerSubmit {
  config_item_id: string;
  answers: Record<string, any>;
}

export interface Decision {
  id: number;
  project_id: number;
  config_item_id: string;
  title: string;
  rationale: string | null;
  impact: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export type BacklogStatus = 'PENDING' | 'BLOCKED' | 'READY' | 'DONE';

export interface BacklogItem {
  id: number;
  project_id: number;
  config_item_id: string;
  status: BacklogStatus;
  answered: boolean;
  created_at: string;
  updated_at: string;
  config_item?: ConfigItem;
}

export type ArtifactType = 'DECISION_LOG' | 'CONFIG_WORKBOOK' | 'TEST_VIEW' | 'MIGRATION_VIEW';

export interface Artifact {
  id: number;
  project_id: number;
  artifact_type: ArtifactType;
  content: string;
  tbd_count: number;
  created_at: string;
}

export interface WizardProgress {
  total: number;
  answered: number;
  ready: number;
  blocked: number;
  done: number;
  progress_percentage: number;
}

export interface DependencyGraphNode {
  id: string;
  label: string;
  priority: string;
  status: string;
  answered: boolean;
}

export interface DependencyGraphEdge {
  from: string;
  to: string;
}

export interface DependencyGraph {
  nodes: DependencyGraphNode[];
  edges: DependencyGraphEdge[];
}
