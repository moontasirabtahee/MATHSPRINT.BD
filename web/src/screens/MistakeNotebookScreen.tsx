import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  RotateCcw,
} from 'lucide-react';
import { db, type DbMistake, type DbQuestion } from '../lib/db';
import { MathView } from '../components/MathView';
import { type ScreenType } from '../components/Navbar';

interface MistakeNotebookScreenProps {
  onNavigate: (screen: ScreenType) => void;
  onSelectTopic: (topicId: string) => void;
}

export const MistakeNotebookScreen: React.FC<MistakeNotebookScreenProps> = ({
  onNavigate,
  onSelectTopic,
}) => {
  const [mistakes, setMistakes] = useState<DbMistake[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  useEffect(() => {
    async function loadMistakes() {
      const allM = await db.mistakes.toArray();
      setMistakes(allM);
    }
    loadMistakes();
  }, []);

  const categories = [
    { id: 'all', label: 'সকল ভুল' },
    { id: 'sign_error', label: 'চিহ্নের ভুল (±)' },
    { id: 'formula_error', label: 'ভুল সূত্র নির্বাচন' },
    { id: 'substitution', label: 'ভুল মান প্রতিস্থাপন' },
    { id: 'algebraic_simplification', label: 'সরলীকরণ ত্রুটি' },
    { id: 'calculation', label: 'হিসাবের অসতর্কতা' },
    { id: 'missing_condition', label: 'শর্ত উপেক্ষা' },
  ];

  const filteredMistakes = mistakes.filter((m) => {
    return selectedCategory === 'all' || m.mistake_category === selectedCategory;
  });

  const handleResolveMistake = async (id: number) => {
    await db.mistakes.update(id, {
      is_resolved: true,
      resolved_at: new Date().toISOString(),
    });
    setMistakes((prev) =>
      prev.map((m) => (m.id === id ? { ...m, is_resolved: true } : m))
    );
  };

  const handleRetryQuestion = async (m: DbMistake) => {
    const q = await db.questions.get(m.question_id);
    if (q) {
      onSelectTopic(m.topic_id);
      onNavigate(q.type === 'written' ? 'written' : 'mcq');
    }
  };

  const unresolvedCount = mistakes.filter((m) => !m.is_resolved).length;

  return (
    <div className="space-y-6 pb-12 max-w-5xl mx-auto">
      {/* Header */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl p-5 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-xs text-rose-600 dark:text-rose-400 font-semibold mb-1">
            <AlertTriangle className="w-4 h-4" />
            <span>মেটাকগনিটিভ ত্রুটি খাতা</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white">
            গাণিতিক ভুল বিশ্লেষণ ও সংশোধন খাতা
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            মোট নথিবদ্ধ ভুল: {mistakes.length}টি · সংশোধন বাকি: {unresolvedCount}টি
          </p>
        </div>

        {/* Category Filter */}
        <div className="flex items-center space-x-2">
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="text-xs font-semibold px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white"
          >
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {mistakes.length === 0 ? (
        <div className="bg-white dark:bg-slate-900 p-12 rounded-2xl border border-slate-200 dark:border-slate-800 text-center text-slate-500">
          <CheckCircle2 className="w-10 h-10 text-emerald-500 mx-auto mb-2 opacity-80" />
          <h3 className="text-sm font-bold text-slate-900 dark:text-white">
            ভুল খাতা একদম পরিষ্কার!
          </h3>
          <p className="text-xs text-slate-500 mt-1">
            অনুশীলন রুমে ভুল করলে এখানে স্বয়ংক্রিয়ভাবে গাণিতিক ফাঁদ নথিভুক্ত হবে।
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredMistakes.map((m) => (
            <div
              key={m.id}
              className={`bg-white dark:bg-slate-900 rounded-2xl p-5 border transition shadow-sm ${
                m.is_resolved
                  ? 'border-slate-200 dark:border-slate-800 opacity-70'
                  : 'border-rose-300 dark:border-rose-900/80 bg-rose-50/20 dark:bg-rose-950/10'
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
                <div className="flex items-center space-x-2">
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                    {m.topic_name}
                  </span>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-100 dark:bg-rose-950 text-rose-800 dark:text-rose-300 uppercase">
                    {m.mistake_category.replace('_', ' ')}
                  </span>
                </div>

                <span className="text-[11px] text-slate-400">
                  ব্যর্থ চেষ্টা: {m.incorrect_attempts} বার
                </span>
              </div>

              {/* Question Stem */}
              <div className="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white mb-3">
                <MathView content={m.question_stem} />
              </div>

              {/* Diagnosis & Remedy Box */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs mb-4">
                <div className="bg-rose-50/60 dark:bg-rose-950/30 p-3 rounded-xl border border-rose-200/80 dark:border-rose-900/60">
                  <span className="font-bold text-rose-900 dark:text-rose-300 block mb-1">
                    ভুলের ধরন ও ফাঁদ:
                  </span>
                  <p className="text-slate-700 dark:text-slate-300">{m.diagnosis_text}</p>
                </div>

                <div className="bg-emerald-50/60 dark:bg-emerald-950/30 p-3 rounded-xl border border-emerald-200/80 dark:border-emerald-900/60">
                  <span className="font-bold text-emerald-900 dark:text-emerald-300 block mb-1">
                    সংশোধনের পথ:
                  </span>
                  <p className="text-slate-700 dark:text-slate-300">{m.remedy_text}</p>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-between pt-3 border-t border-slate-100 dark:border-slate-800 text-xs">
                <button
                  onClick={() => handleRetryQuestion(m)}
                  className="px-3.5 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 dark:bg-rose-600 dark:hover:bg-rose-700 text-white font-bold transition flex items-center space-x-1.5 shadow-sm"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>এখনই পুনরায় সমাধান করুন</span>
                </button>

                {!m.is_resolved ? (
                  <button
                    onClick={() => handleResolveMistake(m.id!)}
                    className="px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-emerald-50 hover:text-emerald-700 transition"
                  >
                    সংশোধিত হিসেবে চিহ্নিত করুন
                  </button>
                ) : (
                  <span className="text-emerald-600 dark:text-emerald-400 font-semibold flex items-center space-x-1">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>সংশোধন সম্পন্ন</span>
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
