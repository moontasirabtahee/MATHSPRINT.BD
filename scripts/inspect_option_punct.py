import json

for fname in ['web/src/data/questions.json', 'web/src/data/questions_core.json']:
    data = json.load(open(fname, encoding='utf-8'))
    count = 0
    for q in data:
        for i, opt in enumerate(q.get('options', [])):
            clean = opt.strip()
            if clean.startswith((',', '।', ':', ';', '.', '–', '-')):
                if count < 10:
                    print(f"{fname} | {q['id']} | opt[{i}]: {repr(opt)}")
                count += 1
    print(f"{fname}: Total options with leading punctuation = {count}")
