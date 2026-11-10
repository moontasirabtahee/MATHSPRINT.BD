import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  TrendingUp,
  Target,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Award,
  Zap,
} from 'lucide-react';
import { db, type DbTopic, type DbUserAttempt, type DbMistake } from '../lib/db';
import { type ScreenType } from '../components/Navbar';

interface AnalyticsScreenProps {
  onNavigate: (screen: ScreenType) => void;
}

export const AnalyticsScreen: React.FC<AnalyticsScreenProps> = ({
  onNavigate,
}) => {
  const [topics, setTopics] = useState<DbTopic[]>([]);
  const [attempts, setAttempts] = useState<DbUserAttempt[]>([]);
  const [mistakes, setMistakes] = useState<DbMistake[]>([]);

  useEffect(() => {
    async function loadAnalytics() {
      const allT = await db.topics.toArray();
      const allA = await db.attempts.toArray();
      const allM = await db.mistakes.toArray();
      setTopics(allT);
      setAttempts(allA);
      setMistakes(allM);
    }
    loadAnalytics();
  }, []);

  // Aggregations
  const totalAttempts = attempts.length;
  const correctAttempts = attempts.filter((a) => a.is_correct).length;
  const overallAccuracy = totalAttempts > 0 ? Math.round((correctAttempts / totalAttempts) * 100) : 0;

  const totalTimeSpentSeconds = attempts.reduce((acc, a) => acc + (a.time_spent_seconds || 0), 0);
  const avgTimePerQuestion =
    totalAttempts > 0 ? Math.round(totalTimeSpentSeconds / totalAttempts) : 0;

  const writtenAttempts = attempts.filter((a) => a.type === 'written');
  const writtenEarned = writtenAttempts.reduce((acc, a) => acc + (a.score_obtained || 0), 0);
  const writtenMax = writtenAttempts.reduce((acc, a) => acc + (a.max_score || 0), 0);
  const writtenAvgPercent = writtenMax > 0 ? Math.round((writtenEarned / writtenMax) * 100) : 0;

  // Category performance
  const categoryStats: Record<string, { total: number; correct: number }> = {};
  for (const a of attempts) {
    const t = topics.find((top) => top.id === a.topic_id);
    const cat = t ? t.category : 'সাধারণ';
    if (!categoryStats[cat]) {
      categoryStats[cat] = { total: 0, correct: 0 };
    }
    categoryStats[cat].total++;
    if (a.is_correct) categoryStats[cat].correct++;
  }

  // Error breakdown
  const errorTypeCounts: Record<string, number> = {};
  for (const m of mistakes) {
    const k = m.mistake_category;
    errorTypeCounts[k] = (errorTypeCounts[k] || 0) + 1;
  }

  return (
    <div className="space-y-6 pb-12 max-w-5xl mx-auto">
      {/* Header */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-xs text-emerald-600 dark:text-emerald-400 font-semibold mb-1">
            <BarChart3 className="w-4 h-4" />
            <span>লাইভ লার্নিং মেট্রিক্স</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white">
            দক্ষতা ও নির্ভুলতা বিশ্লেষণ
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            আপনার গণিত সমাধানের গতি, নির্ভুলতা এবং পুনরাবৃত্তিমূলক দুর্বলতা ট্র্যাক করুন।
          </p>
        </div>
      </div>

      {/* Top 4 Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-500">
              সামগ্রিক সঠিকতা
            </span>
            <Target className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-2xl font-black text-slate-900 dark:text-white">
            {overallAccuracy}%
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            {correctAttempts} / {totalAttempts} টি সঠিক
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-500">
              গড় গতিবেগ
            </span>
            <Clock className="w-4 h-4 text-sky-500" />
          </div>
          <div className="text-2xl font-black text-slate-900 dark:text-white">
            {avgTimePerQuestion}s
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            প্রতি প্রশ্নে সময়
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-500">
              লিখিত পরীক্ষার স্কোর
            </span>
            <Award className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-2xl font-black text-slate-900 dark:text-white">
            {writtenAvgPercent}%
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            {writtenAttempts.length} টি লিখিত অনুশীলন
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-500">
              রেকর্ডকৃত ভুল
            </span>
            <AlertTriangle className="w-4 h-4 text-rose-500" />
          </div>
          <div className="text-2xl font-black text-slate-900 dark:text-white">
            {mistakes.length}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            ভুল খাতা পর্যালোচনায় রয়েছে
          </div>
        </div>
      </div>

      {/* Grid: Category Breakdown + Mistake Taxonomy */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Category Accuracy */}
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center space-x-2">
            <TrendingUp className="w-4 h-4 text-emerald-500" />
            <span>শাখাভিত্তিক নির্ভুলতা</span>
          </h2>

          <div className="space-y-3">
            {Object.keys(categoryStats).length === 0 ? (
              <div className="text-xs text-slate-400 py-4 text-center">
                কোনো অনুশীলনের ডাটা এখনো সংরক্ষিত হয়নি
              </div>
            ) : (
              Object.entries(categoryStats).map(([cat, st]) => {
                const pct = st.total > 0 ? Math.round((st.correct / st.total) * 100) : 0;
                return (
                  <div key={cat} className="space-y-1">
                    <div className="flex justify-between text-xs font-semibold">
                      <span className="text-slate-700 dark:text-slate-300">{cat}</span>
                      <span className="text-slate-500">{pct}% ({st.correct}/{st.total})</span>
                    </div>
                    <div className="w-full h-2 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                      <div
                        className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Error Breakdown */}
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-rose-500" />
            <span>ভুলের ধরন ও পুনরাবৃত্তি</span>
          </h2>

          <div className="space-y-2.5">
            {Object.keys(errorTypeCounts).length === 0 ? (
              <div className="text-xs text-slate-400 py-4 text-center">
                এখনো কোনো ভুল রেকর্ড হয়নি। দুর্দান্ত পারফরম্যান্স!
              </div>
            ) : (
              Object.entries(errorTypeCounts).map(([catKey, cnt]) => {
                const labels: Record<string, string> = {
                  calculation: 'হিসাব বা ক্যালকুলেশনে অসতর্কতা',
                  formula_error: 'ভুল সূত্র প্রয়োগ বা ভুলে যাওয়া',
                  sign_error: 'চিহ্ন পরিবর্তন ও ব্র্যাকেট বিভ্রান্তি (+/-)',
                  algebraic_simplification: 'বীজগণিতীয় সরলীকরণ ও পক্ষান্তর ভুল',
                  substitution: 'মান বসানো বা এককে অসামঞ্জস্য',
                  missing_condition: 'প্রশ্নের গোপন শর্ত না খেয়াল করা',
                };
                const label = labels[catKey] || catKey;
                return (
                  <div
                    key={catKey}
                    className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/60 flex items-center justify-between text-xs"
                  >
                    <span className="font-semibold text-slate-700 dark:text-slate-200">{label}</span>
                    <span className="font-bold text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/60 px-2.5 py-0.5 rounded-full">
                      {cnt} বার
                    </span>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
