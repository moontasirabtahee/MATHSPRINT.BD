import json
import os

with open('web/src/data/questions.json', encoding='utf-8') as f:
    all_q = json.load(f)

# Pick first 15 questions for each topic
by_topic = {}
for q in all_q:
    tid = q['topic_id']
    if tid not in by_topic:
        by_topic[tid] = []
    if len(by_topic[tid]) < 15:
        by_topic[tid].append(q)

core_q = []
for tid, qs in by_topic.items():
    core_q.extend(qs)

print(f"Generated core question bank with {len(core_q)} questions across {len(by_topic)} topics.")

with open('web/src/data/questions_core.json', 'w', encoding='utf-8') as f:
    json.dump(core_q, f, ensure_ascii=False, indent=2)

print("Saved web/src/data/questions_core.json!")

