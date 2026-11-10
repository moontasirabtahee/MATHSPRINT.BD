import { db, type DbTopic, type DbQuestion, type DbFormula } from './db';
import curriculumData from '../data/curriculum.json';
import coreQuestionsData from '../data/questions_core.json';
import formulasData from '../data/formulas.json';

const CURRENT_DATA_VERSION = 6;

export async function initializeDatabase() {
  try {
    const settings = await db.settings.toCollection().first();
    const storedVersion = (settings as any)?.data_version || 1;

    // If version is older, refresh topics, questions, and formulas cleanly
    if (!settings || storedVersion < CURRENT_DATA_VERSION) {
      console.log('Upgrading database dataset to version', CURRENT_DATA_VERSION);
      await db.topics.clear();
      await db.questions.clear();
      await db.formulas.clear();

      const topicsToInsert: DbTopic[] = (curriculumData as any[]).map((t) => ({
        ...t,
        status: 'unstarted',
        masteryScore: 0,
      }));
      await db.topics.bulkAdd(topicsToInsert);
      await db.questions.bulkAdd(coreQuestionsData as DbQuestion[]);

      const formulasToInsert: DbFormula[] = (formulasData as any[]).map((f) => ({
        ...f,
        is_memorized: false,
        is_bookmarked: false,
      }));
      await db.formulas.bulkAdd(formulasToInsert);

      const targetDate = new Date(Date.now() + 48 * 60 * 60 * 1000).toISOString();
      if (!settings) {
        await db.settings.add({
          exam_target_date: targetDate,
          preferred_language: 'bn',
          daily_goal_minutes: 180,
          dark_mode: false,
          data_version: CURRENT_DATA_VERSION,
        } as any);
      } else {
        await db.settings.update(settings.id!, {
          data_version: CURRENT_DATA_VERSION,
        } as any);
      }

      console.log('Database upgrade completed to version', CURRENT_DATA_VERSION);
      return;
    }

    const topicCount = await db.topics.count();
    if (topicCount === 0) {
      const topicsToInsert: DbTopic[] = (curriculumData as any[]).map((t) => ({
        ...t,
        status: 'unstarted',
        masteryScore: 0,
      }));
      await db.topics.bulkAdd(topicsToInsert);
    }

    const questionCount = await db.questions.count();
    if (questionCount === 0) {
      await db.questions.bulkAdd(coreQuestionsData as DbQuestion[]);
    }

    const formulaCount = await db.formulas.count();
    if (formulaCount === 0) {
      const formulasToInsert: DbFormula[] = (formulasData as any[]).map((f) => ({
        ...f,
        is_memorized: false,
        is_bookmarked: false,
      }));
      await db.formulas.bulkAdd(formulasToInsert);
    }

    console.log('Database verified successfully.');
  } catch (error) {
    console.error('Failed to initialize database:', error);
  }
}

// Helper to record a question attempt and automatically update mastery, mistakes, and revision queue
export async function recordAttempt(params: {
  questionId: string;
  topicId: string;
  topicName: string;
  type: 'mcq' | 'written';
  questionStem: string;
  chosenAnswer?: string;
  writtenAnswer?: string;
  isCorrect: boolean;
  scoreObtained: number;
  maxScore: number;
  timeSpentSeconds: number;
  mistakeCategory?: 'sign_error' | 'formula_error' | 'algebraic_simplification' | 'substitution' | 'calculation' | 'missing_condition' | 'conceptual';
  diagnosisText?: string;
  rubricBreakdown?: Record<string, number>;
}) {
  const now = new Date().toISOString();

  // 1. Save attempt record
  await db.attempts.add({
    question_id: params.questionId,
    topic_id: params.topicId,
    type: params.type,
    chosen_answer: params.chosenAnswer,
    written_answer: params.writtenAnswer,
    is_correct: params.isCorrect,
    score_obtained: params.scoreObtained,
    max_score: params.maxScore,
    mistake_type: params.mistakeCategory,
    feedback_notes: params.diagnosisText,
    rubric_breakdown: params.rubricBreakdown,
    time_spent_seconds: params.timeSpentSeconds,
    timestamp: now,
  });

  // 2. Handle mistakes and revision queue
  if (!params.isCorrect) {
    const existingMistake = await db.mistakes
      .where('question_id')
      .equals(params.questionId)
      .first();

    if (existingMistake) {
      await db.mistakes.update(existingMistake.id!, {
        incorrect_attempts: existingMistake.incorrect_attempts + 1,
        is_resolved: false,
        last_occurred_at: now,
        diagnosis_text: params.diagnosisText || existingMistake.diagnosis_text,
      });
    } else {
      await db.mistakes.add({
        question_id: params.questionId,
        topic_id: params.topicId,
        topic_name: params.topicName,
        question_stem: params.questionStem,
        mistake_category: params.mistakeCategory || 'calculation',
        diagnosis_text: params.diagnosisText || 'ভুল উত্তর বা হিসাবের ভুল।',
        remedy_text: 'মূল নিয়মটি পুনরায় পড়ে ধাপে ধাপে হিসাব সম্পন্ন করুন।',
        incorrect_attempts: 1,
        is_resolved: false,
        last_occurred_at: now,
      });
    }

    const tier1Time = new Date(Date.now() + 15 * 60 * 1000).toISOString();
    await db.revisionQueue.add({
      question_id: params.questionId,
      topic_id: params.topicId,
      tier: 1,
      scheduled_for: tier1Time,
      status: 'pending',
      created_at: now,
    });
  } else {
    const existingMistake = await db.mistakes
      .where('question_id')
      .equals(params.questionId)
      .first();

    if (existingMistake && !existingMistake.is_resolved) {
      await db.mistakes.update(existingMistake.id!, {
        is_resolved: true,
        resolved_at: now,
      });
    }
  }

  // 3. Recalculate Topic Mastery Score (never fake 100%)
  const topicAttempts = await db.attempts
    .where('topic_id')
    .equals(params.topicId)
    .toArray();

  if (topicAttempts.length > 0) {
    const totalScore = topicAttempts.reduce((acc, a) => acc + a.score_obtained, 0);
    const maxPossible = topicAttempts.reduce((acc, a) => acc + a.max_score, 0);
    const accuracy = maxPossible > 0 ? Math.round((totalScore / maxPossible) * 100) : 0;

    const uniqueQuestionsAttempted = new Set(topicAttempts.map((a) => a.question_id)).size;
    const topic = await db.topics.get(params.topicId);
    const totalQ = topic ? topic.total_questions : 20;
    const coverageFactor = Math.min(1.0, uniqueQuestionsAttempted / Math.min(15, totalQ));

    const finalMastery = Math.round(accuracy * (0.5 + 0.5 * coverageFactor));

    let status: 'unstarted' | 'in_progress' | 'mastered' = 'in_progress';
    if (finalMastery >= 80 && uniqueQuestionsAttempted >= 8) {
      status = 'mastered';
    }

    await db.topics.update(params.topicId, {
      masteryScore: finalMastery,
      status,
      lastStudiedAt: now,
    });
  }
}
