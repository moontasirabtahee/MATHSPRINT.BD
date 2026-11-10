import json
import re
import os

symbols_to_strip = r'[☐➢❖►□■❑▲•\*\-]'

def clean_text(text):
    if not text:
        return ""
    t = text
    # Replace literal \n
    t = t.replace('\\n', '\n')
    # Remove author names and book title mentions
    t = re.sub(r"Khairul'?s\s+Basic\s+Math", "Mathematics Sprint", t, flags=re.IGNORECASE)
    t = re.sub(r"Khairul'?s", "", t, flags=re.IGNORECASE)
    t = re.sub(r"Md\.\s*Khairul\s*Alam", "", t, flags=re.IGNORECASE)
    t = re.sub(r"খাইরুল'?স?\s*(বেসিক\s*ম্যাথ)?", "", t, flags=re.IGNORECASE)
    t = re.sub(r"খাইরুল\s*আলম", "", t, flags=re.IGNORECASE)
    t = re.sub(r"Scanned\s+with\s+CamScanner", "", t, flags=re.IGNORECASE)
    t = re.sub(r"পৃষ্ঠা\s*[:\-\s]*\d+", "", t)
    t = re.sub(r"Page\s*[:\-\s]*\d+", "", t, flags=re.IGNORECASE)
    return t.strip()

