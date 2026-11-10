import React, { useState, useEffect } from 'react';
import {
  Bookmark,
  Search,
  CheckCircle2,
  Copy,
  Check,
  Star,
  BookOpen,
  Sparkles,
  Eye,
  EyeOff,
  Zap,
  AlertTriangle,
  Lightbulb,
} from 'lucide-react';
import { db, type DbFormula } from '../lib/db';
import { MathView } from '../components/MathView';
import { type ScreenType } from '../components/Navbar';

interface FormulaVaultScreenProps {
  onNavigate: (screen: ScreenType) => void;
}

export const FormulaVaultScreen: React.FC<FormulaVaultScreenProps> = ({
  onNavigate,
}) => {
  const [formulas, setFormulas] = useState<DbFormula[]>([]);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedTopic, setSelectedTopic] = useState<string>('all');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [onlyBookmarked, setOnlyBookmarked] = useState<boolean>(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [flashcardMode, setFlashcardMode] = useState<boolean>(false);
  const [revealedIds, setRevealedIds] = useState<Record<string, boolean>>({});

  useEffect(() => {
    async function loadFormulas() {
      const allF = await db.formulas.toArray();
      setFormulas(allF);
    }
    loadFormulas();
  }, []);

  const topicsList = Array.from(new Set(formulas.map((f) => f.topic_name)));

  const filteredFormulas = formulas.filter((f) => {
    const matchesTopic = selectedTopic === 'all' || f.topic_name === selectedTopic;
    const matchesType = selectedType === 'all' || f.concept_type === selectedType;
    const matchesBookmark = !onlyBookmarked || f.is_bookmarked;
    const matchesSearch =
      f.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      f.formula.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (f.explanation && f.explanation.toLowerCase().includes(searchTerm.toLowerCase())) ||
      f.topic_name.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesTopic && matchesType && matchesBookmark && matchesSearch;
  });

  const toggleBookmark = async (id: string, currentStatus?: boolean) => {
    await db.formulas.update(id, { is_bookmarked: !currentStatus });
    setFormulas((prev) =>
      prev.map((f) => (f.id === id ? { ...f, is_bookmarked: !currentStatus } : f))
    );
  };

  const handleCopyFormula = (id: string, formulaText: string) => {
    navigator.clipboard.writeText(formulaText);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const toggleReveal = (id: string) => {
    setRevealedIds((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const conceptTypes = [
    { id: 'all', label: 'সকল আইটেম', icon: BookOpen },
    { id: 'formula', label: 'মূল সূত্র', icon: Sparkles },
    { id: 'shortcut', label: 'শর্টকাট টেকনিক', icon: Zap },
    { id: 'concept', label: 'মৌলিক তত্ত্ব', icon: Lightbulb },
    { id: 'trap', label: 'পরীক্ষার ফাঁদ', icon: AlertTriangle },
  ];

  const getTypeBadge = (type?: string) => {
    switch (type) {
      case 'formula':
        return (
          <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300 border border-blue-200 dark:border-blue-800">
            মূল সূত্র
          </span>
        );
      case 'shortcut':
        return (
          <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
            শর্টকাট হ্যাক
          </span>
        );
      case 'trap':
        return (
          <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300 border border-rose-200 dark:border-rose-800">
            পরীক্ষার ফাঁদ
          </span>
        );
      case 'concept':
      default:
        return (
          <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
            তাত্ত্বিক ভিত্তি
          </span>
        );
    }
  };

  return (
    <div className="space-y-6 pb-12 max-w-5xl mx-auto">
      {/* Header */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl p-5 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-xs text-emerald-600 dark:text-emerald-400 font-semibold mb-1">
            <Bookmark className="w-4 h-4" />
            <span>প্রামাণ্য গাণিতিক তত্ত্ব ও সূত্রাবলি</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white">
            থিওরি ও সূত্র ভল্ট
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            ৩৬টি অধ্যায়ের মূল গাণিতিক তত্ত্ব, প্রমাণ্য সূত্রাবলি, শর্টকাট টেকনিক ও সতর্কতামূলক ফাঁদ।
          </p>
        </div>

        {/* Search */}
        <div className="relative w-full md:w-64">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="সূত্র, তত্ত্ব বা নিয়ম খুঁজুন..."
            className="w-full pl-9 pr-4 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
        </div>
      </div>

      {/* Filter Bar: Topic Select + Type Pills + Bookmark + Flashcard Mode */}
      <div className="space-y-3">
        {/* Type Filter Pills */}
        <div className="flex items-center space-x-2 overflow-x-auto pb-1 scrollbar-none">
          {conceptTypes.map((t) => {
            const Icon = t.icon;
            const isActive = selectedType === t.id;
            return (
              <button
                key={t.id}
                onClick={() => setSelectedType(t.id)}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition ${
                  isActive
                    ? 'bg-emerald-600 text-white shadow-sm'
                    : 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{t.label}</span>
              </button>
            );
          })}
        </div>

        {/* Second Row: Chapter Dropdown & Toggles */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold text-slate-500">অধ্যায়:</span>
            <select
              value={selectedTopic}
              onChange={(e) => setSelectedTopic(e.target.value)}
              className="text-xs font-semibold px-3 py-2 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            >
              <option value="all">সকল অধ্যায় ({formulas.length}টি থিওরি ও সূত্র)</option>
              {topicsList.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setOnlyBookmarked(!onlyBookmarked)}
              className={`flex items-center space-x-1.5 px-3 py-2 rounded-xl border text-xs font-semibold transition ${
                onlyBookmarked
                  ? 'bg-amber-50 border-amber-300 text-amber-800 dark:bg-amber-950 dark:border-amber-800 dark:text-amber-300'
                  : 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300'
              }`}
            >
              <Star className={`w-3.5 h-3.5 ${onlyBookmarked ? 'fill-amber-500 text-amber-500' : ''}`} />
              <span>বুকমার্ক করা আইটেম</span>
            </button>

            <button
              onClick={() => setFlashcardMode(!flashcardMode)}
              className={`flex items-center space-x-1.5 px-3 py-2 rounded-xl border text-xs font-semibold transition ${
                flashcardMode
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300'
              }`}
            >
              {flashcardMode ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
              <span>ফ্ল্যাশকার্ড মেমরি টেস্ট</span>
            </button>
          </div>
        </div>
      </div>

      {/* Formulas & Theory Grid */}
      {filteredFormulas.length === 0 ? (
        <div className="bg-white dark:bg-slate-900 p-12 rounded-2xl border border-slate-200 dark:border-slate-800 text-center text-slate-500">
          <BookOpen className="w-10 h-10 text-slate-400 mx-auto mb-2 opacity-80" />
          <p className="text-sm font-semibold">
            নির্বাচিত ফিল্টারে কোনো থিওরি বা সূত্র পাওয়া যায়নি।
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredFormulas.map((f) => {
            const isCopied = copiedId === f.id;
            const isRevealed = !flashcardMode || revealedIds[f.id];

            return (
              <div
                key={f.id}
                className="bg-white dark:bg-slate-900 rounded-2xl p-5 border border-slate-200 dark:border-slate-800 transition flex flex-col justify-between shadow-sm hover:shadow-md space-y-4"
              >
                <div>
                  {/* Badge Row & Actions */}
                  <div className="flex items-center justify-between mb-2.5">
                    <div className="flex items-center space-x-2">
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                        {f.topic_name}
                      </span>
                      {getTypeBadge(f.concept_type)}
                    </div>

                    <div className="flex items-center space-x-1">
                      <button
                        onClick={() => toggleBookmark(f.id, f.is_bookmarked)}
                        className="p-1 rounded text-slate-400 hover:text-amber-500 transition"
                        title="বুকমার্ক"
                      >
                        <Star
                          className={`w-4 h-4 ${
                            f.is_bookmarked ? 'fill-amber-400 text-amber-400' : ''
                          }`}
                        />
                      </button>

                      <button
                        onClick={() => handleCopyFormula(f.id, f.formula)}
                        className="p-1 rounded text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition"
                        title="LaTeX সমীকরণ কপি করুন"
                      >
                        {isCopied ? (
                          <Check className="w-4 h-4 text-emerald-500" />
                        ) : (
                          <Copy className="w-4 h-4" />
                        )}
                      </button>
                    </div>
                  </div>

                  {/* Title */}
                  <h3 className="text-sm sm:text-base font-bold text-slate-900 dark:text-white leading-snug">
                    <MathView content={f.title} inline />
                  </h3>

                  {/* Formula LaTeX Display Box */}
                  <div className="my-3 p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200/80 dark:border-slate-700/60 text-xs sm:text-sm text-emerald-900 dark:text-emerald-300 leading-relaxed overflow-hidden">
                    <MathView content={f.formula} />
                  </div>

                  {/* Explanation & Rules Body (with Flashcard Reveal) */}
                  {isRevealed ? (
                    <div className="space-y-3 pt-1 text-xs">
                      {f.explanation && (
                        <div className="text-slate-700 dark:text-slate-300 leading-relaxed">
                          <MathView content={f.explanation} />
                        </div>
                      )}

                      {f.rules && f.rules.length > 0 && (
                        <div className="space-y-1 bg-slate-50 dark:bg-slate-800/40 p-3 rounded-xl border border-slate-100 dark:border-slate-800">
                          <span className="font-bold text-slate-800 dark:text-slate-200 block mb-1">
                            প্রয়োগের নিয়মাবলি:
                          </span>
                          <ul className="list-disc list-inside space-y-1 text-slate-600 dark:text-slate-400">
                            {f.rules.map((r, ri) => (
                              <li key={ri}>
                                <MathView content={r} inline />
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {f.example && (
                        <div className="p-2.5 rounded-lg bg-emerald-50/60 dark:bg-emerald-950/20 border border-emerald-200/60 dark:border-emerald-800/40 text-emerald-950 dark:text-emerald-200">
                          <strong className="block text-[11px] mb-0.5">বাস্তব উদাহরণ:</strong>
                          <MathView content={f.example} />
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-center py-4 bg-slate-50/60 dark:bg-slate-800/30 rounded-xl border border-dashed border-slate-200 dark:border-slate-700">
                      <button
                        onClick={() => toggleReveal(f.id)}
                        className="text-xs font-bold text-emerald-600 dark:text-emerald-400 hover:underline inline-flex items-center space-x-1"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>ব্যাখ্যা ও নিয়ম দেখতে ক্লিক করুন</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
