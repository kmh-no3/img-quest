/**
 * TypeScript型定義の整合性テスト
 * 
 * 型が正しく定義されていることをコンパイル時にチェックする
 */
import type {
  Project,
  ProjectWithStats,
  ProjectCreate,
  ProjectMode,
  ConfigItem,
  ConfigItemInput,
  QuestionInput,
  Question,
  AnswerSubmit,
  Decision,
  BacklogStatus,
  BacklogItem,
  ArtifactType,
  Artifact,
  WizardProgress,
  DependencyGraphNode,
  DependencyGraphEdge,
  DependencyGraph,
} from '../lib/types';

describe('Type definitions', () => {
  test('ProjectMode は BEGINNER と EXPERT を持つ', () => {
    const beginner: ProjectMode = 'BEGINNER';
    const expert: ProjectMode = 'EXPERT';
    expect(beginner).toBe('BEGINNER');
    expect(expert).toBe('EXPERT');
  });

  test('BacklogStatus は正しい値を持つ', () => {
    const statuses: BacklogStatus[] = ['PENDING', 'BLOCKED', 'READY', 'DONE'];
    expect(statuses).toHaveLength(4);
  });

  test('ArtifactType は正しい値を持つ', () => {
    const types: ArtifactType[] = [
      'DECISION_LOG',
      'CONFIG_WORKBOOK',
      'TEST_VIEW',
      'MIGRATION_VIEW',
    ];
    expect(types).toHaveLength(4);
  });

  test('ProjectCreate は最小限の必須フィールドを持つ', () => {
    const project: ProjectCreate = {
      name: 'Test',
      mode: 'EXPERT',
    };
    expect(project.name).toBe('Test');
    expect(project.mode).toBe('EXPERT');
  });

  test('AnswerSubmit は正しい構造を持つ', () => {
    const answer: AnswerSubmit = {
      config_item_id: 'FI-CORE-001',
      answers: { fiscal_year_variant: 'K4' },
    };
    expect(answer.config_item_id).toBe('FI-CORE-001');
    expect(answer.answers.fiscal_year_variant).toBe('K4');
  });

  test('DependencyGraph は nodes と edges を持つ', () => {
    const graph: DependencyGraph = {
      nodes: [
        { id: 'A', label: 'Item A', priority: 'P0', status: 'READY', answered: false },
      ],
      edges: [
        { from: 'A', to: 'B' },
      ],
    };
    expect(graph.nodes).toHaveLength(1);
    expect(graph.edges).toHaveLength(1);
  });

  test('WizardProgress は全てのフィールドを持つ', () => {
    const progress: WizardProgress = {
      total: 10,
      answered: 3,
      ready: 2,
      blocked: 5,
      done: 3,
      progress_percentage: 30.0,
    };
    expect(progress.progress_percentage).toBe(30.0);
  });
});
