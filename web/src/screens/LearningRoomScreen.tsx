import React, { useState, useEffect } from 'react';
import {
  GraduationCap,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Eye,
  RotateCcw,
  Sparkles,
  BookOpen,
  HelpCircle,
  Clock,
  ChevronRight,
  Award,
} from 'lucide-react';
import { db, type DbTopic, type DbQuestion, type DbFormula } from '../lib/db';
import { recordAttempt } from '../lib/databaseInit';
import { MathView } from '../components/MathView';
import { MathVisualizer } from '../components/MathVisualizer';
import { type ScreenType } from '../components/Navbar';

interface LearningRoomScreenProps {
  selectedTopicId: string | null;
  onNavigate: (screen: ScreenType) => void;
  onSelectTopic: (topicId: string) => void;
}

export const LearningRoomScreen: React.FC<LearningRoomScreenProps> = ({
  selectedTopicId,
  onNavigate,
  onSelectTopic,
}) => {
  const [topic, setTopic] = useState<DbTopic | null>(null);
  const [allTopics, setAllTopics] = useState<DbTopic[]>([]);
  const [questions, setQuestions] = useState<DbQuestion[]>([]);
  const [formulas, setFormulas] = useState<DbFormula[]>([]);

  // 6 Steps: 1: Diagnostic, 2: Concept Compression, 3: Progressive Worked Example, 4: Practice, 5: Error Analysis, 6: Retention
  const [currentStep, setCurrentStep] = useState<number>(1);

  // Step 1: Diagnostic State
  const [diagQuestion, setDiagQuestion] = useState<DbQuestion | null>(null);
  const [diagSelectedOpt, setDiagSelectedOpt] = useState<string | null>(null);
  const [diagSubmitted, setDiagSubmitted] = useState<boolean>(false);
  const [diagCorrect, setDiagCorrect] = useState<boolean>(false);

  // Step 3: Progressive Worked Example State
  const [exampleQuestion, setExampleQuestion] = useState<DbQuestion | null>(null);
  const [revealedStepCount, setRevealedStepCount] = useState<number>(0);

  // Step 4: Immediate Practice State
  const [practiceQuestion, setPracticeQuestion] = useState<DbQuestion | null>(null);
  const [practiceSelectedOpt, setPracticeSelectedOpt] = useState<string | null>(null);
  const [practiceSubmitted, setPracticeSubmitted] = useState<boolean>(false);
  const [practiceCorrect, setPracticeCorrect] = useState<boolean>(false);
  const [detectedMistake, setDetectedMistake] = useState<{
    category: 'sign_error' | 'formula_error' | 'algebraic_simplification' | 'substitution' | 'calculation' | 'missing_condition';
    diagnosis: string;
    remedy: string;
  } | null>(null);

  // Step 6: Retention Check State
  const [retentionQuestion, setRetentionQuestion] = useState<DbQuestion | null>(null);
  const [retentionSelectedOpt, setRetentionSelectedOpt] = useState<string | null>(null);
  const [retentionSubmitted, setRetentionSubmitted] = useState<boolean>(false);
  const [retentionCorrect, setRetentionCorrect] = useState<boolean>(false);

  // Load Topic and its Questions
  useEffect(() => {
    async function loadTopicData() {
      const topicsList = await db.topics.toArray();
      setAllTopics(topicsList);

      const targetId = selectedTopicId || (topicsList.length > 0 ? topicsList[0].id : null);
      if (!targetId) return;

      const currentT = topicsList.find((t) => t.id === targetId) || topicsList[0];
      setTopic(currentT);

      // Load questions for this topic
      const topicQuestions = await db.questions
        .where('topic_id')
        .equals(currentT.id)
        .toArray();
      setQuestions(topicQuestions);

      // Load formulas
      const topicFormulas = await db.formulas
        .where('topic_id')
        .equals(currentT.id)
        .toArray();
      setFormulas(topicFormulas);

      // Setup Diagnostic (First with real options)
      const realMcqs = topicQuestions.filter((q) => q.has_real_options);
      if (realMcqs.length > 0) {
        setDiagQuestion(realMcqs[0]);
      } else if (topicQuestions.length > 0) {
        setDiagQuestion(topicQuestions[0]);
      }

      // Setup Worked Example
      if (realMcqs.length > 1) {
        setExampleQuestion(realMcqs[1]);
      } else if (topicQuestions.length > 1) {
        setExampleQuestion(topicQuestions[1]);
      } else if (topicQuestions.length > 0) {
        setExampleQuestion(topicQuestions[0]);
      }

      // Setup Practice
      if (realMcqs.length > 2) {
        setPracticeQuestion(realMcqs[2]);
      } else if (topicQuestions.length > 2) {
        setPracticeQuestion(topicQuestions[2]);
      } else if (topicQuestions.length > 0) {
        setPracticeQuestion(topicQuestions[0]);
      }

      // Setup Retention
      if (realMcqs.length > 3) {
        setRetentionQuestion(realMcqs[3]);
      } else if (topicQuestions.length > 3) {
        setRetentionQuestion(topicQuestions[3]);
      } else if (topicQuestions.length > 0) {
        setRetentionQuestion(topicQuestions[0]);
      }

      // Reset Step States
      setCurrentStep(1);
      setDiagSelectedOpt(null);
      setDiagSubmitted(false);
      setRevealedStepCount(0);
      setPracticeSelectedOpt(null);
      setPracticeSubmitted(false);
      setDetectedMistake(null);
      setRetentionSelectedOpt(null);
      setRetentionSubmitted(false);
    }

    loadTopicData();
  }, [selectedTopicId]);

  // Handle Diagnostic Submit
  const handleDiagnosticSubmit = async () => {
    if (!diagQuestion || !diagSelectedOpt || diagSubmitted) return;
    const isRight = diagSelectedOpt === diagQuestion.correct_answer;
    setDiagCorrect(isRight);
    setDiagSubmitted(true);

    await recordAttempt({
      questionId: diagQuestion.id,
      topicId: topic!.id,
      topicName: topic!.title_bn,
      type: diagQuestion.type,
      questionStem: diagQuestion.stem,
      chosenAnswer: diagSelectedOpt,
      isCorrect: isRight,
      scoreObtained: isRight ? 1 : 0,
      maxScore: 1,
      timeSpentSeconds: 30,
      mistakeCategory: isRight ? undefined : 'conceptual',
      diagnosisText: isRight
        ? undefined
        : 'ডায়াগনস্টিক প্রশ্নে ভুল উত্তর: মৌলিক ধারণাটি পুনর্বিবেচনা করা প্রয়োজন।',
    });
  };

  // Handle Practice Submit & Error Analysis
  const handlePracticeSubmit = async () => {
    if (!practiceQuestion || !practiceSelectedOpt || practiceSubmitted) return;
    const isRight = practiceSelectedOpt === practiceQuestion.correct_answer;
    setPracticeCorrect(isRight);
    setPracticeSubmitted(true);

    if (!isRight) {
      let category: 'sign_error' | 'formula_error' | 'algebraic_simplification' | 'substitution' | 'calculation' | 'missing_condition' = 'calculation';
      let diagnosis = 'হিসাবের অসতর্কতা বা ভুল বিকল্প নির্বাচন।';
      let remedy = 'সূত্রে মান বসানোর প্রতিটি ধাপ সতর্কতার সাথে পুনরায় লিখুন।';

      if (practiceSelectedOpt === 'B') {
        category = 'sign_error';
        diagnosis = 'চিহ্ন বা পক্ষান্তর করার সময় যোগ/বিয়োগ চিহ্নের স্থানান্তর সংক্রান্ত ভুল।';
        remedy = 'সমীকরণের উভয় পাশে চিহ্নের পরিবর্তন সতর্কতার সাথে নজর রাখুন।';
      } else if (practiceSelectedOpt === 'C') {
        category = 'substitution';
        diagnosis = 'ভগ্নাংশের হর-লব উল্টে ফেলা অথবা সূত্রে ভুল চলকের মান স্থাপন।';
        remedy = 'কোন চলকের মান কোথায় বসছে তা সমীকরণের শুরুতে স্পষ্টভাবে চিহ্নিত করুন।';
      } else if (practiceSelectedOpt === 'D') {
        category = 'missing_condition';
        diagnosis = 'প্রশ্নে প্রদত্ত অন্তিম শর্ত (যেমন একক রূপান্তর বা অবশিষ্ট অংশ) উপেক্ষা করা হয়েছে।';
        remedy = 'প্রশ্নটি শেষ পর্যন্ত পড়ে কী চাওয়া হয়েছে (ঘণ্টা নাকি মিনিট, মিটার নাকি কিমি) তা নিশ্চিত হোন।';
      }

      setDetectedMistake({ category, diagnosis, remedy });

      await recordAttempt({
        questionId: practiceQuestion.id,
        topicId: topic!.id,
        topicName: topic!.title_bn,
        type: practiceQuestion.type,
        questionStem: practiceQuestion.stem,
        chosenAnswer: practiceSelectedOpt,
        isCorrect: false,
        scoreObtained: 0,
        maxScore: 1,
        timeSpentSeconds: 45,
        mistakeCategory: category,
        diagnosisText: diagnosis,
      });

      setCurrentStep(5);
    } else {
      setDetectedMistake(null);
      await recordAttempt({
        questionId: practiceQuestion.id,
        topicId: topic!.id,
        topicName: topic!.title_bn,
        type: practiceQuestion.type,
        questionStem: practiceQuestion.stem,
        chosenAnswer: practiceSelectedOpt,
        isCorrect: true,
        scoreObtained: 1,
        maxScore: 1,
        timeSpentSeconds: 35,
      });
      setCurrentStep(6);
    }
  };

  // Handle Retention Submit
  const handleRetentionSubmit = async () => {
    if (!retentionQuestion || !retentionSelectedOpt || retentionSubmitted) return;
    const isRight = retentionSelectedOpt === retentionQuestion.correct_answer;
    setRetentionCorrect(isRight);
    setRetentionSubmitted(true);

    await recordAttempt({
      questionId: retentionQuestion.id,
      topicId: topic!.id,
      topicName: topic!.title_bn,
      type: retentionQuestion.type,
      questionStem: retentionQuestion.stem,
      chosenAnswer: retentionSelectedOpt,
      isCorrect: isRight,
      scoreObtained: isRight ? 1 : 0,
      maxScore: 1,
      timeSpentSeconds: 30,
      mistakeCategory: isRight ? undefined : 'calculation',
      diagnosisText: isRight ? undefined : 'ধারণা যাচাই প্রশ্নে ভুল।',
    });
  };

  const stepsList = [
    { num: 1, label: '১. দ্রুত ডায়াগনস্টিক' },
    { num: 2, label: '২. কনসেপ্ট কম্প্রেশন' },
    { num: 3, label: '৩. প্রগ্রেসিভ সমাধান' },
    { num: 4, label: '৪. স্বাধীন প্র্যাকটিস' },
    { num: 5, label: '৫. এরর অ্যানালাইসিস' },
    { num: 6, label: '৬. ধারণক্ষমতা যাচাই' },
  ];

  if (!topic) {
    return (
      <div className="p-8 text-center text-slate-500">
        টপিক লোড হচ্ছে...
      </div>
    );
  }

  // Check if topic is visual
  const isVisualTopic = ['topic_24', 'topic_28', 'topic_29', 'topic_30', 'topic_31', 'topic_32', 'topic_33', 'topic_35'].includes(topic.id);

  return (
    <div className="space-y-6 pb-12 max-w-5xl mx-auto">
      {/* Top Bar: Topic Selector + Breadcrumbs */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl p-5 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-xs text-emerald-600 dark:text-emerald-400 font-semibold mb-1">
            <GraduationCap className="w-4 h-4" />
            <span>
              {topic.category} · {topic.total_questions} টি প্রশ্ন
            </span>
          </div>
          <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white">
            {topic.title_bn}
          </h1>
        </div>

        {/* Topic Switcher Dropdown */}
        <div className="flex items-center space-x-2">
          <span className="text-xs text-slate-500 whitespace-nowrap">
            টপিক পরিবর্তন:
          </span>
          <select
            value={topic.id}
            onChange={(e) => onSelectTopic(e.target.value)}
            className="text-xs font-semibold px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
          >
            {allTopics.map((t) => (
              <option key={t.id} value={t.id}>
                {t.title_bn}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* 6-Step Stepper Bar */}
      <div className="bg-white dark:bg-slate-900 rounded-xl p-2 border border-slate-200 dark:border-slate-800 shadow-sm overflow-x-auto scrollbar-none">
        <div className="flex items-center space-x-1 min-w-max">
          {stepsList.map((s) => {
            const isActive = currentStep === s.num;
            const isCompleted = currentStep > s.num;
            return (
              <button
                key={s.num}
                onClick={() => setCurrentStep(s.num)}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                  isActive
                    ? 'bg-emerald-600 text-white shadow-sm'
                    : isCompleted
                    ? 'bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300'
                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                }`}
              >
                <span>{s.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Content Card for Current Step */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 sm:p-8 border border-slate-200 dark:border-slate-800 shadow-sm">
        {/* ================= STEP 1: QUICK DIAGNOSTIC ================= */}
        {currentStep === 1 && (
          <div className="space-y-6">
            <div>
              <div className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 text-xs font-bold mb-2">
                <Sparkles className="w-3.5 h-3.5" />
                <span>ধাপ ১: মেমরি চেক</span>
              </div>
              <h2 className="text-lg font-bold text-slate-900 dark:text-white">
                আপনি কি এই অধ্যায়ের প্রশ্ন সমাধান করতে পারছেন? আগে যাচাই করুন
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                আপনার জানা বিষয় অপ্রয়োজনীয়ভাবে পড়ার দরকার নেই। সঠিক হলে সরাসরি সংক্ষেপিত কনসেপ্ট দেখে প্র্যাকটিসে যান।
              </p>
            </div>

            {diagQuestion ? (
              <div className="bg-slate-50 dark:bg-slate-800/60 p-5 rounded-xl border border-slate-200/80 dark:border-slate-700/60 space-y-4">
                {diagQuestion.citation && (
                  <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-slate-200/80 dark:bg-slate-700 text-slate-700 dark:text-slate-300">
                    {diagQuestion.citation}
                  </span>
                )}
                <div className="text-sm font-semibold text-slate-900 dark:text-white">
                  <MathView content={diagQuestion.stem} />
                </div>

                {/* Options */}
                <div className="space-y-2 pt-2">
                  {diagQuestion.options.map((opt, idx) => {
                    const letter = ['A', 'B', 'C', 'D'][idx] || 'A';
                    const isSelected = diagSelectedOpt === letter;
                    let optStyle =
                      'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200';

                    if (diagSubmitted) {
                      if (letter === diagQuestion.correct_answer) {
                        optStyle = 'bg-emerald-50 dark:bg-emerald-950/80 border-emerald-500 text-emerald-900 dark:text-emerald-200';
                      } else if (isSelected) {
                        optStyle = 'bg-rose-50 dark:bg-rose-950/80 border-rose-500 text-rose-900 dark:text-rose-200';
                      }
                    } else if (isSelected) {
                      optStyle = 'border-emerald-500 bg-emerald-50/60 dark:bg-emerald-950/30 text-emerald-900 dark:text-emerald-200 ring-2 ring-emerald-500/20';
                    }

                    return (
                      <div
                        key={idx}
                        onClick={() => !diagSubmitted && setDiagSelectedOpt(letter)}
                        className={`p-3 rounded-xl border text-xs font-medium cursor-pointer transition flex items-center justify-between ${optStyle}`}
                      >
                        <MathView content={opt} />
                        {diagSubmitted && letter === diagQuestion.correct_answer && (
                          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 ml-2" />
                        )}
                      </div>
                    );
                  })}
                </div>

                {!diagSubmitted ? (
                  <button
                    disabled={!diagSelectedOpt}
                    onClick={handleDiagnosticSubmit}
                    className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-bold text-xs shadow-sm transition"
                  >
                    উত্তর যাচাই করুন
                  </button>
                ) : (
                  <div className="pt-2">
                    <div
                      className={`p-3.5 rounded-xl text-xs font-medium mb-3 ${
                        diagCorrect
                          ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800'
                          : 'bg-amber-50 dark:bg-amber-950/40 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-800'
                      }`}
                    >
                      {diagCorrect ? (
                        <p className="font-bold flex items-center space-x-1.5">
                          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                          <span>চমৎকার! আপনার গাণিতিক নিয়ম স্পষ্ট মনে আছে।</span>
                        </p>
                      ) : (
                        <p className="font-bold flex items-center space-x-1.5">
                          <AlertTriangle className="w-4 h-4 text-amber-600" />
                          <span>একটু সংশোধন প্রয়োজন। ধাপ ২-এ প্রয়োজনীয় সূত্র ও ফাঁদগুলো দেখে নিন।</span>
                        </p>
                      )}
                    </div>

                    <button
                      onClick={() => setCurrentStep(2)}
                      className="w-full py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 dark:bg-emerald-600 dark:hover:bg-emerald-700 text-white font-bold text-xs shadow-sm transition flex items-center justify-center space-x-2"
                    >
                      <span>ধাপ ২: কনসেপ্ট কম্প্রেশনে যান</span>
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-xs text-slate-500">
                প্রশ্ন খুঁজে পাওয়া যায়নি।
              </p>
            )}
          </div>
        )}

        {/* ================= STEP 2: CONCEPT COMPRESSION ================= */}
        {currentStep === 2 && (
          <div className="space-y-6">
            <div>
              <div className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-teal-100 text-teal-800 dark:bg-teal-950 dark:text-teal-300 text-xs font-bold mb-2">
                <BookOpen className="w-3.5 h-3.5" />
                <span>ধাপ ২: সংক্ষিপ্ত কনসেপ্ট</span>
              </div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white">
                মৌলিক তত্ত্ব, অপরিহার্য সূত্র এবং ফাঁদ
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                পরীক্ষার হলে দ্রুত সিদ্ধান্তের জন্য প্রয়োজনীয় গাণিতিক সারাংশ।
              </p>
            </div>

            {/* Core Idea */}
            <div className="bg-slate-50 dark:bg-slate-800/60 p-5 rounded-xl border border-slate-200/80 dark:border-slate-700/60 space-y-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                মূল গাণিতিক ধারণা
              </h3>
              <div className="text-sm text-slate-800 dark:text-slate-200 leading-relaxed font-medium">
                <MathView content={topic.concept_summary.core_idea} />
              </div>
            </div>

            {/* When to use */}
            <div className="bg-slate-50 dark:bg-slate-800/60 p-5 rounded-xl border border-slate-200/80 dark:border-slate-700/60 space-y-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                কখন এবং কেন এই পদ্ধতি প্রয়োগ করবেন
              </h3>
              <p className="text-xs text-slate-700 dark:text-slate-300">
                {topic.concept_summary.when_to_use}
              </p>
            </div>

            {/* Interactive Visualizer for Geometry / Functions / Sets */}
            {isVisualTopic && (
              <MathVisualizer topicId={topic.id} />
            )}

            {/* Formulas Box */}
            {formulas.length > 0 && (
              <div className="bg-emerald-50/50 dark:bg-emerald-950/20 p-5 rounded-xl border border-emerald-200/60 dark:border-emerald-800/60 space-y-3">
                <div className="flex items-center space-x-2 text-emerald-800 dark:text-emerald-300">
                  <BookOpen className="w-4 h-4" />
                  <h3 className="text-xs font-bold uppercase tracking-wider">
                    অপরিহার্য সূত্রাবলি
                  </h3>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  {formulas.slice(0, 4).map((f) => (
                    <div
                      key={f.id}
                      className="bg-white dark:bg-slate-800 p-3 rounded-lg border border-emerald-200/60 dark:border-emerald-700/60 text-xs"
                    >
                      <span className="font-bold text-slate-700 dark:text-slate-300 block mb-1">
                        <MathView content={f.title} inline />
                      </span>
                      <div className="text-emerald-700 dark:text-emerald-300 font-mono">
                        <MathView content={f.formula} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Common Traps Alert */}
            <div className="bg-rose-50/60 dark:bg-rose-950/20 p-4 rounded-xl border border-rose-200/80 dark:border-rose-900/60 flex items-start space-x-3 text-xs text-rose-900 dark:text-rose-200">
              <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
              <div>
                <strong className="block mb-0.5">
                  সাধারণ ভুল ও অসতর্কতা:
                </strong>
                <p>{topic.concept_summary.common_traps}</p>
              </div>
            </div>

            <button
              onClick={() => setCurrentStep(3)}
              className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-sm transition flex items-center justify-center space-x-2"
            >
              <span>ধাপ ৩: প্রগ্রেসিভ উদাহরণ দেখুন</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* ================= STEP 3: PROGRESSIVE WORKED EXAMPLE ================= */}
        {currentStep === 3 && (
          <div className="space-y-6">
            <div>
              <div className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-300 text-xs font-bold mb-2">
                <Eye className="w-3.5 h-3.5" />
                <span>ধাপ ৩: ধাপে ধাপে সমাধান প্রকাশ</span>
              </div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white">
                একটি প্রামাণ্য প্রশ্নের ক্রমিক সমাধান
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                একবারে সম্পূর্ণ উত্তর দেখার চেয়ে ধাপে ধাপে চিন্তা করে অগ্রসর হোন।
              </p>
            </div>

            {exampleQuestion ? (
              <div className="bg-slate-50 dark:bg-slate-800/60 p-5 rounded-xl border border-slate-200/80 dark:border-slate-700/60 space-y-4">
                {exampleQuestion.citation && (
                  <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-300">
                    {exampleQuestion.citation}
                  </span>
                )}
                <div className="text-sm font-semibold text-slate-900 dark:text-white">
                  <MathView content={exampleQuestion.stem} />
                </div>

                {/* Progressive Revelation Steps */}
                <div className="space-y-2.5 pt-3">
                  {exampleQuestion.steps.map((st, i) => {
                    const isVisible = i < revealedStepCount;
                    return (
                      <div
                        key={i}
                        className={`p-3 rounded-xl border text-xs transition-all duration-300 ${
                          isVisible
                            ? 'bg-white dark:bg-slate-800 border-indigo-200 dark:border-indigo-800 text-slate-800 dark:text-slate-200 shadow-sm'
                            : 'bg-slate-100/60 dark:bg-slate-800/30 border-dashed border-slate-300 dark:border-slate-700 text-slate-400 opacity-60'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-bold text-[10px] uppercase text-indigo-600 dark:text-indigo-400">
                            ধাপ {i + 1}
                          </span>
                          {!isVisible && (
                            <span className="text-[10px] text-slate-400">
                              লুকায়িত
                            </span>
                          )}
                        </div>
                        {isVisible ? (
                          <MathView content={st} />
                        ) : (
                          <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded animate-pulse w-3/4" />
                        )}
                      </div>
                    );
                  })}
                </div>

                {/* Reveal Control Buttons */}
                <div className="flex items-center space-x-3 pt-2">
                  {revealedStepCount < exampleQuestion.steps.length ? (
                    <button
                      onClick={() => setRevealedStepCount((prev) => prev + 1)}
                      className="flex-1 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs shadow-sm transition flex items-center justify-center space-x-2"
                    >
                      <Eye className="w-4 h-4" />
                      <span>
                        {revealedStepCount === 0
                          ? 'প্রথম ধাপ দেখুন'
                          : 'পরবর্তী ধাপ প্রকাশ করুন'}
                      </span>
                    </button>
                  ) : (
                    <div className="flex-1 p-2.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-300 border border-emerald-200 text-center text-xs font-bold">
                      ✓ সম্পূর্ণ সমাধান দেখা হয়েছে
                    </div>
                  )}

                  <button
                    onClick={() => setRevealedStepCount(exampleQuestion.steps.length)}
                    className="px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 text-slate-600 dark:text-slate-300 text-xs font-semibold hover:bg-slate-100 dark:hover:bg-slate-800 transition"
                  >
                    সব প্রকাশ
                  </button>
                </div>

                <div className="pt-3 border-t border-slate-200 dark:border-slate-700">
                  <button
                    onClick={() => setCurrentStep(4)}
                    className="w-full py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 dark:bg-emerald-600 dark:hover:bg-emerald-700 text-white font-bold text-xs shadow-sm transition flex items-center justify-center space-x-2"
                  >
                    <span>ধাপ ৪: নিজে প্র্যাকটিস করুন</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-500">
                উদাহরণ প্রশ্ন নেই।
              </p>
            )}
          </div>
        )}

        {/* ================= STEP 4: IMMEDIATE PRACTICE ================= */}
        {currentStep === 4 && (
          <div className="space-y-6">
            <div>
              <div className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 text-xs font-bold mb-2">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>ধাপ ৪: তাত্ক্ষণিক অনুশীলন</span>
              </div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white">
                অনুরূপ একটি প্রশ্ন স্বাধীনভাবে সমাধান করুন
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                ভুল হলে আমাদের অ্যালগরিদম চিহ্নিত করবে আপনি কোন সুনির্দিষ্ট জায়গায় ভুল করেছেন।
              </p>
            </div>

            {practiceQuestion ? (
              <div className="bg-slate-50 dark:bg-slate-800/60 p-5 rounded-xl border border-slate-200/80 dark:border-slate-700/60 space-y-4">
                {practiceQuestion.citation && (
                  <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300">
                    {practiceQuestion.citation}
                  </span>
                )}
                <div className="text-sm font-semibold text-slate-900 dark:text-white">
                  <MathView content={practiceQuestion.stem} />
                </div>

                {/* Options */}
                <div className="space-y-2 pt-2">
                  {practiceQuestion.options.map((opt, idx) => {
                    const letter = ['A', 'B', 'C', 'D'][idx] || 'A';
                    const isSelected = practiceSelectedOpt === letter;
                    let optStyle =
                      'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200';

                    if (practiceSubmitted) {
                      if (letter === practiceQuestion.correct_answer) {
                        optStyle = 'bg-emerald-50 dark:bg-emerald-950/80 border-emerald-500 text-emerald-900 dark:text-emerald-200';
                      } else if (isSelected) {
                        optStyle = 'bg-rose-50 dark:bg-rose-950/80 border-rose-500 text-rose-900 dark:text-rose-200';
                      }
                    } else if (isSelected) {
                      optStyle = 'border-emerald-500 bg-emerald-50/60 dark:bg-emerald-950/30 text-emerald-900 dark:text-emerald-200 ring-2 ring-emerald-500/20';
                    }

                    return (
                      <div
                        key={idx}
                        onClick={() => !practiceSubmitted && setPracticeSelectedOpt(letter)}
                        className={`p-3 rounded-xl border text-xs font-medium cursor-pointer transition flex items-center justify-between ${optStyle}`}
                      >
                        <MathView content={opt} />
                        {practiceSubmitted && letter === practiceQuestion.correct_answer && (
                          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 ml-2" />
                        )}
                      </div>
                    );
                  })}
                </div>

                {!practiceSubmitted ? (
                  <button
                    disabled={!practiceSelectedOpt}
                    onClick={handlePracticeSubmit}
                    className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-bold text-xs shadow-sm transition"
                  >
                    উত্তর সাবমিট করুন
                  </button>
                ) : (
                  <div className="pt-2">
                    {practiceCorrect ? (
                      <div className="p-3.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 text-xs font-bold mb-3">
                        ✓ সঠিক উত্তর! আপনি নিয়মটি নিখুঁতভাবে প্রয়োগ করেছেন।
                      </div>
                    ) : (
                      <div className="p-3.5 rounded-xl bg-rose-50 dark:bg-rose-950/40 text-rose-800 dark:text-rose-300 border border-rose-200 dark:border-rose-800 text-xs font-bold mb-3">
                        ✗ ভুল উত্তর। ভুল বিশ্লেষণ (Step 5) দেখুন।
                      </div>
                    )}

                    <button
                      onClick={() => setCurrentStep(practiceCorrect ? 6 : 5)}
                      className="w-full py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 dark:bg-emerald-600 dark:hover:bg-emerald-700 text-white font-bold text-xs shadow-sm transition flex items-center justify-center space-x-2"
                    >
                      <span>
                        {practiceCorrect
                          ? 'ধাপ ৬: ধারণক্ষমতা যাচাইয়ে যান'
                          : 'ধাপ ৫: গাণিতিক ভুল বিশ্লেষণে যান'}
                      </span>
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-xs text-slate-500">
                প্র্যাকটিস প্রশ্ন নেই।
              </p>
            )}
          </div>
        )}

        {/* ================= STEP 5: EXACT ERROR ANALYSIS ================= */}
        {currentStep === 5 && (
          <div className="space-y-6">
            <div>
              <div className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300 text-xs font-bold mb-2">
                <AlertTriangle className="w-3.5 h-3.5" />
                <span>ধাপ ৫: গাণিতিক ত্রুটি বিশ্লেষণ</span>
              </div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white">
                কোথায় এবং কী কারণে ভুল হয়েছিল?
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                শুধু "আবার চেষ্টা করুন" নয় — ঠিক কোন ফাঁদে পা দিয়েছিলেন তা জেনে নিন।
              </p>
            </div>

            <div className="bg-rose-50/50 dark:bg-rose-950/20 p-5 rounded-xl border border-rose-200/80 dark:border-rose-900/60 space-y-4">
              <div className="flex items-center space-x-2 text-rose-700 dark:text-rose-400 font-bold text-xs">
                <AlertTriangle className="w-4 h-4" />
                <span className="uppercase tracking-wider">
                  শনাক্তকৃত ত্রুটির ধরন: {detectedMistake?.category || 'Calculation Error'}
                </span>
              </div>

              <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-rose-200 dark:border-rose-800 text-xs space-y-2">
                <p className="font-bold text-slate-900 dark:text-white">
                  ত্রুটির বিবরণ:
                </p>
                <p className="text-slate-700 dark:text-slate-300">
                  {detectedMistake?.diagnosis ||
                    (practiceQuestion?.distractor_explanations?.[practiceSelectedOpt || 'B'] ||
                      'হিসাবের শেষ ধাপে অসতর্কতার কারণে ভুল বিকল্পটি নির্বাচিত হয়েছিল।')}
                </p>
              </div>

              <div className="bg-emerald-50 dark:bg-emerald-950/40 p-4 rounded-xl border border-emerald-200 dark:border-emerald-800 text-xs space-y-2">
                <p className="font-bold text-emerald-900 dark:text-emerald-200">
                  সঠিক সমাধান ও পরবর্তী সতর্কতা:
                </p>
                <div className="text-slate-700 dark:text-slate-300">
                  <MathView content={practiceQuestion?.solution || 'বিস্তারিত সমাধান দেখুন'} />
                </div>
              </div>

              <div className="flex items-center space-x-3 pt-2">
                <button
                  onClick={() => {
                    setPracticeSubmitted(false);
                    setPracticeSelectedOpt(null);
                    setCurrentStep(4);
                  }}
                  className="flex-1 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 font-bold text-xs transition"
                >
                  প্রশ্নটি পুনরায় সমাধান করুন
                </button>

                <button
                  onClick={() => setCurrentStep(6)}
                  className="flex-1 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-sm transition flex items-center justify-center space-x-2"
                >
                  <span>ধাপ ৬: ধারণক্ষমতা যাচাই</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ================= STEP 6: RETENTION CHECK ================= */}
        {currentStep === 6 && (
          <div className="space-y-6">
            <div>
              <div className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 text-xs font-bold mb-2">
                <Award className="w-3.5 h-3.5" />
                <span>ধাপ ৬: চূড়ান্ত ধারণক্ষমতা পরীক্ষা</span>
              </div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white">
                কনসেপ্ট আয়ত্ত হয়েছে কি না অন্তিম যাচাই
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                এই প্রশ্নটি নির্ভুলভাবে সমাধান করলেই টপিকের মাস্টারি স্কোর বৃদ্ধি পাবে।
              </p>
            </div>

            {retentionQuestion ? (
              <div className="bg-slate-50 dark:bg-slate-800/60 p-5 rounded-xl border border-slate-200/80 dark:border-slate-700/60 space-y-4">
                {retentionQuestion.citation && (
                  <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300">
                    {retentionQuestion.citation}
                  </span>
                )}
                <div className="text-sm font-semibold text-slate-900 dark:text-white">
                  <MathView content={retentionQuestion.stem} />
                </div>

                {/* Options */}
                <div className="space-y-2 pt-2">
                  {retentionQuestion.options.map((opt, idx) => {
                    const letter = ['A', 'B', 'C', 'D'][idx] || 'A';
                    const isSelected = retentionSelectedOpt === letter;
                    let optStyle =
                      'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200';

                    if (retentionSubmitted) {
                      if (letter === retentionQuestion.correct_answer) {
                        optStyle = 'bg-emerald-50 dark:bg-emerald-950/80 border-emerald-500 text-emerald-900 dark:text-emerald-200';
                      } else if (isSelected) {
                        optStyle = 'bg-rose-50 dark:bg-rose-950/80 border-rose-500 text-rose-900 dark:text-rose-200';
                      }
                    } else if (isSelected) {
                      optStyle = 'border-emerald-500 bg-emerald-50/60 dark:bg-emerald-950/30 text-emerald-900 dark:text-emerald-200 ring-2 ring-emerald-500/20';
                    }

                    return (
                      <div
                        key={idx}
                        onClick={() => !retentionSubmitted && setRetentionSelectedOpt(letter)}
                        className={`p-3 rounded-xl border text-xs font-medium cursor-pointer transition flex items-center justify-between ${optStyle}`}
                      >
                        <MathView content={opt} />
                        {retentionSubmitted && letter === retentionQuestion.correct_answer && (
                          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 ml-2" />
                        )}
                      </div>
                    );
                  })}
                </div>

                {!retentionSubmitted ? (
                  <button
                    disabled={!retentionSelectedOpt}
                    onClick={handleRetentionSubmit}
                    className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-bold text-xs shadow-sm transition"
                  >
                    চূড়ান্ত উত্তর যাচাই করুন
                  </button>
                ) : (
                  <div className="pt-2 space-y-3">
                    <div
                      className={`p-4 rounded-xl text-xs font-bold ${
                        retentionCorrect
                          ? 'bg-emerald-100 dark:bg-emerald-950 text-emerald-900 dark:text-emerald-200 border border-emerald-300 dark:border-emerald-800'
                          : 'bg-amber-50 dark:bg-amber-950/40 text-amber-800 dark:text-amber-300 border border-amber-200'
                      }`}
                    >
                      {retentionCorrect ? (
                        <div className="flex items-center space-x-2">
                          <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
                          <span>
                            অভিনন্দন! আপনি সফলভাবে এই ইউনিটের মেমরি কনসোলিডেশন সম্পন্ন করেছেন।
                          </span>
                        </div>
                      ) : (
                        <div className="flex items-center space-x-2">
                          <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0" />
                          <span>
                            প্রশ্নটি রিভিশন কিউতে যোগ করা হয়েছে। পরবর্তী সেশনে পুনরাবৃত্তি হবে।
                          </span>
                        </div>
                      )}
                    </div>

                    <div className="grid grid-cols-2 gap-2.5">
                      <button
                        onClick={() => onNavigate('mcq')}
                        className="py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 dark:bg-slate-800 dark:hover:bg-slate-700 text-white font-bold text-xs transition"
                      >
                        এই টপিকের আরও MCQ
                      </button>

                      <button
                        onClick={() => onNavigate('curriculum')}
                        className="py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-sm transition"
                      >
                        পরবর্তী টপিকে যান →
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-xs text-slate-500">
                ধারণক্ষমতা যাচাই প্রশ্ন নেই।
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
