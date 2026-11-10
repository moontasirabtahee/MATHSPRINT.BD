import json

with open('web/src/data/questions.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

for q in questions:
    if q.get('src_hash') == 'p758_b05' or 'p758' in q.get('src_hash', ''):
        print(f"ID: {q['id']}, Topic: {q['topic_id']} ({q['topic_name']})")
        print(f"  Stem: {repr(q['stem'])}")
        print(f"  Options: {q['options']}")
        print(f"  Ans: {q.get('correct_answer')}")
        print(f"  Sol: {repr(q.get('solution'))}")

