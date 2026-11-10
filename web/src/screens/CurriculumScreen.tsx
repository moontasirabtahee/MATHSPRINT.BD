import React, { useState, useEffect } from 'react';
import {
  Search,
  CheckCircle2,
  GitFork,
  BookOpen,
  GraduationCap,
  PenTool,
} from 'lucide-react';
import { db, type DbTopic } from '../lib/db';
import { type ScreenType } from '../components/Navbar';
import { MathView } from '../components/MathView';

interface CurriculumScreenProps {
  onNavigate: (screen: ScreenType) => void;
  onSelectTopic: (topicId: string) => void;
}

export const CurriculumScreen: React.FC<CurriculumScreenProps> = ({
  onNavigate,
  onSelectTopic,
}) => {
  const [topics, setTopics] = useState<DbTopic[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [showDependencyGraph, setShowDependencyGraph] = useState<boolean>(true);

  useEffect(() => {
    async function loadTopics() {
      const allTopics = await db.topics.toArray();
      setTopics(allTopics);
    }
    loadTopics();
  }, []);

  const categories = [
    { id: 'all', label: 'সকল অধ্যায় (৩৬)' },
    { id: 'Arithmetic', label: 'পাটিগণিত' },
    { id: 'Commercial Math', label: 'বাণিজ্যিক গণিত' },
    { id: 'Algebra', label: 'বীজগণিত' },
    { id: 'Higher Math', label: 'উচ্চতর গণিত ও সম্ভাবনা' },
    { id: 'Geometry', label: 'জ্যামিতি ও পরিমিতি' },
    { id: 'Exam Revision', label: 'বিসিএস ও ব্যাংক মডেল টেস্ট' },
  ];

  const filteredTopics = topics.filter((t) => {
    const matchesCategory = selectedCategory === 'all' || t.category === selectedCategory;
    const matchesSearch =
      t.title_bn.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.title_en.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.concept_summary.core_idea.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const getPrerequisiteNames = (prereqIds: string[]) => {
    return prereqIds
      .map((id) => {
        const found = topics.find((t) => t.id === id);
        return found ? found.title_bn : id;
      })
      .filter(Boolean);
  };

  const handleOpenLearning = (topicId: string) => {
    onSelectTopic(topicId);
    onNavigate('learning');
  };

  const handleOpenMCQ = (topicId: string) => {
    onSelectTopic(topicId);
    onNavigate('mcq');
  };

  const handleOpenWritten = (topicId: string) => {
    onSelectTopic(topicId);
    onNavigate('written');
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <div>
          <div className="flex items-center space-x-2 text-emerald-600 dark:text-emerald-400 mb-1">
            <GitFork className="w-5 h-5" />
            <span className="text-xs font-bold uppercase tracking-wider">
              নলেজ গ্রাফ ও সিলেবাস
            </span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            মডিউল বিন্যাস ও নির্ভরতা ম্যাপিং
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            কোনো অপ্রয়োজনীয় বইয়ের নাম বা পৃষ্ঠা নম্বর ছাড়াই সংগৃহীত বিশুদ্ধ গাণিতিক সিলেবাস।
          </p>
        </div>

        {/* Search */}
        <div className="relative w-full md:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="টপিক বা সূত্র খুঁজুন..."
            className="w-full pl-9 pr-4 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
        </div>
      </div>

      {/* Understand-Anything Concept Dependency Tree Card */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-teal-950 p-5 rounded-2xl text-white border border-slate-700 shadow-md">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <GitFork className="w-4 h-4 text-emerald-400" />
            <h3 className="text-sm font-bold tracking-tight">
              কনসেপ্ট নির্ভরতা পাথওয়ে (Knowledge Graph)
            </h3>
          </div>
          <button
            onClick={() => setShowDependencyGraph(!showDependencyGraph)}
            className="text-xs text-emerald-300 hover:underline"
          >
            {showDependencyGraph ? 'লুকান' : 'দেখান'}
          </button>
        </div>

        {showDependencyGraph && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs mt-3 pt-3 border-t border-slate-700/80">
            <div className="bg-slate-800/80 p-3 rounded-xl border border-slate-700">
              <span className="font-bold text-emerald-400 block mb-1">
                পাটিগণিত ভিত্তি পথ:
              </span>
              <p className="text-slate-300">
                সংখ্যা পদ্ধতি → ভগ্নাংশ → শতকরা → লাভ-ক্ষতি → সুদকষা → মিশ্রণ ও এলিগেশন
              </p>
            </div>
            <div className="bg-slate-800/80 p-3 rounded-xl border border-slate-700">
              <span className="font-bold text-teal-400 block mb-1">
                গতি ও ঐকিক ধারা:
              </span>
              <p className="text-slate-300">
                ঐকিক নিয়ম → ট্রেন ও গতিবেগ → আপেক্ষিক গতি → নৌকা ও স্রোত → কাজ ও চৌবাচ্চা
              </p>
            </div>
            <div className="bg-slate-800/80 p-3 rounded-xl border border-slate-700">
              <span className="font-bold text-amber-400 block mb-1">
                উচ্চতর ও বিন্যাস পথ:
              </span>
              <p className="text-slate-300">
                বীজগণিত সূত্র → সূচক → লগারিদম → ধারা → বিন্যাস → সমাবেশ → সম্ভাব্যতা
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Category Pills */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-1 scrollbar-none">
        {categories.map((c) => (
          <button
            key={c.id}
            onClick={() => setSelectedCategory(c.id)}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
              selectedCategory === c.id
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
            }`}
          >
            {c.label}
          </button>
        ))}
      </div>

      {/* Topic Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredTopics.map((topic) => {
          const prereqNames = getPrerequisiteNames(topic.prerequisites);
          const isMastered = topic.status === 'mastered';
          const isInProgress = topic.status === 'in_progress';

          return (
            <div
              key={topic.id}
              className={`bg-white dark:bg-slate-900 rounded-2xl p-5 border transition-all duration-200 flex flex-col justify-between shadow-sm hover:shadow-md ${
                isMastered
                  ? 'border-emerald-300 dark:border-emerald-800/80'
                  : isInProgress
                  ? 'border-amber-300 dark:border-amber-800/80'
                  : 'border-slate-200 dark:border-slate-800'
              }`}
            >
              <div>
                {/* Top Badge & Mastery */}
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                    {topic.category}
                  </span>

                  <div className="flex items-center space-x-1">
                    {isMastered ? (
                      <span className="inline-flex items-center space-x-1 text-[11px] font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-2 py-0.5 rounded-full">
                        <CheckCircle2 className="w-3 h-3" />
                        <span>{topic.masteryScore}%</span>
                      </span>
                    ) : isInProgress ? (
                      <span className="inline-flex items-center space-x-1 text-[11px] font-bold text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/60 px-2 py-0.5 rounded-full">
                        <span>{topic.masteryScore}%</span>
                      </span>
                    ) : (
                      <span className="text-[11px] text-slate-400">
                        শুরু হয়নি
                      </span>
                    )}
                  </div>
                </div>

                {/* Titles */}
                <h3 className="text-base font-bold text-slate-900 dark:text-white leading-snug">
                  {topic.title_bn}
                </h3>
                <p className="text-[11px] text-slate-400 dark:text-slate-500 mb-2">
                  {topic.title_en}
                </p>

                {/* Core Idea snippet */}
                <div className="text-xs text-slate-600 dark:text-slate-300 line-clamp-2 mb-3">
                  <MathView content={topic.concept_summary.core_idea} inline />
                </div>

                {/* Prerequisites If Any */}
                {prereqNames.length > 0 && (
                  <div className="mb-3 text-[11px] text-slate-500 dark:text-slate-400 flex items-center space-x-1.5 flex-wrap">
                    <span className="font-semibold text-slate-700 dark:text-slate-300">
                      পূর্বশর্ত:
                    </span>
                    {prereqNames.map((name, i) => (
                      <span
                        key={i}
                        className="bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 px-1.5 py-0.5 rounded text-[10px]"
                      >
                        {name}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Bottom Metrics & Actions */}
              <div className="pt-3 border-t border-slate-100 dark:border-slate-800 space-y-3">
                <div className="flex items-center justify-between text-[11px] text-slate-500">
                  <span className="flex items-center space-x-1">
                    <BookOpen className="w-3.5 h-3.5" />
                    <span>
                      {topic.total_questions} টি প্রশ্ন
                    </span>
                  </span>
                  <span>
                    {topic.mcq_count} MCQ · {topic.written_count} লিখিত
                  </span>
                </div>

                <div className="grid grid-cols-3 gap-1.5">
                  <button
                    onClick={() => handleOpenLearning(topic.id)}
                    className="flex items-center justify-center space-x-1 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs shadow-sm transition"
                    title="Interactive 6-Step Learning Room"
                  >
                    <GraduationCap className="w-3.5 h-3.5" />
                    <span>শিখুন</span>
                  </button>

                  <button
                    onClick={() => handleOpenMCQ(topic.id)}
                    className="flex items-center justify-center space-x-1 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 font-semibold text-xs transition"
                    title="MCQ Practice & Timed Exam"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                    <span>MCQ</span>
                  </button>

                  <button
                    onClick={() => handleOpenWritten(topic.id)}
                    className="flex items-center justify-center space-x-1 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 font-semibold text-xs transition"
                    title="Written Multi-step Math Workspace"
                  >
                    <PenTool className="w-3.5 h-3.5 text-teal-500" />
                    <span>লিখিত</span>
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
