import React, { useState, useEffect } from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  BookOpen,
  ArrowRight,
  TrendingUp,
  BrainCircuit,
  Target,
  Sparkles,
  Zap,
  Bookmark,
} from 'lucide-react';
import { db, type DbTopic, type DbQuestion } from '../lib/db';
import { MathView } from '../components/MathView';
import { type ScreenType } from '../components/Navbar';

interface DashboardScreenProps {
  onNavigate: (screen: ScreenType) => void;
  onSelectTopic: (topicId: string) => void;
}

export const DashboardScreen: React.FC<DashboardScreenProps> = ({
  onNavigate,
  onSelectTopic,
}) => {
  const [topics, setTopics] = useState<DbTopic[]>([]);
  const [stats, setStats] = useState({
    totalTopics: 36,
    masteredTopics: 0,
    inProgressTopics: 0,
    totalQuestions: 3820,
    attemptedCount: 0,
    correctCount: 0,
    accuracy: 0,
    writtenMarksEarned: 0,
    writtenMarksTotal: 0,
    mistakesCount: 0,
    pendingRevisionsCount: 0,
    formulasMemorized: 0,
    readinessScore: 0,
  });
  const [recommendedTopic, setRecommendedTopic] = useState<DbTopic | null>(null);
  const [recentMistakeQ, setRecentMistakeQ] = useState<DbQuestion | null>(null);

  useEffect(() => {
    async function loadDashboardData() {
      const allTopics = await db.topics.toArray();
      setTopics(allTopics);

      const allAttempts = await db.attempts.toArray();
      const allMistakes = await db.mistakes.where('is_resolved').equals(0 as any).toArray();
      const allRevisions = await db.revisionQueue.where('status').equals('pending').toArray();
      const memorizedFormulas = await db.formulas.where('is_memorized').equals(1 as any).count();

      const mastered = allTopics.filter((t) => t.status === 'mastered').length;
      const inProgress = allTopics.filter((t) => t.status === 'in_progress').length;

      const attempted = allAttempts.length;
      const correct = allAttempts.filter((a) => a.is_correct).length;
      const acc = attempted > 0 ? Math.round((correct / attempted) * 100) : 0;

      const writtenAttempts = allAttempts.filter((a) => a.type === 'written');
      const wEarned = writtenAttempts.reduce((sum, a) => sum + (a.score_obtained || 0), 0);
      const wTotal = writtenAttempts.reduce((sum, a) => sum + (a.max_score || 0), 0);

      const topicCoverage = allTopics.length > 0 ? ((mastered + inProgress * 0.4) / allTopics.length) * 100 : 0;
      const formulaRetention = Math.min(100, (memorizedFormulas / 100) * 100);
      const readiness = Math.round(topicCoverage * 0.4 + acc * 0.4 + formulaRetention * 0.2);

      setStats({
        totalTopics: allTopics.length || 36,
        masteredTopics: mastered,
        inProgressTopics: inProgress,
        totalQuestions: 3820,
        attemptedCount: attempted,
        correctCount: correct,
        accuracy: acc,
        writtenMarksEarned: wEarned,
        writtenMarksTotal: wTotal,
        mistakesCount: allMistakes.length,
        pendingRevisionsCount: allRevisions.length,
        formulasMemorized: memorizedFormulas,
        readinessScore: readiness,
      });

      const weakTopic = allTopics
        .filter((t) => t.status === 'in_progress')
        .sort((a, b) => (a.masteryScore || 0) - (b.masteryScore || 0))[0];

      if (weakTopic) {
        setRecommendedTopic(weakTopic);
      } else {
        const nextUnstarted = allTopics.find((t) => t.status === 'unstarted');
        setRecommendedTopic(nextUnstarted || allTopics[0] || null);
      }

      if (allMistakes.length > 0) {
        const lastM = allMistakes[allMistakes.length - 1];
        const q = await db.questions.get(lastM.question_id);
        if (q) setRecentMistakeQ(q);
      }
    }

    loadDashboardData();
  }, []);

  const handleStartTopic = (topicId: string) => {
    onSelectTopic(topicId);
    onNavigate('learning');
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Hero: 48-Hour Sprint Banner */}
      <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-emerald-950 rounded-2xl p-6 sm:p-8 text-white shadow-xl relative overflow-hidden border border-slate-700/60">
        <div className="absolute right-0 top-0 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-semibold mb-3 border border-emerald-500/30">
            <Zap className="w-3.5 h-3.5" />
            <span>৪৮ ঘণ্টার নিবিড় গণিত রিভিশন স্প্রিন্ট</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight mb-2 text-white">
            সম্পূর্ণ গাণিতিক সিলেবাস রিভিশন ও প্র্যাকটিস ইঞ্জিন
          </h1>
          <p className="text-slate-300 text-sm leading-relaxed mb-6">
            কোনো অপ্রয়োজনীয় আলোচনা বা বিভ্রান্তি ছাড়া সরাসরি প্রশ্ন সমাধান, ভুল বিশ্লেষণ, রিটেন রুব্রিক এবং সূত্র আত্মস্থ করার সমন্বিত পরিবেশ।
          </p>

          <div className="flex flex-wrap items-center gap-3">
            {recommendedTopic && (
              <button
                onClick={() => handleStartTopic(recommendedTopic.id)}
                className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold text-sm shadow-lg shadow-emerald-500/25 transition-all transform hover:-translate-y-0.5"
              >
                <span>চালিয়ে যান: {recommendedTopic.title_bn}</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            )}

            <button
              onClick={() => onNavigate('mcq')}
              className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-white font-medium text-sm border border-slate-600 transition"
            >
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>এমসিকিউ স্প্রিন্ট শুরু</span>
            </button>

            <button
              onClick={() => onNavigate('written')}
              className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-white font-medium text-sm border border-slate-600 transition"
            >
              <BrainCircuit className="w-4 h-4 text-teal-400" />
              <span>লিখিত গণিত রুম</span>
            </button>
          </div>
        </div>
      </div>

      {/* Core Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
        {/* Readiness Index */}
        <div className="bg-white dark:bg-slate-900 rounded-xl p-4 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">
              প্রস্তুতি সূচক
            </span>
            <Target className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
          </div>
          <div className="mt-3">
            <div className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">
              {stats.readinessScore}%
            </div>
            <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-1.5 mt-2 overflow-hidden">
              <div
                className="bg-emerald-500 h-full rounded-full transition-all duration-500"
                style={{ width: `${stats.readinessScore}%` }}
              />
            </div>
          </div>
        </div>

        {/* Mastered Topics */}
        <div className="bg-white dark:bg-slate-900 rounded-xl p-4 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">
              মাস্টার করা টপিক
            </span>
            <BookOpen className="w-4 h-4 text-teal-600 dark:text-teal-400" />
          </div>
          <div className="mt-3">
            <div className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">
              {stats.masteredTopics} <span className="text-xs text-slate-400 font-normal">/ {stats.totalTopics}</span>
            </div>
            <p className="text-[11px] text-slate-500 mt-1">
              {stats.inProgressTopics} চলতি অনুশীলন
            </p>
          </div>
        </div>

        {/* Questions Solved */}
        <div className="bg-white dark:bg-slate-900 rounded-xl p-4 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">
              সমাধানকৃত প্রশ্ন
            </span>
            <TrendingUp className="w-4 h-4 text-blue-600 dark:text-blue-400" />
          </div>
          <div className="mt-3">
            <div className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">
              {stats.attemptedCount}
            </div>
            <p className="text-[11px] text-emerald-600 dark:text-emerald-400 font-medium mt-1">
              {stats.accuracy}% সঠিকতার হার
            </p>
          </div>
        </div>

        {/* Written Marks */}
        <div className="bg-white dark:bg-slate-900 rounded-xl p-4 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">
              লিখিত নম্বর
            </span>
            <BrainCircuit className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
          </div>
          <div className="mt-3">
            <div className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">
              {stats.writtenMarksEarned}
              <span className="text-xs text-slate-400 font-normal">
                {stats.writtenMarksTotal > 0 ? ` / ${stats.writtenMarksTotal}` : ''}
              </span>
            </div>
            <p className="text-[11px] text-slate-500 mt-1">
              রুব্রিক অনুযায়ী মূল্যায়িত
            </p>
          </div>
        </div>

        {/* Mistakes to Resolve */}
        <div
          onClick={() => onNavigate('mistakes')}
          className="bg-white dark:bg-slate-900 rounded-xl p-4 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between cursor-pointer hover:border-rose-400 transition"
        >
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">
              অমীমাংসিত ভুল
            </span>
            <AlertTriangle className="w-4 h-4 text-rose-500" />
          </div>
          <div className="mt-3">
            <div className="text-2xl sm:text-3xl font-extrabold text-rose-600 dark:text-rose-400">
              {stats.mistakesCount}
            </div>
            <p className="text-[11px] text-rose-500 mt-1 font-medium">
              পুনরায় চেষ্টা করুন →
            </p>
          </div>
        </div>

        {/* Formula and Theory Vault Quick Access */}
        <div
          onClick={() => onNavigate('vault')}
          className="bg-white dark:bg-slate-900 rounded-xl p-4 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between cursor-pointer hover:border-emerald-500 transition"
        >
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">
              থিওরি ও সূত্র
            </span>
            <Bookmark className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="mt-3">
            <div className="text-2xl sm:text-3xl font-extrabold text-emerald-600 dark:text-emerald-400">
              ৩৬টি অধ্যায়
            </div>
            <p className="text-[11px] text-emerald-600 dark:text-emerald-400 mt-1 font-medium">
              সূত্র ও শর্টকাট দেখুন →
            </p>
          </div>
        </div>
      </div>

      {/* Two Column Section: Priority Next Action + Active Error Recovery */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Next Topic Focus (2 Cols) */}
        <div className="lg:col-span-2 bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-emerald-600" />
              <h2 className="text-base font-bold text-slate-900 dark:text-white">
                পরবর্তী প্রস্তাবিত রিভিশন টপিক
              </h2>
            </div>
            <button
              onClick={() => onNavigate('curriculum')}
              className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 hover:underline"
            >
              সকল টপিক দেখুন →
            </button>
          </div>

          {recommendedTopic ? (
            <div className="bg-slate-50 dark:bg-slate-800/60 rounded-xl p-5 border border-slate-200/80 dark:border-slate-700/60">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-xs font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
                      {recommendedTopic.category}
                    </span>
                    <span className="text-xs text-slate-500">
                      {recommendedTopic.total_questions} টি প্রশ্ন সংগৃহীত
                    </span>
                  </div>
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white">
                    {recommendedTopic.title_bn}
                  </h3>
                  <div className="text-xs text-slate-600 dark:text-slate-300 mt-1 line-clamp-2">
                    <MathView content={recommendedTopic.concept_summary.core_idea} inline />
                  </div>
                </div>

                <div className="flex items-center space-x-2 shrink-0">
                  <button
                    onClick={() => handleStartTopic(recommendedTopic.id)}
                    className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs shadow-sm transition"
                  >
                    লার্নিং রুমে যান
                  </button>
                </div>
              </div>

              {/* Common Trap Warning */}
              <div className="mt-4 pt-3 border-t border-slate-200 dark:border-slate-700 flex items-start space-x-2 text-xs text-amber-800 dark:text-amber-300 bg-amber-50/60 dark:bg-amber-950/20 p-2.5 rounded-lg">
                <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                <span className="leading-relaxed">
                  <strong className="mr-1">সতর্কতা ও ফাঁদ:</strong>
                  <MathView content={recommendedTopic.concept_summary.common_traps} inline />
                </span>
              </div>
            </div>
          ) : (
            <p className="text-sm text-slate-500">
              কোনো টপিক নির্বাচন করা হয়নি।
            </p>
          )}

          {/* Quick Curriculum Sprints */}
          <div className="mt-5">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-3">
              দ্রুত অনুশীলন ক্যাটাগরি
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
              {[
                { name: 'পাটিগণিত (ঐকিক, অনুপাত, ল.সা.গু)', cat: 'Arithmetic', count: 12 },
                { name: 'বাণিজ্যিক গণিত (শতকরা, লাভ-ক্ষতি, সুদ)', cat: 'Commercial Math', count: 6 },
                { name: 'বীজগণিত (মান নির্ণয়, ধারা, সূচক)', cat: 'Algebra', count: 7 },
                { name: 'উচ্চতর গণিত (বিন্যাস, সমাবেশ, সেট)', cat: 'Higher Math', count: 4 },
                { name: 'জ্যামিতি ও পরিমিতি', cat: 'Geometry', count: 6 },
                { name: 'বিসিএস ও ব্যাংক মডেল টেস্ট', cat: 'Exam Revision', count: 1 },
              ].map((c) => (
                <div
                  key={c.cat}
                  onClick={() => onNavigate('curriculum')}
                  className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-200/80 dark:border-slate-800 hover:border-emerald-500 cursor-pointer transition text-left"
                >
                  <p className="text-xs font-bold text-slate-900 dark:text-white line-clamp-1">{c.name}</p>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                    {c.count} টি অধ্যায়
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Mistake Alert & Vault Quick Recall */}
        <div className="space-y-4">
          {/* Mistake Alert Card */}
          <div className="bg-white dark:bg-slate-900 rounded-2xl p-5 border border-slate-200 dark:border-slate-800 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2 text-rose-600 dark:text-rose-400">
                <AlertTriangle className="w-4 h-4" />
                <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                  ভুল সংশোধন অগ্রাধিকার
                </h3>
              </div>
              <button
                onClick={() => onNavigate('mistakes')}
                className="text-xs font-semibold text-rose-600 dark:text-rose-400 hover:underline"
              >
                সব দেখুন
              </button>
            </div>

            {recentMistakeQ ? (
              <div className="bg-rose-50/70 dark:bg-rose-950/20 p-3.5 rounded-xl border border-rose-200/60 dark:border-rose-900/40">
                <span className="text-[10px] font-bold uppercase tracking-wider text-rose-700 dark:text-rose-400">
                  {recentMistakeQ.topic_name}
                </span>
                <div className="text-xs text-slate-800 dark:text-slate-200 font-medium line-clamp-2 mt-1">
                  <MathView content={recentMistakeQ.stem} inline />
                </div>
                <button
                  onClick={() => onNavigate('mistakes')}
                  className="mt-3 w-full py-1.5 rounded-lg bg-rose-600 hover:bg-rose-700 text-white font-semibold text-xs shadow-sm transition"
                >
                  এখনই পুনরায় সমাধান করুন
                </button>
              </div>
            ) : (
              <div className="text-center py-6 text-slate-400 text-xs">
                <CheckCircle2 className="w-8 h-8 mx-auto text-emerald-500 mb-2 opacity-80" />
                চমৎকার! কোনো অমীমাংসিত ভুল নেই।
              </div>
            )}
          </div>

          {/* Formula Quick Vault Card */}
          <div className="bg-white dark:bg-slate-900 rounded-2xl p-5 border border-slate-200 dark:border-slate-800 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2 text-emerald-600 dark:text-emerald-400">
                <BookOpen className="w-4 h-4" />
                <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                  সূত্র ভল্ট দ্রুত অনুশীলন
                </h3>
              </div>
              <button
                onClick={() => onNavigate('vault')}
                className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 hover:underline"
              >
                ভল্ট খুলুন
              </button>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-3">
              ৩৬টি অধ্যায়ের মূল গাণিতিক তত্ত্ব, প্রমাণ্য সূত্র ও শর্টকাট সংকলন।
            </p>
            <button
              onClick={() => onNavigate('vault')}
              className="w-full py-2 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 font-semibold text-xs transition"
            >
              ফ্ল্যাশকার্ডে সূত্র মুখস্থ করুন
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