CHAPTER_MAP = [
    {"id": "topic_01", "name_bn": "সংখ্যা ও সংখ্যা পদ্ধতি", "name_en": "Number Systems & Real Numbers", "start": 22, "end": 55, "category": "Arithmetic", "prereqs": []},
    {"id": "topic_02", "name_bn": "ঐকিক নিয়ম", "name_en": "Unitary Method", "start": 56, "end": 98, "category": "Arithmetic", "prereqs": ["topic_01"]},
    {"id": "topic_03", "name_bn": "ল.সা.গু ও গ.সা.গু", "name_en": "LCM and HCF", "start": 99, "end": 125, "category": "Arithmetic", "prereqs": ["topic_01"]},
    {"id": "topic_04", "name_bn": "ভগ্নাংশ ও দশমিক", "name_en": "Fractions & Decimals", "start": 126, "end": 166, "category": "Arithmetic", "prereqs": ["topic_01"]},
    {"id": "topic_05", "name_bn": "বর্গ ও বর্গমূল", "name_en": "Squares & Square Roots", "start": 167, "end": 177, "category": "Arithmetic", "prereqs": ["topic_01"]},
    {"id": "topic_06", "name_bn": "ট্রেন ও আপেক্ষিক গতি", "name_en": "Train Problems & Relative Speed", "start": 178, "end": 196, "category": "Arithmetic", "prereqs": ["topic_02"]},
    {"id": "topic_07", "name_bn": "সময়, দূরত্ব ও গতিবেগ", "name_en": "Time, Distance & Speed", "start": 197, "end": 216, "category": "Arithmetic", "prereqs": ["topic_02", "topic_06"]},
    {"id": "topic_08", "name_bn": "নৌকা ও স্রোতের বেগ", "name_en": "Boat & Stream", "start": 217, "end": 234, "category": "Arithmetic", "prereqs": ["topic_07"]},
    {"id": "topic_09", "name_bn": "নল ও চৌবাচ্চা", "name_en": "Pipes & Cisterns", "start": 235, "end": 255, "category": "Arithmetic", "prereqs": ["topic_02"]},
    {"id": "topic_10", "name_bn": "সময় ও কাজের হিসাব", "name_en": "Work & Time", "start": 256, "end": 265, "category": "Arithmetic", "prereqs": ["topic_02", "topic_09"]},
    {"id": "topic_11", "name_bn": "গড় ও সমষ্টি", "name_en": "Averages", "start": 266, "end": 291, "category": "Arithmetic", "prereqs": ["topic_01"]},
    {"id": "topic_12", "name_bn": "শতকরা হিসাব", "name_en": "Percentages", "start": 292, "end": 341, "category": "Arithmetic", "prereqs": ["topic_04"]},
    {"id": "topic_13", "name_bn": "লাভ ও ক্ষতি", "name_en": "Profit & Loss", "start": 342, "end": 395, "category": "Commercial Math", "prereqs": ["topic_12"]},
    {"id": "topic_14", "name_bn": "সরল ও যৌগিক মুনাফা", "name_en": "Simple & Compound Interest", "start": 396, "end": 445, "category": "Commercial Math", "prereqs": ["topic_12"]},
    {"id": "topic_15", "name_bn": "অনুপাত ও সমানুপাত", "name_en": "Ratio & Proportion", "start": 446, "end": 473, "category": "Arithmetic", "prereqs": ["topic_04"]},
    {"id": "topic_16", "name_bn": "এলিগেশন ও মিশ্রণ", "name_en": "Alligation & Mixture", "start": 474, "end": 499, "category": "Commercial Math", "prereqs": ["topic_15", "topic_12"]},
    {"id": "topic_17", "name_bn": "অংশীদারি কারবার", "name_en": "Partnership", "start": 500, "end": 507, "category": "Commercial Math", "prereqs": ["topic_15"]},
    {"id": "topic_18", "name_bn": "বয়স সংক্রান্ত সমস্যা", "name_en": "Age Problems", "start": 508, "end": 533, "category": "Arithmetic", "prereqs": ["topic_15"]},
    {"id": "topic_19", "name_bn": "বীজগাণিতিক সূত্র ও মান নির্ণয়", "name_en": "Algebraic Formulas & Identities", "start": 541, "end": 568, "category": "Algebra", "prereqs": ["topic_05"]},
    {"id": "topic_20", "name_bn": "উৎপাদকে বিশ্লেষণ", "name_en": "Factorization", "start": 569, "end": 587, "category": "Algebra", "prereqs": ["topic_19"]},
    {"id": "topic_21", "name_bn": "সূচক ও ঘাত", "name_en": "Exponents & Powers", "start": 588, "end": 606, "category": "Algebra", "prereqs": ["topic_19"]},
    {"id": "topic_22", "name_bn": "লগারিদম", "name_en": "Logarithms", "start": 607, "end": 614, "category": "Algebra", "prereqs": ["topic_21"]},
    {"id": "topic_23", "name_bn": "সমান্তর ও গুণোত্তর ধারা", "name_en": "Arithmetic & Geometric Progressions", "start": 615, "end": 639, "category": "Algebra", "prereqs": ["topic_19"]},
    {"id": "topic_24", "name_bn": "সরল সমীকরণ ও গঠন", "name_en": "Linear Equations", "start": 640, "end": 655, "category": "Algebra", "prereqs": ["topic_19"]},
    {"id": "topic_25", "name_bn": "বিন্যাস (Permutation)", "name_en": "Permutations", "start": 656, "end": 678, "category": "Higher Math", "prereqs": ["topic_01"]},
    {"id": "topic_26", "name_bn": "সমাবেশ (Combination)", "name_en": "Combinations", "start": 679, "end": 693, "category": "Higher Math", "prereqs": ["topic_25"]},
    {"id": "topic_27", "name_bn": "সম্ভাবনা তত্ত্ব (Probability)", "name_en": "Probability Theory", "start": 694, "end": 712, "category": "Higher Math", "prereqs": ["topic_26"]},
    {"id": "topic_28", "name_bn": "সেট ও ভেনচিত্র", "name_en": "Set & Venn Diagram", "start": 713, "end": 728, "category": "Higher Math", "prereqs": ["topic_01"]},
    {"id": "topic_29", "name_bn": "অসমতা (Inequality)", "name_en": "Inequalities", "start": 729, "end": 744, "category": "Algebra", "prereqs": ["topic_24"]},
    {"id": "topic_30", "name_bn": "রেখা, কোণ ও বহুভুজ", "name_en": "Lines, Angles & Polygons", "start": 749, "end": 757, "category": "Geometry", "prereqs": []},
    {"id": "topic_31", "name_bn": "ত্রিভুজ সংক্রান্ত জ্যামিতি", "name_en": "Triangles & Geometry", "start": 758, "end": 785, "category": "Geometry", "prereqs": ["topic_30"]},
    {"id": "topic_32", "name_bn": "চতুর্ভুজ ও বৃত্ত", "name_en": "Quadrilaterals & Circles", "start": 786, "end": 828, "category": "Geometry", "prereqs": ["topic_31"]},
    {"id": "topic_33", "name_bn": "ঘন জ্যামিতি ও ত্রিমাত্রিক বস্তু", "name_en": "Solid Geometry", "start": 829, "end": 839, "category": "Geometry", "prereqs": ["topic_32"]},
    {"id": "topic_34", "name_bn": "ত্রিকোণমিতি", "name_en": "Trigonometry", "start": 840, "end": 851, "category": "Geometry", "prereqs": ["topic_31"]},
    {"id": "topic_35", "name_bn": "পরিমিতি ও ক্ষেত্রফল", "name_en": "Mensuration", "start": 852, "end": 863, "category": "Geometry", "prereqs": ["topic_32"]},
    {"id": "topic_36", "name_bn": "বিসিএস ও ব্যাংক মডেল টেস্ট", "name_en": "Competitive Exam Master Sets", "start": 864, "end": 882, "category": "Exam Revision", "prereqs": ["topic_01", "topic_12", "topic_19", "topic_31"]}
]

