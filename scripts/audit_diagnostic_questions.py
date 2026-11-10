import json

curriculum = json.load(open('web/src/data/curriculum.json', encoding='utf-8'))
questions = {q['id']: q for q in json.load(open('web/src/data/questions.json', encoding='utf-8'))}

print("Auditing diagnostic questions for all 36 topics:")
for t in curriculum:
    qid = t.get('diagnostic_question_id')
    q = questions.get(qid)
    if not q:
        print(f"ERROR: {t['id']} ({t['title_bn']}) has missing question {qid}")
        continue
    opts = q.get('options', [])
    if len(opts) < 4:
        print(f"WARN: {t['id']} ({t['title_bn']}) {qid} only has {len(opts)} options: {q.get('stem')[:40]} | opts: {opts}")
