import json
import re
import subprocess

def test_all_math():
    with open('web/src/data/questions.json', encoding='utf-8') as f:
        questions = json.load(f)

    with open('web/src/data/formulas.json', encoding='utf-8') as f:
        formulas = json.load(f)

    all_math_snippets = []
    
    for q in questions:
        # find all $...$ and $$...$$
        st = q.get('stem', '') + ' ' + q.get('solution', '') + ' ' + ' '.join(q.get('options', []))
        matches = re.findall(r'\$(.+?)\$', st)
        for m in matches:
            all_math_snippets.append(m)

    for f in formulas:
        form = f.get('formula', '')
        matches = re.findall(r'\$(.+?)\$', form)
        if matches:
            all_math_snippets.extend(matches)
        else:
            all_math_snippets.append(form)

    print(f"Total extracted math snippets to test: {len(all_math_snippets)}")
    
    # Save a sample to test with node katex
    with open('web/math_samples.json', 'w', encoding='utf-8') as f:
        json.dump(all_math_snippets[:500], f, ensure_ascii=False)

    print("Saved web/math_samples.json")

if __name__ == '__main__':
    test_all_math()