def clean_question_stem(text):
    if not text:
        return "", ""
    t = clean_text(text)
    # Replace literal \n
    t = t.replace('\\n', ' ').replace('\n', ' ')
    
    # Strip any leading bullets or symbols repeatedly
    t = re.sub(r'^(?:' + symbols_to_strip + r'|\s)+', '', t)
    
    # Strip prefixes like "নিজে করুন:", "অনুশীলন:", etc.
    t = re.sub(r'^(?:নিজে\s*করুন|অনুশীলন|উদাহরণ|নমুনা\s*প্রশ্ন)[\s\:\-]*', '', t, flags=re.IGNORECASE)
    
    # Strip bullets again
    t = re.sub(r'^(?:' + symbols_to_strip + r'|\s)+', '', t)
    
    # Strip leading question numbering like "৩৯. " or "৮. " or "1) "
    t = re.sub(r'^[০-৯\d]+[\.\)]\s*', '', t)

    # Strip bullets again
    t = re.sub(r'^(?:' + symbols_to_strip + r'|\s)+', '', t)
    
    # Extract Ans/Answer if present
    ans = ""
    ans_match = re.search(r'(?:উত্তর|Ans|Answer)\s*[:\.\-]?\s*(.*)$', t, re.IGNORECASE)
    if ans_match:
        ans = ans_match.group(1).strip()
        t = t[:ans_match.start()].strip()
        
    return t.strip(), ans

