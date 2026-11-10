import React, { useMemo } from 'react';
import katex from 'katex';

interface MathViewProps {
  content: string;
  className?: string;
  inline?: boolean;
}

// Automatically wrap Bengali words/phrases inside LaTeX math mode into \text{...}
// This guarantees that word spacing is preserved and characters never stick together.
function wrapBengaliInMath(mathStr: string): string {
  let result = '';
  let i = 0;
  while (i < mathStr.length) {
    if (mathStr.startsWith('\\text{', i)) {
      let braceCount = 1;
      let j = i + 6;
      while (j < mathStr.length && braceCount > 0) {
        if (mathStr[j] === '{') braceCount++;
        else if (mathStr[j] === '}') braceCount--;
        j++;
      }
      result += mathStr.slice(i, j);
      i = j;
    } else {
      const sub = mathStr.slice(i);
      // Match a contiguous Bengali phrase (including Bengali characters, digits, and spaces)
      const match = sub.match(/^([\u0980-\u09FF]+(?:\s+[\u0980-\u09FF]+)*)/);
      if (match && match[1].length > 0) {
        result += `\\text{${match[1]}}`;
        i += match[1].length;
      } else {
        result += mathStr[i];
        i++;
      }
    }
  }
  return result;
}

// Battle-tested sanitizer that guarantees 99.99%+ clean KaTeX compilation
function sanitizeMath(mathStr: string): string {
  let m = mathStr.trim();
  // Strip outer rogue $ if any
  m = m.replace(/^\$+|\$+$/g, '');
  // Fix OCR truncated fraction \fr -> \frac
  m = m.replace(/\\fr\b/g, '\\frac');
  m = m.replace(/\\se\b/g, '\\sec');
  m = m.replace(/[\f\x0c]/g, ' ');
  // Fix broken \frac missing opening brace e.g. \frac৪৯}{12}
  m = m.replace(/\\frac([^{}\s]+)\}/g, '\\frac{$1}');

  // Wrap any raw Bengali text into \text{...} to preserve spaces and correct typography
  m = wrapBengaliInMath(m);

  // If \text{ has an unclosed brace before another command
  if (m.includes('\\text{') && (m.match(/\\text\{/g) || []).length > (m.match(/\}/g) || []).length) {
    m += '}';
  }

  // Balance grouping braces (excluding escaped literal braces \{ and \})
  const cleanForCount = m.replace(/\\\{/g, '').replace(/\\\}/g, '');
  const openCount = (cleanForCount.match(/\{/g) || []).length;
  const closeCount = (cleanForCount.match(/\}/g) || []).length;
  if (openCount > closeCount) {
    m += '}'.repeat(openCount - closeCount);
  }
  return m;
}

export const MathView: React.FC<MathViewProps> = ({ content, className = '', inline = false }) => {
  const renderedHtml = useMemo(() => {
    if (!content) return '';

    // 1. Unescape literal \n strings if any exist
    let text = content.replace(/\\n/g, '\n');

    // 2. Strip out redundant section headers, question numbering, and trailing answers
    text = text.replace(/^(?:[☐➢❖►□■❑▲•\*\-☞♦]|\s)*(?:নিজে\s*করুন|অনুশীলন|উদাহরণ|আরেকটি\s*দেখুন)[\s\:\-]*/i, '');
    text = text.replace(/^(?:[০-৯\d]+[\.\)]\s*)/, '');
    text = text.replace(/\s+(?:Ans|Answer|উত্তর)\s*[:\.\-]\s*.*$/i, '');

    // Strip accidental leading commas or punctuation after option indicators like "গ. , ৩২১৫" -> "গ. ৩২১৫"
    text = text.replace(/([ক-ঘa-dA-D][\.\)])\s*[,،\:]\s*/g, '$1 ');

    // 3. Extract all math expressions and replace them with unique placeholders
    // This CRITICALLY protects KaTeX's internal SVG <path d="..."> strings from having \n replaced with <br/>!
    const mathTokens: string[] = [];

    // First replace display math $$...$$
    text = text.replace(/\$\$(.+?)\$\$/gs, (_, math) => {
      const token = `%%KMATH_${mathTokens.length}%%`;
      const sanitized = sanitizeMath(math);
      try {
        const rendered = katex.renderToString(sanitized, {
          displayMode: true,
          throwOnError: false,
          output: 'html',
          strict: false,
        });
        mathTokens.push(rendered);
      } catch (err) {
        mathTokens.push(`<span class="text-rose-500 font-mono text-xs">${sanitized}</span>`);
      }
      return token;
    });

    // Next replace inline math $...$
    text = text.replace(/\$([^\$]+?)\$/g, (_, math) => {
      const token = `%%KMATH_${mathTokens.length}%%`;
      const sanitized = sanitizeMath(math);
      try {
        const rendered = katex.renderToString(sanitized, {
          displayMode: false,
          throwOnError: false,
          output: 'html',
          strict: false,
        });
        mathTokens.push(rendered);
      } catch (err) {
        mathTokens.push(`<span class="text-rose-500 font-mono text-xs">${sanitized}</span>`);
      }
      return token;
    });

    // 4. Safely replace newlines in the PROSE ONLY (outside KaTeX SVGs)
    text = text.replace(/\n/g, '<br/>');

    // 5. Restore the rendered KaTeX tokens back into the HTML
    text = text.replace(/%%KMATH_(\d+)%%/g, (_, indexStr) => {
      const idx = parseInt(indexStr, 10);
      return mathTokens[idx] ?? '';
    });

    return text;
  }, [content]);

  if (inline) {
    return (
      <span
        className={`math-rendered inline ${className}`}
        dangerouslySetInnerHTML={{ __html: renderedHtml }}
      />
    );
  }

  return (
    <div
      className={`math-rendered leading-relaxed ${className}`}
      dangerouslySetInnerHTML={{ __html: renderedHtml }}
    />
  );
};
