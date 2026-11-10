import os

def search_text():
    for root, dirs, files in os.walk('.'):
        if any(x in root for x in ['node_modules', '.git', 'dist', '.vscode']):
            continue
        for f in files:
            p = os.path.join(root, f)
            try:
                with open(p, 'r', encoding='utf-8', errors='ignore') as fl:
                    content = fl.read()
                    if 'x - 5' in content and '39' in content:
                        print(f"Match 1 in {p}")
                    if '৩৯' in content and 'x - 5' in content:
                        print(f"Match 2 in {p}")
                    if '|x - 5|' in content:
                        print(f"Match 3 in {p}")
            except Exception as e:
                pass

search_text()

