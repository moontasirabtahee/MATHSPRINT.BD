import json

with open('web/src/data/formulas.json', 'r', encoding='utf-8') as f:
    formulas = json.load(f)

for f in formulas:
    title = f.get('title', '')
    formula = f.get('formula', '')
    if 'ভাবতে পারেন' in title or 'ভাবতে পারেন' in formula:
        print(f"ID: {f.get('id')}")
        print(f"Title: {repr(title)}")
        print(f"Formula: {repr(formula)}")