def parse_mcq_content_robust(raw_text):
    # 1. Extract Citation in brackets
    citation = ""
    cite_match = re.search(r"\[(.*?)\]", raw_text)
    if cite_match:
        citation = cite_match.group(1).strip()
        text_without_cite = raw_text.replace(cite_match.group(0), " ").strip()
    else:
        text_without_cite = raw_text

    # Clean text
    clean_t = clean_text(text_without_cite).replace('\\n', ' ').replace('\n', ' ')
    clean_t = re.sub(r'^(?:' + symbols_to_strip + r'|\s)+', '', clean_t)
    clean_t = re.sub(r'^(?:নিজে\s*করুন|অনুশীলন|উদাহরণ|নমুনা\s*প্রশ্ন)[\s\:\-]*', '', clean_t, flags=re.IGNORECASE)
    clean_t = re.sub(r'^[০-৯\d]+[\.\)]\s*', '', clean_t).strip()

    # Look for option markers using lookahead so LaTeX \frac is NEVER truncated
    marker_regex = re.compile(r'(?:^|\s+)([কখগঘABCDabcd])[\.\)]\s+')
    markers = list(marker_regex.finditer(clean_t))

    options = []
    trailing_ans = ""

    if len(markers) >= 3:
        stem = clean_t[:markers[0].start()].strip()
        for i, m in enumerate(markers):
            label = m.group(1).strip()
            content_start = m.end()
            content_end = markers[i+1].start() if i + 1 < len(markers) else len(clean_t)
            opt_val = clean_t[content_start:content_end].strip()
            
            # Check if answer is in this option
            ans_m = re.search(r'(?:উত্তর|Ans|Answer)\s*[:\.\-]?\s*(.*)$', opt_val, re.IGNORECASE)
            if ans_m:
                trailing_ans = ans_m.group(1).strip()
                opt_val = opt_val[:ans_m.start()].strip()
            
            # Clean up opt_val: replace \fr with \frac if corrupted
            opt_val = re.sub(r'\\fr\b', r'\\frac', opt_val)
            options.append(f"{label}. {opt_val}")
    else:
        # Check if Ans exists
        ans_m = re.search(r'(?:উত্তর|Ans|Answer)\s*[:\.\-]?\s*(.*)$', clean_t, re.IGNORECASE)
        if ans_m:
            trailing_ans = ans_m.group(1).strip()
            stem = clean_t[:ans_m.start()].strip()
        else:
            stem = clean_t

    # Final stem cleanup
    stem = re.sub(r'^(?:' + symbols_to_strip + r'|\s)+', '', stem)
    stem = re.sub(r'^(?:নিজে\s*করুন|অনুশীলন|উদাহরণ)[\s\:\-]*', '', stem, flags=re.IGNORECASE)
    stem = re.sub(r'^[০-৯\d]+[\.\)]\s*', '', stem).strip()
    # Replace any rogue \fr
    stem = re.sub(r'\\fr\b', r'\\frac', stem)

    # Determine answer letter
    mapping = {'ক': 'A', 'খ': 'B', 'গ': 'C', 'ঘ': 'D', 'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D'}
    ans_norm = trailing_ans.lower().replace('.', '').strip()
    ans_letter = mapping.get(ans_norm[:1], 'A')

    return {
        "stem": stem,
        "citation": clean_text(citation),
        "options": options,
        "answer_raw": trailing_ans,
        "answer_letter": ans_letter,
        "has_real_options": len(options) >= 3
    }

def make_clean_formula_title(formula_text, default_title):
    # Take first line
    line = formula_text.split('\n')[0].strip()
    line = re.sub(r'^(?:Confusion clear|Note|নোট|মনে রাখুন)[\s\:\-]*', '', line, flags=re.IGNORECASE)
    # If title has unclosed math, balance it
    if line.count('$') % 2 != 0:
        last_d = line.rfind('$')
        line = line[:last_d] + line[last_d+1:]
    line = line.strip()
    if len(line) < 4:
        return f"{default_title} এর গুরুত্বপূর্ণ সূত্র"
    if len(line) > 75:
        line = line[:75].rsplit(' ', 1)[0]
        if line.count('$') % 2 != 0:
            line += '$'
    return line

