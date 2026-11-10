import React, { useState } from 'react';
import { Eye, RotateCcw, Sliders } from 'lucide-react';

export type VisualizerDiagramType =
  | 'coordinate'
  | 'triangle'
  | 'circle'
  | 'transversal'
  | 'venn'
  | 'mensuration_rectangle';

interface MathVisualizerProps {
  type?: VisualizerDiagramType;
  title?: string;
  topicId?: string;
  className?: string;
}

export const MathVisualizer: React.FC<MathVisualizerProps> = ({
  type = 'coordinate',
  title,
  topicId,
  className = '',
}) => {
  // Determine diagram type by topic if not explicitly given
  let resolvedType: VisualizerDiagramType = type;
  if (topicId) {
    if (['topic_30', 'topic_31'].includes(topicId)) resolvedType = 'triangle';
    else if (['topic_32', 'topic_37'].includes(topicId)) resolvedType = 'circle';
    else if (['topic_35'].includes(topicId)) resolvedType = 'mensuration_rectangle';
    else if (['topic_28'].includes(topicId)) resolvedType = 'venn';
    else if (['topic_24', 'topic_29', 'topic_23'].includes(topicId)) resolvedType = 'coordinate';
  }

  // Interactive state for coordinate plot
  const [slope, setSlope] = useState<number>(1.5);
  const [intercept, setIntercept] = useState<number>(20);
  const [curveType, setCurveType] = useState<'linear' | 'parabola'>('linear');

  // Interactive state for right triangle
  const [triBase, setTriBase] = useState<number>(4);
  const [triHeight, setTriHeight] = useState<number>(3);
  const triHypotenuse = Math.sqrt(triBase * triBase + triHeight * triHeight).toFixed(1);

  // Interactive state for Venn diagram
  const [vennMode, setVennMode] = useState<'union' | 'intersect' | 'onlyA' | 'onlyB'>('intersect');

  return (
    <div
      className={`bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-4 sm:p-5 shadow-sm space-y-4 ${className}`}
    >
      <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <Eye className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
          <h3 className="text-xs sm:text-sm font-bold text-slate-900 dark:text-white">
            {title ||
              (resolvedType === 'triangle'
                ? 'জ্যামিতিক চিত্র: পিথাগোরাস ও সমকোণী ত্রিভুজ'
                : resolvedType === 'circle'
                ? 'জ্যামিতিক চিত্র: বৃত্ত, ব্যাসার্ধ ও স্পর্শক'
                : resolvedType === 'venn'
                ? 'ভেনচিত্র: সেট অপারেশন (A ∩ B / A ∪ B)'
                : resolvedType === 'mensuration_rectangle'
                ? 'পরিমিতি চিত্র: রাস্তা সহ আয়তাকার ক্ষেত্র'
                : 'স্থানাঙ্ক জ্যামিতি ও ফাংশন লেখচিত্র')}
          </h3>
        </div>

        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 uppercase tracking-wider">
          ইন্টারেক্টিভ ভিজ্যুয়ালাইজার
        </span>
      </div>

      {/* SVG Container */}
      <div className="relative bg-slate-50 dark:bg-slate-950/60 rounded-xl border border-slate-200/80 dark:border-slate-800/80 p-2 flex items-center justify-center overflow-hidden">
        {/* ================= 1. COORDINATE PLOT ================= */}
        {resolvedType === 'coordinate' && (
          <svg viewBox="0 0 400 240" className="w-full h-auto max-h-60 select-none">
            {/* Grid Lines */}
            <defs>
              <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                <path d="M 20 0 L 0 0 0 20" fill="none" stroke="currentColor" className="text-slate-200 dark:text-slate-800" strokeWidth="0.5" />
              </pattern>
            </defs>
            <rect width="400" height="240" fill="url(#grid)" />

            {/* X and Y Axes */}
            <line x1="20" y1="120" x2="380" y2="120" stroke="currentColor" className="text-slate-400 dark:text-slate-600" strokeWidth="1.5" />
            <line x1="200" y1="20" x2="200" y2="220" stroke="currentColor" className="text-slate-400 dark:text-slate-600" strokeWidth="1.5" />

            {/* Axis Arrows & Labels */}
            <text x="385" y="124" className="text-[10px] fill-slate-500 font-mono">X</text>
            <text x="195" y="15" className="text-[10px] fill-slate-500 font-mono">Y</text>
            <text x="185" y="135" className="text-[9px] fill-slate-400 font-mono">O(0,0)</text>

            {/* Plot Curve */}
            {curveType === 'linear' ? (
              <line
                x1="40"
                y1={120 + 160 * slope * 0.2 - intercept}
                x2="360"
                y2={120 - 160 * slope * 0.2 - intercept}
                stroke="#10b981"
                strokeWidth="2.5"
                strokeLinecap="round"
              />
            ) : (
              <path
                d="M 60 40 Q 200 200 340 40"
                fill="none"
                stroke="#06b6d4"
                strokeWidth="2.5"
                strokeLinecap="round"
              />
            )}

            {/* Function Equation Tag */}
            <rect x="230" y="25" width="150" height="30" rx="6" fill="currentColor" className="text-white dark:text-slate-800 shadow-sm" opacity="0.9" />
            <text x="240" y="45" className="text-[11px] font-mono font-bold fill-emerald-600 dark:fill-emerald-400">
              {curveType === 'linear'
                ? `y = ${slope}x + ${intercept > 0 ? intercept : intercept}`
                : `y = ax² + bx + c`}
            </text>
          </svg>
        )}

        {/* ================= 2. RIGHT TRIANGLE (PYTHAGORAS) ================= */}
        {resolvedType === 'triangle' && (
          <svg viewBox="0 0 400 240" className="w-full h-auto max-h-60 select-none">
            {/* Triangle Shape */}
            <polygon
              points="80,190 320,190 80,50"
              fill="rgba(16, 185, 129, 0.12)"
              stroke="#10b981"
              strokeWidth="2.5"
              strokeLinejoin="round"
            />
            {/* Right Angle Box */}
            <polyline points="80,170 100,170 100,190" fill="none" stroke="#10b981" strokeWidth="1.5" />

            {/* Side Labels */}
            <text x="185" y="210" className="text-xs font-bold fill-slate-700 dark:fill-slate-200">ভূমি (Base) = {triBase}</text>
            <text x="15" y="125" className="text-xs font-bold fill-slate-700 dark:fill-slate-200">উচ্চতা (h) = {triHeight}</text>
            <text x="210" y="110" className="text-xs font-bold fill-emerald-600 dark:fill-emerald-400">
              অতিভুজ (Hyp) = {triHypotenuse}
            </text>

            {/* Formula Badge */}
            <rect x="180" y="20" width="200" height="40" rx="8" fill="currentColor" className="text-white dark:text-slate-800 shadow" />
            <text x="195" y="45" className="text-[11px] font-bold font-mono fill-slate-800 dark:fill-slate-200">
              c² = a² + b² ({triHypotenuse}² = {triBase}² + {triHeight}²)
            </text>
          </svg>
        )}

        {/* ================= 3. CIRCLE GEOMETRY ================= */}
        {resolvedType === 'circle' && (
          <svg viewBox="0 0 400 240" className="w-full h-auto max-h-60 select-none">
            {/* Circle */}
            <circle cx="180" cy="120" r="80" fill="rgba(6, 182, 212, 0.1)" stroke="#06b6d4" strokeWidth="2.5" />
            {/* Center */}
            <circle cx="180" cy="120" r="3.5" fill="#0891b2" />
            <text x="175" y="112" className="text-[10px] font-bold fill-slate-600 dark:fill-slate-300 font-mono">O</text>

            {/* Radius */}
            <line x1="180" y1="120" x2="260" y2="120" stroke="#0891b2" strokeWidth="2" strokeDasharray="3,3" />
            <text x="210" y="115" className="text-xs font-bold fill-cyan-600 dark:fill-cyan-400">r</text>

            {/* Tangent Line */}
            <line x1="260" y1="30" x2="260" y2="210" stroke="#f59e0b" strokeWidth="2" />
            <text x="270" y="50" className="text-[10px] font-bold fill-amber-600 dark:fill-amber-400">স্পর্শক (Tangent)</text>

            {/* Legend Box */}
            <rect x="275" y="140" width="115" height="60" rx="8" fill="currentColor" className="text-white dark:text-slate-800 shadow" />
            <text x="285" y="160" className="text-[10px] font-mono fill-slate-700 dark:fill-slate-300">ক্ষেত্রফল = πr²</text>
            <text x="285" y="178" className="text-[10px] font-mono fill-slate-700 dark:fill-slate-300">পরিধি = 2πr</text>
            <text x="285" y="194" className="text-[10px] font-mono fill-slate-700 dark:fill-slate-300">ব্যাসার্ধ ⟂ স্পর্শক</text>
          </svg>
        )}

        {/* ================= 4. VENN DIAGRAM ================= */}
        {resolvedType === 'venn' && (
          <svg viewBox="0 0 400 240" className="w-full h-auto max-h-60 select-none">
            {/* Universal Set Rectangle */}
            <rect x="30" y="20" width="340" height="200" rx="12" fill="none" stroke="currentColor" className="text-slate-300 dark:text-slate-700" strokeWidth="1.5" />
            <text x="45" y="42" className="text-xs font-bold fill-slate-400 font-mono">U</text>

            {/* Circle A */}
            <circle
              cx="160"
              cy="120"
              r="70"
              fill={
                vennMode === 'union' || vennMode === 'onlyA'
                  ? 'rgba(16, 185, 129, 0.25)'
                  : 'rgba(16, 185, 129, 0.05)'
              }
              stroke="#10b981"
              strokeWidth="2"
            />
            {/* Circle B */}
            <circle
              cx="240"
              cy="120"
              r="70"
              fill={
                vennMode === 'union' || vennMode === 'onlyB'
                  ? 'rgba(59, 130, 246, 0.25)'
                  : 'rgba(59, 130, 246, 0.05)'
              }
              stroke="#3b82f6"
              strokeWidth="2"
            />

            {/* Overlap Intersection Highlight */}
            {vennMode === 'intersect' && (
              <path
                d="M 200 68 A 70 70 0 0 1 200 172 A 70 70 0 0 1 200 68"
                fill="rgba(168, 85, 247, 0.45)"
                stroke="#a855f7"
                strokeWidth="2"
              />
            )}

            <text x="120" y="125" className="text-sm font-bold fill-emerald-700 dark:fill-emerald-300 font-mono">A</text>
            <text x="270" y="125" className="text-sm font-bold fill-blue-700 dark:fill-blue-300 font-mono">B</text>
            <text x="187" y="125" className="text-xs font-bold fill-purple-700 dark:fill-purple-300 font-mono">A∩B</text>
          </svg>
        )}

        {/* ================= 5. MENSURATION RECTANGLE WITH PATH ================= */}
        {resolvedType === 'mensuration_rectangle' && (
          <svg viewBox="0 0 400 240" className="w-full h-auto max-h-60 select-none">
            {/* Outer Rectangle (Field + Path) */}
            <rect x="50" y="40" width="300" height="160" rx="8" fill="rgba(245, 158, 11, 0.15)" stroke="#f59e0b" strokeWidth="2" strokeDasharray="4,4" />
            {/* Inner Rectangle (Field) */}
            <rect x="90" y="70" width="220" height="100" rx="4" fill="rgba(16, 185, 129, 0.25)" stroke="#10b981" strokeWidth="2.5" />

            {/* Labels */}
            <text x="175" y="125" className="text-xs font-bold fill-emerald-800 dark:fill-emerald-200">মূল বাগান (L × W)</text>
            <text x="175" y="55" className="text-[10px] font-bold fill-amber-700 dark:fill-amber-300">চারপাশে x মিটার চওড়া রাস্তা</text>

            <line x1="90" y1="180" x2="310" y2="180" stroke="#10b981" strokeWidth="1.5" />
            <text x="190" y="195" className="text-[11px] font-bold fill-slate-700 dark:fill-slate-300">দৈর্ঘ্য L</text>

            <line x1="320" y1="70" x2="320" y2="170" stroke="#10b981" strokeWidth="1.5" />
            <text x="325" y="125" className="text-[11px] font-bold fill-slate-700 dark:fill-slate-300">প্রস্থ W</text>
          </svg>
        )}
      </div>

      {/* Interactive Controls Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 pt-1 text-xs">
        {resolvedType === 'coordinate' && (
          <div className="flex items-center space-x-3 w-full">
            <span className="font-semibold text-slate-600 dark:text-slate-300 flex items-center space-x-1">
              <Sliders className="w-3.5 h-3.5" />
              <span>ঢাল (Slope m): {slope}</span>
            </span>
            <input
              type="range"
              min="0.5"
              max="3"
              step="0.5"
              value={slope}
              onChange={(e) => setSlope(parseFloat(e.target.value))}
              className="flex-1 accent-emerald-600"
            />
            <button
              onClick={() => setCurveType(curveType === 'linear' ? 'parabola' : 'linear')}
              className="px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 font-semibold hover:bg-slate-200 text-slate-700 dark:text-slate-300"
            >
              {curveType === 'linear' ? 'প্যারাবোলা দেখুন' : 'সরলরেখা দেখুন'}
            </button>
          </div>
        )}

        {resolvedType === 'triangle' && (
          <div className="flex items-center space-x-3 w-full">
            <span className="font-semibold text-slate-600 dark:text-slate-300">
              বাহু পরিবর্তন:
            </span>
            <button
              onClick={() => {
                setTriBase(4);
                setTriHeight(3);
              }}
              className={`px-2.5 py-1 rounded-lg font-semibold ${
                triBase === 4 ? 'bg-emerald-600 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-700'
              }`}
            >
              ৩, ৪, ৫ ট্রিপ্লেট
            </button>
            <button
              onClick={() => {
                setTriBase(12);
                setTriHeight(5);
              }}
              className={`px-2.5 py-1 rounded-lg font-semibold ${
                triBase === 12 ? 'bg-emerald-600 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-700'
              }`}
            >
              ৫, ১২, ১৩ ট্রিপ্লেট
            </button>
            <button
              onClick={() => {
                setTriBase(15);
                setTriHeight(8);
              }}
              className={`px-2.5 py-1 rounded-lg font-semibold ${
                triBase === 15 ? 'bg-emerald-600 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-700'
              }`}
            >
              ৮, ১৫, ১৭ ট্রিপ্লেট
            </button>
          </div>
        )}

        {resolvedType === 'venn' && (
          <div className="flex items-center space-x-2 w-full">
            <span className="font-semibold text-slate-600 dark:text-slate-300">
              অপারেশন দেখুন:
            </span>
            <button
              onClick={() => setVennMode('intersect')}
              className={`px-2.5 py-1 rounded-lg font-semibold ${
                vennMode === 'intersect' ? 'bg-purple-600 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-700'
              }`}
            >
              ছেদ সেট (A ∩ B)
            </button>
            <button
              onClick={() => setVennMode('union')}
              className={`px-2.5 py-1 rounded-lg font-semibold ${
                vennMode === 'union' ? 'bg-emerald-600 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-700'
              }`}
            >
              সংযোগ সেট (A ∪ B)
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

