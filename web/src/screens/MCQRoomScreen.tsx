import React, { useState, useEffect } from 'react';
import {
  CheckCircle2,
  Clock,
  Shuffle,
  ChevronRight,
  ChevronLeft,
  Check,
  X,
  AlertTriangle,
} from 'lucide-react';
import { db, type DbQuestion, type DbTopic } from '../lib/db';
import { recordAttempt } from '../lib/databaseInit';
import { MathView } from '../components/MathView';
import { type ScreenType } from '../components/Navbar';

interface MCQRoomScreenProps {
  selectedTopicId: string | null;
  onNavigate: (screen: ScreenType) => void;
  onSelectTopic: (topicId: string) => void;
}

export const MCQRoomScreen: React.FC<MCQRoomScreenProps> = ({
  selectedTopicId,
  onNavigate,
  onSelectTopic,
}) => {
  const [topics, setTopics] = useState<DbTopic[]>([]);
  const [activeTopicId, setActiveTopicId] = useState<string>('all');
  const [questions, setQuestions] = useState<DbQuestion[]>([]);
  const [currentIndex, setCurrentIndex] = useState<number>(0);

  // Modes: 'practice' (instant feedback) or 'exam' (delayed feedback / timer)
  const [mode, setMode] = useState<'practice' | 'exam'>('practice');
  const [onlyMissed, setOnlyMissed] = useState<boolean>(false);

  // State for current session
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, string>>({});
  const [submittedAnswers, setSubmittedAnswers] = useState<Record<string, boolean>>({});
  const [elapsedSeconds, setElapsedSeconds] = useState<number>(0);
  const [examSubmitted, setExamSubmitted] = useState<boolean>(false);

  // Load Topics & Questions
  useEffect(() => {
    async function loadData() {
      const allTopics = await db.topics.toArray();
      setTopics(allTopics);

      if (selectedTopicId) {
        setActiveTopicId(selectedTopicId);
      }
    }
    loadData();
  }, [selectedTopicId]);

  useEffect(() => {
    async function fetchQuestions() {
      let qList: DbQuestion[] = [];
      if (activeTopicId === 'all') {
        qList = await db.questions.where('type').equals('mcq').limit(60).toArray();
      } else {
        qList = await db.questions
          .where('topic_id')
          .equals(activeTopicId)
          .and((q) => q.type === 'mcq')
          .toArray();
      }

      if (onlyMissed) {
        const mistakeList = await db.mistakes.where('is_resolved').equals(0 as any).toArray();
        const mistakeQIds = new Set(mistakeList.map((m) => m.question_id));
        qList = qList.filter((q) => mistakeQIds.has(q.id));
      }

      setQuestions(qList);
      setCurrentIndex(0);
      setSelectedAnswers({});
      setSubmittedAnswers({});
      setExamSubmitted(false);
    }
    fetchQuestions();
  }, [activeTopicId, onlyMissed]);

  // Per-question elapsed timer
  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedSeconds((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, [currentIndex]);

  const currentQ = questions[currentIndex];

  const handleSelectOption = (letter: string) => {
    if (!currentQ) return;
    if (mode === 'practice' && submittedAnswers[currentQ.id]) return;
    if (examSubmitted) return;

    setSelectedAnswers((prev) => ({
      ...prev,
      [currentQ.id]: letter,
    }));
  };

  const handlePracticeSubmit = async () => {
    if (!currentQ || submittedAnswers[currentQ.id]) return;
    const chosen = selectedAnswers[currentQ.id];
    if (!chosen) return;

    const isRight = chosen === currentQ.correct_answer;
    setSubmittedAnswers((prev) => ({
      ...prev,
      [currentQ.id]: true,
    }));

    await recordAttempt({
      questionId: currentQ.id,
      topicId: currentQ.topic_id,
      topicName: currentQ.topic_name,
      type: 'mcq',
      questionStem: currentQ.stem,
      chosenAnswer: chosen,
      isCorrect: isRight,
      scoreObtained: isRight ? 1 : 0,
      maxScore: 1,
      timeSpentSeconds: elapsedSeconds,
      mistakeCategory: isRight ? undefined : 'calculation',
      diagnosisText: isRight
        ? undefined
        : currentQ.distractor_explanations?.[chosen] || 'ভুল অপশন নির্বাচিত হয়েছে।',
    });
  };

  const handleExamSubmitAll = async () => {
    setExamSubmitted(true);
    for (const q of questions) {
      const chosen = selectedAnswers[q.id];
      const isRight = chosen === q.correct_answer;
      if (chosen) {
        await recordAttempt({
          questionId: q.id,
          topicId: q.topic_id,
          topicName: q.topic_name,
          type: 'mcq',
          questionStem: q.stem,
          chosenAnswer: chosen,
          isCorrect: isRight,
          scoreObtained: isRight ? 1 : 0,
          maxScore: 1,
          timeSpentSeconds: 40,
        });
      }
    }
  };

  const handleShuffle = () => {
    const shuffled = [...questions].sort(() => Math.random() - 0.5);
    setQuestions(shuffled);
    setCurrentIndex(0);
    setSelectedAnswers({});
    setSubmittedAnswers({});
  };

  const answeredCount = Object.keys(selectedAnswers).length;

  return (
    <div className="space-y-6 pb-12 max-w-5xl mx-auto">
      {/* Top Header Controls */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl p-5 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-xs text-emerald-600 dark:text-emerald-400 font-semibold mb-1">
            <CheckCircle2 className="w-4 h-4" />
            <span>বাংলাদেশ সরকারি ও ব্যাংক পরীক্ষা স্প্রিন্ট</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white">
            এমসিকিউ পরীক্ষা ও প্র্যাকটিস রুম
          </h1>
        </div>

        {/* Filters & Mode Switch */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Mode Switch: Practice vs Exam */}
          <div className="inline-flex rounded-xl bg-slate-100 dark:bg-slate-800 p-1 border border-slate-200 dark:border-slate-700">
            <button
              onClick={() => {
                setMode('practice');
                setExamSubmitted(false);
              }}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${
                mode === 'practice'
                  ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm'
                  : 'text-slate-500 hover:text-slate-900'
              }`}
            >
              অনুশীলন মোড
            </button>
            <button
              onClick={() => {
                setMode('exam');
                setExamSubmitted(false);
              }}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${
                mode === 'exam'
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'text-slate-500 hover:text-slate-900'
              }`}
            >
              পরীক্ষা মোড
            </button>
          </div>

          {/* Topic Select */}
          <select
            value={activeTopicId}
            onChange={(e) => setActiveTopicId(e.target.value)}
            className="text-xs font-semibold px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white"
          >
            <option value="all">
              সকল অধ্যায় (মিক্সড স্প্রিন্ট)
            </option>
            {topics.map((t) => (
              <option key={t.id} value={t.id}>
                {t.title_bn}
              </option>
            ))}
          </select>

          {/* Shuffle button */}
          <button
            onClick={handleShuffle}
            className="p-2 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
            title="প্রশ্ন অদলবদল করুন"
          >
            <Shuffle className="w-4 h-4" />
          </button>

          {/* Filter missed only */}
          <button
            onClick={() => setOnlyMissed(!onlyMissed)}
            className={`px-3 py-2 rounded-xl border text-xs font-semibold transition ${
              onlyMissed
                ? 'bg-rose-50 border-rose-300 text-rose-700 dark:bg-rose-950 dark:border-rose-800 dark:text-rose-300'
                : 'border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400'
            }`}
          >
            ভুল প্রশ্নগুলো
          </button>
        </div>
      </div>

      {questions.length === 0 ? (
        <div className="bg-white dark:bg-slate-900 p-12 rounded-2xl border border-slate-200 dark:border-slate-800 text-center text-slate-500">
          <AlertTriangle className="w-8 h-8 text-amber-500 mx-auto mb-2 opacity-80" />
          <p className="text-sm font-semibold">
            নির্বাচিত ফিল্টারে কোনো MCQ প্রশ্ন পাওয়া যায়নি।
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Question Index Progress & Question Timer */}
          <div className="flex items-center justify-between text-xs text-slate-500 px-1">
            <span className="font-bold text-slate-800 dark:text-slate-200">
              প্রশ্ন {currentIndex + 1} / {questions.length}
            </span>

            <div className="flex items-center space-x-2 text-slate-500">
              <Clock className="w-3.5 h-3.5 text-emerald-600" />
              <span>
                {Math.floor(elapsedSeconds / 60)}:
                {String(elapsedSeconds % 60).padStart(2, '0')}
              </span>
            </div>
          </div>

          {/* The Main Question Card */}
          <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 sm:p-8 border border-slate-200 dark:border-slate-800 shadow-sm space-y-5">
            {/* Exam Tag */}
            <div className="flex items-center justify-between">
              {currentQ.citation ? (
                <span className="text-[11px] font-bold px-2.5 py-1 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                  {currentQ.citation}
                </span>
              ) : (
                <span className="text-[11px] text-slate-400">{currentQ.topic_name}</span>
              )}

              <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400">
                {currentQ.topic_name}
              </span>
            </div>

            {/* Question Stem */}
            <div className="text-base sm:text-lg font-bold text-slate-900 dark:text-white leading-relaxed">
              <MathView content={currentQ.stem} />
            </div>

            {/* Options */}
            <div className="space-y-2.5 pt-2">
              {currentQ.options.map((opt, idx) => {
                const letter = ['A', 'B', 'C', 'D'][idx] || 'A';
                const isSelected = selectedAnswers[currentQ.id] === letter;
                const isSubmitted =
                  mode === 'practice'
                    ? submittedAnswers[currentQ.id]
                    : examSubmitted;

                let optClass =
                  'bg-slate-50 dark:bg-slate-800/80 border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200 hover:border-emerald-400';

                if (isSubmitted) {
                  if (letter === currentQ.correct_answer) {
                    optClass =
                      'bg-emerald-50 dark:bg-emerald-950/80 border-emerald-500 text-emerald-900 dark:text-emerald-200 ring-2 ring-emerald-500/20';
                  } else if (isSelected) {
                    optClass =
                      'bg-rose-50 dark:bg-rose-950/80 border-rose-500 text-rose-900 dark:text-rose-200 ring-2 ring-rose-500/20';
                  }
                } else if (isSelected) {
                  optClass =
                    'border-emerald-500 bg-emerald-50/60 dark:bg-emerald-950/40 text-emerald-900 dark:text-emerald-200 ring-2 ring-emerald-500/20';
                }

                return (
                  <div
                    key={idx}
                    onClick={() => handleSelectOption(letter)}
                    className={`p-4 rounded-xl border text-sm font-medium cursor-pointer transition flex items-center justify-between ${optClass}`}
                  >
                    <MathView content={opt} />
                    {isSubmitted && (
                      <div className="ml-3 shrink-0">
                        {letter === currentQ.correct_answer ? (
                          <Check className="w-5 h-5 text-emerald-600 font-bold" />
                        ) : isSelected ? (
                          <X className="w-5 h-5 text-rose-600 font-bold" />
                        ) : null}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Practice Mode Submit / Feedback */}
            {mode === 'practice' && (
              <div className="pt-2">
                {!submittedAnswers[currentQ.id] ? (
                  <button
                    disabled={!selectedAnswers[currentQ.id]}
                    onClick={handlePracticeSubmit}
                    className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-bold text-xs shadow-sm transition"
                  >
                    উত্তর যাচাই করুন
                  </button>
                ) : (
                  <div className="space-y-4 pt-2">
                    {/* Correctness banner */}
                    <div
                      className={`p-3.5 rounded-xl text-xs font-bold ${
                        selectedAnswers[currentQ.id] === currentQ.correct_answer
                          ? 'bg-emerald-50 dark:bg-emerald-950/60 text-emerald-900 dark:text-emerald-200 border border-emerald-300'
                          : 'bg-rose-50 dark:bg-rose-950/60 text-rose-900 dark:text-rose-200 border border-rose-300'
                      }`}
                    >
                      {selectedAnswers[currentQ.id] === currentQ.correct_answer
                        ? '✓ সঠিক উত্তর!'
                        : `✗ ভুল উত্তর! সঠিক উত্তর ছিল: ${currentQ.correct_answer}`}
                    </div>

                    {/* Distractor Trap Analysis */}
                    {selectedAnswers[currentQ.id] !== currentQ.correct_answer && (
                      <div className="bg-amber-50 dark:bg-amber-950/30 p-3.5 rounded-xl border border-amber-200 dark:border-amber-800 text-xs">
                        <strong className="text-amber-900 dark:text-amber-200 block mb-1">
                          ফাঁদ বিশ্লেষণ:
                        </strong>
                        <p className="text-slate-700 dark:text-slate-300">
                          {currentQ.distractor_explanations?.[
                            selectedAnswers[currentQ.id] || 'B'
                          ] || 'এই বিকল্পে গাণিতিক চিহ্ন বা রূপান্তরে ভুল রয়েছে।'}
                        </p>
                      </div>
                    )}

                    {/* Detailed Worked Solution */}
                    <div className="bg-slate-50 dark:bg-slate-800/60 p-4 rounded-xl border border-slate-200 dark:border-slate-700 text-xs space-y-2">
                      <span className="font-bold text-slate-800 dark:text-slate-200 block">
                        ব্যাখ্যা সহ সমাধান:
                      </span>
                      <div className="text-slate-700 dark:text-slate-300 leading-relaxed">
                        <MathView content={currentQ.solution} />
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Exam Mode Result Box if Submitted */}
            {mode === 'exam' && examSubmitted && (
              <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs space-y-2">
                <span className="font-bold text-slate-900 dark:text-white block">
                  ব্যাখ্যা সহ সমাধান:
                </span>
                <MathView content={currentQ.solution} />
              </div>
            )}

            {/* Pagination Controls */}
            <div className="flex items-center justify-between pt-4 border-t border-slate-100 dark:border-slate-800">
              <button
                disabled={currentIndex === 0}
                onClick={() => {
                  setCurrentIndex((prev) => prev - 1);
                  setElapsedSeconds(0);
                }}
                className="flex items-center space-x-1 px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-xs font-semibold disabled:opacity-40 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
              >
                <ChevronLeft className="w-4 h-4" />
                <span>পূর্ববর্তী</span>
              </button>

              {mode === 'exam' && !examSubmitted && (
                <button
                  onClick={handleExamSubmitAll}
                  className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-sm transition"
                >
                  পরীক্ষা শেষ করুন ({answeredCount}/{questions.length})
                </button>
              )}

              <button
                disabled={currentIndex === questions.length - 1}
                onClick={() => {
                  setCurrentIndex((prev) => prev + 1);
                  setElapsedSeconds(0);
                }}
                className="flex items-center space-x-1 px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 dark:bg-emerald-600 dark:hover:bg-emerald-700 text-white text-xs font-semibold disabled:opacity-40 transition"
              >
                <span>পরবর্তী প্রশ্ন</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
