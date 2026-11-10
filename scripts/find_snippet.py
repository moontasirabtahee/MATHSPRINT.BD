import json, os

target = "x - 5"

for root, dirs, files in os.walk('.'):
    if 'node_modules' in root or '.git' in root or 'dist' in root:
        continue
    for f in files:
        if f.endswith('.json'):
            p = os.path.join(root, f)
            try:
                with open(p, 'r', encoding='utf-8') as fl:
                    content = fl.read()
                    if '|x - 5|' in content or ('৩৯' in content and 'x - 5' in content):
                        print(f"Found in {p}")
            except Exception as e:
                pass
