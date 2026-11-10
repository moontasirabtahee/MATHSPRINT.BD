import React, { useState, useEffect } from 'react';
import { Navbar, type ScreenType } from './components/Navbar';
import { initializeDatabase } from './lib/databaseInit';
import { DashboardScreen } from './screens/DashboardScreen';
import { CurriculumScreen } from './screens/CurriculumScreen';
import { LearningRoomScreen } from './screens/LearningRoomScreen';
import { MCQRoomScreen } from './screens/MCQRoomScreen';
import { WrittenRoomScreen } from './screens/WrittenRoomScreen';
import { FormulaVaultScreen } from './screens/FormulaVaultScreen';
import { MistakeNotebookScreen } from './screens/MistakeNotebookScreen';
import { AnalyticsScreen } from './screens/AnalyticsScreen';

export function App() {
  const [currentScreen, setCurrentScreen] = useState<ScreenType>('dashboard');
  const [selectedTopicId, setSelectedTopicId] = useState<string | null>('topic_01');
  const [darkMode, setDarkMode] = useState<boolean>(false);
  const [isReady, setIsReady] = useState<boolean>(false);

  useEffect(() => {
    async function setup() {
      await initializeDatabase();
      setIsReady(true);
    }
    setup();
  }, []);

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  const handleToggleDarkMode = () => {
    setDarkMode((prev) => !prev);
  };

  if (!isReady) {
    return (
      <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center text-white space-y-4">
        <div className="w-12 h-12 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-sm font-semibold tracking-wider text-emerald-400">
          MathSprint BD উপাত্ত প্রস্তুত হচ্ছে...
        </p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors">
      <Navbar
        currentScreen={currentScreen}
        onNavigate={setCurrentScreen}
        darkMode={darkMode}
        onToggleDarkMode={handleToggleDarkMode}
        selectedTopicId={selectedTopicId}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        {currentScreen === 'dashboard' && (
          <DashboardScreen
            onNavigate={setCurrentScreen}
            onSelectTopic={setSelectedTopicId}
          />
        )}

        {currentScreen === 'curriculum' && (
          <CurriculumScreen
            onNavigate={setCurrentScreen}
            onSelectTopic={setSelectedTopicId}
          />
        )}

        {currentScreen === 'learning' && (
          <LearningRoomScreen
            selectedTopicId={selectedTopicId}
            onNavigate={setCurrentScreen}
            onSelectTopic={setSelectedTopicId}
          />
        )}

        {currentScreen === 'mcq' && (
          <MCQRoomScreen
            selectedTopicId={selectedTopicId}
            onNavigate={setCurrentScreen}
            onSelectTopic={setSelectedTopicId}
          />
        )}

        {currentScreen === 'written' && (
          <WrittenRoomScreen
            selectedTopicId={selectedTopicId}
            onNavigate={setCurrentScreen}
            onSelectTopic={setSelectedTopicId}
          />
        )}

        {currentScreen === 'vault' && (
          <FormulaVaultScreen
            onNavigate={setCurrentScreen}
          />
        )}

        {currentScreen === 'mistakes' && (
          <MistakeNotebookScreen
            onNavigate={setCurrentScreen}
            onSelectTopic={setSelectedTopicId}
          />
        )}

        {currentScreen === 'analytics' && (
          <AnalyticsScreen
            onNavigate={setCurrentScreen}
          />
        )}
      </main>
    </div>
  );
}

export default App;
