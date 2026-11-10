import React, { useState, useEffect } from 'react';
import {
  PenTool,
  Eye,
  EyeOff,
  ChevronRight,
  ChevronLeft,
  CheckCircle2,
  RotateCcw,
  BookOpen,
  Check,
  Sparkles,
} from 'lucide-react';
import { db, type DbQuestion, type DbTopic } from '../lib/db';
import { recordAttempt } from '../lib/databaseInit';
import { MathView } from '../components/MathView';
import { type ScreenType } from '../components/Navbar';

interface WrittenRoomScreenProps {
  selectedTopicId: string | null;
  onNavigate: (screen: ScreenType) => void;
  onSelectTopic: (topicId: string) => void;
}

export const WrittenRoomScreen: React.FC<WrittenRoomScreenProps> = ({
  selectedTopicId,
  onNavigate,
  onSelectTopic,
}) => {
  const [topics, setTopics] = useState<DbTopic[]>([]);
  const [activeTopicId, setActiveTopicId] = useState<string>('all');
  const [questions, setQuestions] = useState<DbQuestion[]>([]);
  const [currentIndex, setCurrentIndex] = useState<number>(0);

  // Single Core Toggle State: Show Answer / Hide Answer
  const [showAnswer, setShowAnswer] = useState<boolean>(false);
  const [selfMarked, setSelfMarked] = useState<'correct' | 'needs_revision' | null>(null);

  // Load Topics
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

  // Fetch Written Questions
  useEffect(() => {
    async function fetchQuestions() {
      let qList: DbQuestion[] = [];
      if (activeTopicId === 'all') {
        qList = await db.questions.where('type').equals('written').toArray();
        if (qList.length === 0) {
          qList = await db.questions.limit(60).toArray();
        }
      } else {
        qList = await db.questions
          .where('topic_id')
          .equals(activeTopicId)
          .and((q) => q.type === 'written')
          .toArray();

        if (qList.length === 0) {
          qList = await db.questions.where('topic_id').equals(activeTopicId).toArray();
        }
      }

      setQuestions(qList);
      setCurrentIndex(0);
      setShowAnswer(false);
      setSelfMarked(null);
    }
    fetchQuestions();
  }, [activeTopicId]);

  const currentQ = questions[currentIndex];

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex((prev) => prev + 1);
      setShowAnswer(false);
      setSelfMarked(null);
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1);
      setShowAnswer(false);
      setSelfMarked(null);
    }
  };

  // Self Evaluation Actions
  const handleMarkSuccess = async () => {
    if (!currentQ) return;
    setSelfMarked('correct');
    await recordAttempt({
      questionId: currentQ.id,
      topicId: currentQ.topic_id,
      topicName: currentQ.topic_name,
      type: 'written',
      questionStem: currentQ.stem,
      isCorrect: true,
      scoreObtained: 5,
      maxScore: 5,
      timeSpentSeconds: 60,
    });
  };

  const handleMarkRevision = async () => {
    if (!currentQ) return;
    setSelfMarked('needs_revision');
    await recordAttempt({
      questionId: currentQ.id,
      topicId: currentQ.topic_id,
      topicName: currentQ.topic_name,
      type: 'written',
      questionStem: currentQ.stem,
      isCorrect: false,
      scoreObtained: 2,
      maxScore: 5,
      timeSpentSeconds: 60,
      mistakeCategory: 'calculation',
      diagnosisText: 'লিখিত গণিত অনুশীলনে পুনরায় রিভিশন প্রয়োজন হিসেবে চিহ্নিত।',
    });
  };

  return (
    <div className="space-y-6 pb-12 max-w-4xl mx-auto">
      {/* Header Bar */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl p-5 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-xs text-emerald-600 dark:text-emerald-400 font-semibold mb-1">
            <PenTool className="w-4 h-4" />
            <span>খাতা-কলমে লিখিত গণিত সমাধান</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white">
            লিখিত গণিত অনুশীলন রুম
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            খাতায় কলম দিয়ে নিজে সমাধান করুন। এরপর নিচে উত্তর ও বিস্তারিত লিখিত সমাধান মিলিয়ে নিন।
          </p>
        </div>

        {/* Topic Selector */}
        <div className="flex items-center space-x-2">
          <select
            value={activeTopicId}
            onChange={(e) => setActiveTopicId(e.target.value)}
            className="text-xs font-semibold px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
          >
            <option value="all">
              সকল অধ্যায় (মোট {questions.length}টি লিখিত প্রশ্ন)
            </option>
            {topics.map((t) => (
              <option key={t.id} value={t.id}>
                {t.title_bn}
              </option>
            ))}
          </select>
        </div>
      </div>

      {questions.length === 0 ? (
        <div className="bg-white dark:bg-slate-900 p-12 rounded-2xl border border-slate-200 dark:border-slate-800 text-center text-slate-500">
          <BookOpen className="w-10 h-10 text-slate-400 mx-auto mb-2 opacity-80" />
          <p className="text-sm font-semibold">
            নির্বাচিত অধ্যায়ে কোনো লিখিত প্রশ্ন পাওয়া যায়নি।
          </p>
        </div>
      ) : (
        <div className="space-y-5">
          {/* Main Question Card */}
          <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 sm:p-8 border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
            {/* Meta tags and counter */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="text-[11px] font-bold px-2.5 py-1 rounded-md bg-emerald-50 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                  {currentQ.citation || 'প্রতিযোগিতামূলক লিখিত পরীক্ষা'}
                </span>
                <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">
                  {currentQ.topic_name}
                </span>
              </div>

              <span className="text-xs font-extrabold text-slate-700 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 px-3 py-1 rounded-full">
                প্রশ্ন {currentIndex + 1} / {questions.length}
              </span>
            </div>

            {/* Question Stem */}
            <div className="text-base sm:text-xl font-bold text-slate-900 dark:text-white leading-relaxed border-l-4 border-emerald-500 pl-4 py-1">
              <MathView content={currentQ.stem} />
            </div>

            {/* Bangladeshi Student Khata Reminder */}
            <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/60 text-xs text-slate-600 dark:text-slate-300 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <PenTool className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
                <span>আপনার খাতায় অংকটি সম্পন্ন হলে নিচের বাটনে ক্লিক করে সমাধান মেলান।</span>
              </div>
            </div>

            {/* SINGLE CORE BUTTON: SHOW ANSWER / HIDE ANSWER */}
            <div className="pt-2">
              <button
                onClick={() => setShowAnswer(!showAnswer)}
                className={`w-full py-3.5 px-6 rounded-xl font-bold text-sm shadow-sm transition flex items-center justify-center space-x-2 ${
                  showAnswer
                    ? 'bg-slate-800 hover:bg-slate-700 text-white dark:bg-slate-700 dark:hover:bg-slate-600'
                    : 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-emerald-600/20 shadow-md'
                }`}
              >
                {showAnswer ? (
                  <>
                    <EyeOff className="w-5 h-5" />
                    <span>সমাধান লুকান</span>
                  </>
                ) : (
                  <>
                    <Eye className="w-5 h-5" />
                    <span>উত্তর ও সমাধান দেখুন</span>
                  </>
                )}
              </button>
            </div>

            {/* REVEALED STEP-BY-STEP SOLUTION CONTAINER */}
            {showAnswer && (
              <div className="space-y-4 pt-4 border-t border-slate-200 dark:border-slate-800 animate-fadeIn">
                {/* Official Solution Box */}
                <div className="p-5 sm:p-6 rounded-2xl bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-800/60 space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-emerald-900 dark:text-emerald-300 uppercase tracking-wider flex items-center space-x-1.5">
                      <Sparkles className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                      <span>বিস্তারিত লিখিত সমাধান (মডেল সলিউশন)</span>
                    </span>

                    {currentQ.answer_raw && (
                      <span className="text-xs font-bold px-3 py-1 rounded-full bg-emerald-600 text-white">
                        উত্তর: {currentQ.answer_raw}
                      </span>
                    )}
                  </div>

                  <div className="text-sm text-slate-800 dark:text-slate-200 leading-relaxed font-normal bg-white dark:bg-slate-900/90 p-5 rounded-xl border border-emerald-100 dark:border-emerald-900/50">
                    <MathView content={currentQ.solution} />
                  </div>
                </div>

                {/* Optional Self-Assessment Check */}
                <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                  <span className="text-slate-600 dark:text-slate-300 font-semibold">
                    খাতায় আপনার সমাধান কি সঠিক হয়েছে?
                  </span>

                  <div className="flex items-center space-x-2">
                    <button
                      onClick={handleMarkSuccess}
                      className={`px-3.5 py-1.5 rounded-lg font-bold transition flex items-center space-x-1.5 ${
                        selfMarked === 'correct'
                          ? 'bg-emerald-600 text-white'
                          : 'bg-white dark:bg-slate-800 text-emerald-700 dark:text-emerald-400 border border-emerald-300 dark:border-emerald-800 hover:bg-emerald-50'
                      }`}
                    >
                      <Check className="w-3.5 h-3.5" />
                      <span>সঠিক হয়েছে</span>
                    </button>

                    <button
                      onClick={handleMarkRevision}
                      className={`px-3.5 py-1.5 rounded-lg font-bold transition flex items-center space-x-1.5 ${
                        selfMarked === 'needs_revision'
                          ? 'bg-amber-600 text-white'
                          : 'bg-white dark:bg-slate-800 text-amber-700 dark:text-amber-400 border border-amber-300 dark:border-amber-800 hover:bg-amber-50'
                      }`}
                    >
                      <RotateCcw className="w-3.5 h-3.5" />
                      <span>আবার রিভিশন দিন</span>
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Navigation Controls: Previous / Next */}
            <div className="flex items-center justify-between pt-4 border-t border-slate-100 dark:border-slate-800">
              <button
                disabled={currentIndex === 0}
                onClick={handlePrev}
                className="flex items-center space-x-1.5 px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-xs font-bold disabled:opacity-40 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
              >
                <ChevronLeft className="w-4 h-4" />
                <span>পূর্ববর্তী প্রশ্ন</span>
              </button>

              <button
                disabled={currentIndex === questions.length - 1}
                onClick={handleNext}
                className="flex items-center space-x-1.5 px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold disabled:opacity-40 shadow-sm transition"
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
