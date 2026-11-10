# MathSprint BD 🇧🇩

> **A 100% Offline, Fast-Loading, Interactive Mathematics Platform for Bangladesh Competitive Exams (BCS Preliminary, Bank Recruitment, and Govt Jobs).**

---

## 🌟 Core Features

- 📐 **থিওরি ও সূত্র ভল্ট (Theory & Formula Vault)**:
  - Covers all **36 curriculum topics** with 145+ mathematically rigorous cards.
  - Multi-level filtering: **মূল সূত্র (Core Formulas)**, **শর্টকাট হ্যাক (Shortcuts)**, **মৌলিক তত্ত্ব (Theory)**, and **পরীক্ষার ফাঁদ (Exam Traps)**.
  - Precision LaTeX KaTeX rendering with zero duplicate text rendering.
  - Flashcard recall mode for active memory testing.
- ✍️ **লিখিত গণিত (Pen & Paper Written Math)**:
  - Authentic offline workflow tailored for Bangladeshi job seekers who solve math on paper.
  - Single-click "উত্তর দেখুন" (Show Solution) and "উত্তর লুকান" (Hide Solution) toggle.
  - Complete step-by-step mathematical explanations with formulas and alternate shortcuts.
- ⏱️ **এমসিকিউ স্প্রিন্ট রুম (MCQ Practice)**:
  - Instant answer validation with timer tracking.
  - Distractor trap explanations and diagnostic question sequencing.
- 📕 **ভুল খাতা (Mistake Notebook)**:
  - Automatically captures erroneous attempts.
  - Direct retry mechanism to master previously failed problems.
- ⚡ **100% Client-Side & Offline-First**:
  - Powered by IndexedDB (Dexie.js). Zero runtime cloud dependencies.
  - Instant snappy transitions with zero loading spinners.

---

## 🛠️ Tech Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS
- **Math Rendering**: KaTeX (with specialized MathML suppression for duplicate-free rendering)
- **Local Storage**: Dexie.js (IndexedDB)
- **Icons**: Lucide React
- **Deployment**: Vercel (Auto-builds via Vite)

---

## 🚀 Getting Started

### Local Development

```bash
cd web
npm install
npm run dev
```

### Production Build

```bash
cd web
npm run build
npm run preview
```

---

## 📄 License

Proprietary — Developed for Bangladeshi Competitive Exam Aspirants.
