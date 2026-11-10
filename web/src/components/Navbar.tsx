import React, { useState, useEffect } from 'react';
import {
  LayoutDashboard,
  GitFork,
  GraduationCap,
  CheckCircle2,
  PenTool,
  Bookmark,
  AlertTriangle,
  RotateCcw,
  UploadCloud,
  BarChart3,
  Clock,
  Sun,
  Moon,
  Flame,
} from 'lucide-react';
import { db } from '../lib/db';

export type ScreenType =
  | 'dashboard'
  | 'curriculum'
  | 'learning'
  | 'mcq'
  | 'written'
  | 'vault'
  | 'mistakes'
  | 'analytics';

interface NavbarProps {
  currentScreen: ScreenType;
  onNavigate: (screen: ScreenType) => void;
  darkMode: boolean;
  onToggleDarkMode: () => void;
  selectedTopicId: string | null;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentScreen,
  onNavigate,
  darkMode,
  onToggleDarkMode,
}) => {
  const [timeLeft, setTimeLeft] = useState<{ hours: number; minutes: number; seconds: number }>({
    hours: 47,
    minutes: 58,
    seconds: 40,
  });

  const [pendingRevisionsCount, setPendingRevisionsCount] = useState<number>(0);
  const [mistakesCount, setMistakesCount] = useState<number>(0);

  // Poll for live badge updates
  useEffect(() => {
    async function fetchBadges() {
      try {
        const revCount = await db.revisionQueue.where('status').equals('pending').count();
        setPendingRevisionsCount(revCount);
        const misCount = await db.mistakes.where('is_resolved').equals(0 as any).count();
        setMistakesCount(misCount);
      } catch (e) {
        // ignore
      }
    }
    fetchBadges();
    const interval = setInterval(fetchBadges, 3000);
    return () => clearInterval(interval);
  }, []);

  // 48-Hour Countdown timer
  useEffect(() => {
    async function initTimer() {
      const settings = await db.settings.toCollection().first();
      const targetTime = settings?.exam_target_date
        ? new Date(settings.exam_target_date).getTime()
        : Date.now() + 48 * 3600 * 1000;

      const updateCountdown = () => {
        const diff = Math.max(0, targetTime - Date.now());
        const hours = Math.floor(diff / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);
        setTimeLeft({ hours, minutes, seconds });
      };

      updateCountdown();
      const timer = setInterval(updateCountdown, 1000);
      return () => clearInterval(timer);
    }
    initTimer();
  }, []);

  const navItems = [
    {
      id: 'dashboard' as ScreenType,
      label: 'ড্যাশবোর্ড',
      icon: LayoutDashboard,
    },
    {
      id: 'curriculum' as ScreenType,
      label: 'সিলেবাস ও গ্রাফ',
      icon: GitFork,
    },
    {
      id: 'learning' as ScreenType,
      label: 'লার্নিং রুম',
      icon: GraduationCap,
    },
    {
      id: 'mcq' as ScreenType,
      label: 'এমসিকিউ রুম',
      icon: CheckCircle2,
    },
    {
      id: 'written' as ScreenType,
      label: 'লিখিত গণিত',
      icon: PenTool,
    },
    {
      id: 'vault' as ScreenType,
      label: 'থিওরি ও সূত্র',
      icon: Bookmark,
    },
    {
      id: 'mistakes' as ScreenType,
      label: 'ভুল খাতা',
      icon: AlertTriangle,
      badge: mistakesCount > 0 ? mistakesCount : undefined,
      badgeColor: 'bg-rose-500 text-white',
    },
    {
      id: 'analytics' as ScreenType,
      label: 'পারফরম্যান্স',
      icon: BarChart3,
    },
  ];

  return (
    <header className="sticky top-0 z-50 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 shadow-sm transition-colors">
      {/* Top Banner: Brand + Sprint Timer + Controls */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand */}
          <div
            onClick={() => onNavigate('dashboard')}
            className="flex items-center space-x-3 cursor-pointer group"
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center text-white shadow-md shadow-emerald-500/20 group-hover:scale-105 transition-transform">
              <Flame className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-xl tracking-tight text-slate-900 dark:text-white">
                  MATHSPRINT<span className="text-emerald-600 dark:text-emerald-400">.BD</span>
                </span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-700">
                  বিসিএস ও ব্যাংক স্প্রিন্ট
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 hidden sm:block">
                উচ্চমানের প্রামাণ্য গণিত প্রস্তুতি ও রিভিশন প্ল্যাটফর্ম
              </p>
            </div>
          </div>

          {/* 48-Hour Exam Sprint Countdown Pill */}
          <div className="flex items-center space-x-2 bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-950/40 dark:to-orange-950/30 border border-amber-200/80 dark:border-amber-800/60 px-3.5 py-1.5 rounded-full shadow-sm">
            <Clock className="w-4 h-4 text-amber-600 dark:text-amber-400 animate-spin-slow" />
            <span className="text-xs font-semibold text-amber-800 dark:text-amber-300">
              ৪৮ ঘণ্টার স্প্রিন্ট বাকি:
            </span>
            <span className="font-mono font-bold text-xs sm:text-sm text-amber-900 dark:text-amber-200 tracking-wider">
              {String(timeLeft.hours).padStart(2, '0')}:{String(timeLeft.minutes).padStart(2, '0')}:{String(timeLeft.seconds).padStart(2, '0')}
            </span>
          </div>

          {/* Utility buttons: Dark mode only (Bangla/English toggle removed per instruction) */}
          <div className="flex items-center space-x-2">
            <button
              onClick={onToggleDarkMode}
              className="p-2 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
              title={darkMode ? 'লাইট মোড' : 'ডার্ক মোড'}
            >
              {darkMode ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
            </button>
          </div>
        </div>
      </div>

      {/* Navigation Sub-bar */}
      <div className="bg-slate-50/80 dark:bg-slate-900/90 border-t border-slate-200/70 dark:border-slate-800/80 overflow-x-auto scrollbar-none">
        <div className="max-w-7xl mx-auto px-2 sm:px-4 flex items-center space-x-1 py-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentScreen === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`relative flex items-center space-x-2 px-3 py-2 rounded-lg text-xs font-medium whitespace-nowrap transition-all ${
                  isActive
                    ? 'bg-emerald-600 text-white shadow-sm font-semibold'
                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-200/60 dark:hover:bg-slate-800/70 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-500 dark:text-slate-400'}`} />
                <span>{item.label}</span>

                {item.badge !== undefined && (
                  <span
                    className={`ml-1 px-1.5 py-0.2 text-[10px] font-bold rounded-full ${item.badgeColor}`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
};