def main():
    print("Loading master textbook JSON...")
    with open('output/final_json/textbook_master.json', encoding='utf-8') as f:
        master = json.load(f)

    pages = master['pages']
    page_by_num = {p['page_number']: p for p in pages}

    topics_data = []
    all_questions = []
    all_formulas = []
    formula_id_counter = 1

    for ch in CHAPTER_MAP:
        ch_id = ch["id"]
        ch_name_bn = ch["name_bn"]
        ch_name_en = ch["name_en"]
        start_p = ch["start"]
        end_p = ch["end"]
        
        ch_questions = []
        ch_concepts = []
        ch_formulas = []
        
        for p_num in range(start_p, end_p + 1):
            if p_num not in page_by_num:
                continue
            p = page_by_num[p_num]
            blocks = p.get('blocks', [])
            
            for i, b in enumerate(blocks):
                b_type = b.get('type')
                b_text = b.get('text', '')
                b_id = b.get('block_id', f"p{p_num}_b{i}")
                
                # Formula
                if b_type == 'math_block' or (b_type == 'callout_box' and ('सूत्र' in b_text or 'Formula' in b_text or '=' in b_text)):
                    clean_f = clean_text(b_text)
                    # auto-fix broken \fr
                    clean_f = re.sub(r'\\fr\b', r'\\frac', clean_f)
                    if len(clean_f) > 8:
                        f_entry = {
                            "id": f"formula_{formula_id_counter:03d}",
                            "topic_id": ch_id,
                            "topic_name": ch_name_bn,
                            "title": make_clean_formula_title(clean_f, ch_name_bn),
                            "formula": clean_f,
                            "src_hash": b_id
                        }
                        ch_formulas.append(f_entry)
                        all_formulas.append(f_entry)
                        formula_id_counter += 1

                # Concept
                if b_type in ['callout_box', 'paragraph'] and ('মনে রাখুন' in b_text or 'নিয়ম' in b_text or 'টিপস' in b_text or 'পদ্ধতি' in b_text):
                    clean_c = clean_text(b_text)
                    clean_c = re.sub(r'\\fr\b', r'\\frac', clean_c)
                    if len(clean_c) > 20 and len(clean_c) < 500:
                        ch_concepts.append({
                            "title": make_clean_formula_title(clean_c, ch_name_bn),
                            "content": clean_c,
                            "src_hash": b_id
                        })

                # Exercise item
                if b_type == 'exercise_item':
                    sol_text = ""
                    for next_idx in range(i + 1, min(i + 3, len(blocks))):
                        if blocks[next_idx].get('type') == 'solution_block':
                            sol_text = clean_text(blocks[next_idx].get('text', ''))
                            sol_text = re.sub(r'\\fr\b', r'\\frac', sol_text)
                            break
                    
                    parsed = parse_mcq_content_robust(b_text)
                    if not parsed["stem"] or len(parsed["stem"]) < 8:
                        continue

                    q_type = "mcq" if parsed["has_real_options"] else "written"
                    
                    steps = []
                    if sol_text:
                        lines = [l.strip() for l in sol_text.split('\n') if l.strip() and not l.lower().startswith('solution') and not l.startswith('সমাধান')]
                        if lines:
                            steps = lines
                        else:
                            steps = [sol_text]
                    elif parsed["answer_raw"]:
                        steps = [f"প্রদত্ত শর্তানুসারে হিসাব: {parsed['answer_raw']}"]
                    else:
                        steps = ["প্রদত্ত নিয়মানুযায়ী সরাসরি মান বসিয়ে হিসাব সম্পন্ন করুন।"]

                    final_options = parsed["options"]
                    if not final_options:
                        if parsed["answer_raw"]:
                            ans_val = parsed["answer_raw"]
                            final_options = [
                                f"ক. {ans_val}",
                                "খ. বিকল্প বিভ্রান্তিকর মান",
                                "গ. বিপরীতমুখী অনুপাত",
                                "ঘ. এদের কোনটিই নয়"
                            ]
                        else:
                            final_options = ["ক. অপশন ১", "খ. অপশন ২", "গ. অপশন ৩", "ঘ. অপশন ৪"]

                    q_id = f"q_{ch_id}_{len(ch_questions) + 1:03d}"
                    q_entry = {
                        "id": q_id,
                        "topic_id": ch_id,
                        "topic_name": ch_name_bn,
                        "type": q_type,
                        "has_real_options": parsed["has_real_options"],
                        "stem": parsed["stem"],
                        "citation": parsed["citation"] or "প্রতিযোগিতামূলক পরীক্ষা",
                        "options": final_options,
                        "correct_answer": parsed["answer_letter"],
                        "answer_raw": parsed["answer_raw"],
                        "solution": sol_text or f"সঠিক উত্তর: {parsed['answer_raw'] or 'বিকল্প A'}",
                        "steps": steps[:5],
                        "marks": 5 if q_type == "written" else 1,
                        "rubric": {
                            "formula_selection": 1,
                            "substitution": 1,
                            "calculation": 2,
                            "final_answer": 1
                        } if q_type == "written" else None,
                        "distractor_explanations": {
                            "A": "বিকল্প পদ্ধতি বা সাধারণ সমীকরণ প্রয়োগে নির্ণেয় মান।",
                            "B": "চিহ্ন পরিবর্তন বা ভুল সূত্র ব্যবহারের কারণে আসা বিভ্রান্তিকর মান।",
                            "C": "ভগ্নাংশের হর-লব বিপরীতক্রমে গুণ করলে এই ভুল উত্তর পাওয়া যায়।",
                            "D": "হিসাবের শেষ ধাপে একক বা মাত্রায় অসতর্কতার ফলে সৃষ্ট বিভ্রান্তিকর মান।"
                        },
                        "src_hash": b_id
                    }
                    ch_questions.append(q_entry)
                    all_questions.append(q_entry)
        
        # Priority for Diagnostic Question: First question that HAS REAL OPTIONS and a Citation
        real_mcqs = [q for q in ch_questions if q.get("has_real_options")]
        diagnostic_q = real_mcqs[0] if real_mcqs else (ch_questions[0] if ch_questions else None)
        worked_example = real_mcqs[1] if len(real_mcqs) > 1 else (ch_questions[1] if len(ch_questions) > 1 else diagnostic_q)
        
        primary_concept = ch_concepts[0]["content"] if ch_concepts else f"{ch_name_bn} অধ্যায়ের মৌলিক নিয়ম ও সূত্রাবলি।"
        
        topics_data.append({
            "id": ch_id,
            "title_bn": ch_name_bn,
            "title_en": ch_name_en,
            "category": ch["category"],
            "prerequisites": ch["prereqs"],
            "estimated_minutes": 25,
            "total_questions": len(ch_questions),
            "mcq_count": sum(1 for q in ch_questions if q["type"] == "mcq"),
            "written_count": sum(1 for q in ch_questions if q["type"] == "written"),
            "concept_summary": {
                "core_idea": primary_concept,
                "when_to_use": f"যখন প্রশ্নে {ch_name_bn} সম্পর্কিত গাণিতিক সম্পর্ক বা অনুপাত দেয়া থাকে।",
                "common_traps": "চিহ্ন পরিবর্তন (±), এককের রূপান্তর (যেমন কিমি/ঘণ্টা থেকে মিটার/সেকেন্ড), এবং শেষের ধাপে শর্ত যাচাই না করা।"
            },
            "diagnostic_question_id": diagnostic_q["id"] if diagnostic_q else None,
            "worked_example_id": worked_example["id"] if worked_example else None,
            "formula_ids": [f["id"] for f in ch_formulas]
        })

    os.makedirs('web/src/data', exist_ok=True)

    with open('web/src/data/curriculum.json', 'w', encoding='utf-8') as f:
        json.dump(topics_data, f, ensure_ascii=False, indent=2)

    with open('web/src/data/questions.json', 'w', encoding='utf-8') as f:
        json.dump(all_questions, f, ensure_ascii=False, indent=2)

    with open('web/src/data/formulas.json', 'w', encoding='utf-8') as f:
        json.dump(all_formulas, f, ensure_ascii=False, indent=2)

    print(f"Generated clean dataset: {len(topics_data)} topics, {len(all_questions)} questions, {len(all_formulas)} formulas.")

if __name__ == '__main__':
    main()
