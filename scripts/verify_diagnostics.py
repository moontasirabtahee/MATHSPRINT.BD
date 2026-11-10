import json

with open('web/src/data/curriculum.json', encoding='utf-8') as f:
    topics = json.load(f)
with open('web/src/data/questions.json', encoding='utf-8') as f:
    questions = {q['id']: q for q in json.load(f)}

flagged = 0
for t in topics:
    diag_id = t['diagnostic_question_id']
    q = questions.get(diag_id)
    if q:
        for bad in ['Ans:', 'উত্তর:', 'নিজে করুন', '\\n', '□', '➢']:
            if bad in q['stem']:
                print(f"FLAGGED [{t['id']}]: {q['stem'][:70]}")
                flagged += 1
                break
    else:
        print(f"MISSING DIAGNOSTIC: {t['id']}")
        flagged += 1

print(f"Total flagged diagnostic questions: {flagged}")

