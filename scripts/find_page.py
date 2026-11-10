import os

for root, dirs, files in os.walk('output/checkpoints'):
    for f in files:
        if f.endswith('.json'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8') as fl:
                c = fl.read()
                if '|x - 5| = 4' in c:
                    print(f"Found in checkpoint: {p}")
                    # print snippet
                    idx = c.find('|x - 5| = 4')
                    print(c[max(0, idx-100):min(len(c), idx+100)])

