import json

with open("web/src/data/curriculum.json", encoding="utf-8") as f:
    ch = json.load(f)

for c in ch:
    print(f"{c['id']} | {c['title_bn']} | {c['category']}")
