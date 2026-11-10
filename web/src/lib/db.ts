import Dexie, { type Table } from 'dexie';

export interface DbTopic {
  id: string;
  title_bn: string;
  title_en: string;
  category: string;
  prerequisites: string[];
  estimated_minutes: number;
  total_questions: number;
  mcq_count: number;
  written_count: number;
  concept_summary: {
    core_idea: string;
    when_to_use: string;
    common_traps: string;
  };
  diagnostic_question_id: string | null;
  worked_example_id: string | null;
  formula_ids: string[];
  status?: 'unstarted' | 'in_progress' | 'mastered';
  masteryScore?: number; // 0 to 100
  lastStudiedAt?: string;
}

export interface DbQuestion {
  id: string;
  topic_id: string;
  topic_name: string;
  type: 'mcq' | 'written';
  has_real_options?: boolean;
  stem: string;
  citation: string;
  options: string[];
  correct_answer: string;
  answer_raw?: string;
  solution: string;
  steps: string[];
  marks: number;
  rubric?: {
    formula_selection?: number;
    substitution?: number;
    calculation?: number;
    final_answer?: number;
  };
  distractor_explanations?: Record<string, string>;
  src_hash?: string;
  custom_imported?: boolean;
}

export interface DbFormula {
  id: string;
  topic_id: string;
  topic_name: string;
  category?: string;
  concept_type?: 'formula' | 'concept' | 'shortcut' | 'trap';
  title: string;
  formula: string;
  explanation?: string;
  rules?: string[];
  example?: string;
  src_hash?: string;
  is_memorized?: boolean;
  is_bookmarked?: boolean;
  notes?: string;
}

export interface DbUserAttempt {
  id?: number;
  question_id: string;
  topic_id: string;
  type: 'mcq' | 'written';
  chosen_answer?: string;
  written_answer?: string;
  is_correct: boolean;
  score_obtained: number;
  max_score: number;
  mistake_type?: string;
  feedback_notes?: string;
  rubric_breakdown?: Record<string, number>;
  time_spent_seconds: number;
  timestamp: string;
}

export interface DbMistake {
  id?: number;
  question_id: string;
  topic_id: string;
  topic_name: string;
  question_stem: string;
  mistake_category: 'sign_error' | 'formula_error' | 'algebraic_simplification' | 'substitution' | 'calculation' | 'missing_condition' | 'conceptual';
  diagnosis_text: string;
  remedy_text: string;
  incorrect_attempts: number;
  is_resolved: boolean;
  resolved_at?: string;
  last_occurred_at: string;
}

export interface DbRevisionQueueItem {
  id?: number;
  question_id: string;
  topic_id: string;
  tier: 1 | 2 | 3 | 4; // 1: Immediate Session, 2: Later Today (6h), 3: Tomorrow Morning (18h), 4: Final Sprint
  scheduled_for: string;
  status: 'pending' | 'completed' | 're_failed';
  created_at: string;
}

export interface DbStudySettings {
  id?: number;
  exam_target_date: string; // ISO string
  preferred_language: 'bn' | 'en';
  daily_goal_minutes: number;
  dark_mode: boolean;
}

class MathSprintDatabase extends Dexie {
  topics!: Table<DbTopic, string>;
  questions!: Table<DbQuestion, string>;
  formulas!: Table<DbFormula, string>;
  attempts!: Table<DbUserAttempt, number>;
  mistakes!: Table<DbMistake, number>;
  revisionQueue!: Table<DbRevisionQueueItem, number>;
  settings!: Table<DbStudySettings, number>;

  constructor() {
    super('MathSprintBD_DB');
    this.version(1).stores({
      topics: 'id, category, status, masteryScore',
      questions: 'id, topic_id, type, citation',
      formulas: 'id, topic_id, is_memorized, is_bookmarked',
      attempts: '++id, question_id, topic_id, is_correct, timestamp',
      mistakes: '++id, question_id, topic_id, mistake_category, is_resolved',
      revisionQueue: '++id, question_id, topic_id, tier, scheduled_for, status',
      settings: '++id'
    });
  }
}

export const db = new MathSprintDatabase();

