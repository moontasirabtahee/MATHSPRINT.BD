const katex = require('katex');

function sanitizeMath(mathStr) {
  let m = mathStr.trim();
  // Strip outer or rogue $
  m = m.replace(/\$/g, '');
  // Fix OCR truncated fraction \fr -> \frac
  m = m.replace(/\\fr\b/g, '\\frac');
  m = m.replace(/\\se\b/g, '\\sec');
  m = m.replace(/[\f\x0c]/g, ' ');
  // Fix broken \frac missing opening brace e.g. \frac৪৯}{12}
  m = m.replace(/\\frac([^{}\s]+)\}/g, '\\frac{$1}');

  // Fix unescaped grouping braces only (exclude \{ and \})
  const cleanForCount = m.replace(/\\\{/g, '').replace(/\\\}/g, '');
  const openCount = (cleanForCount.match(/\{/g) || []).length;
  const closeCount = (cleanForCount.match(/\}/g) || []).length;
  if (openCount > closeCount) {
    m += '}'.repeat(openCount - closeCount);
  }
  return m;
}

const allQuestions = require('./src/data/questions.json');
let failed = 0;
let total = 0;

allQuestions.forEach(q => {
  const text = (q.stem || '') + ' ' + (q.solution || '') + ' ' + (q.options || []).join(' ');
  const matches = text.match(/\$(.+?)\$/g);
  if (matches) {
    matches.forEach(m => {
      total++;
      const s = sanitizeMath(m.slice(1, -1));
      try {
        katex.renderToString(s, { output: 'html', strict: false, throwOnError: true });
      } catch (e) {
        failed++;
        if (failed <= 5) console.log('Failed:', m.slice(1, -1), '-->', e.message);
      }
    });
  }
});

console.log(`Tested ${total} snippets. Failed: ${failed} (${((failed/total)*100).toFixed(2)}%)`);
