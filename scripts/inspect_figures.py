import json

with open('output/final_json/textbook_master.json', encoding='utf-8') as f:
    master = json.load(f)

count = 0
for p in master['pages']:
    for b in p.get('blocks', []):
        if b.get('type') == 'figure':
            print(f"Page {p['page_number']}, figure block: {b['block_id']}")
            print(json.dumps(b, ensure_ascii=False))
            count += 1
            if count >= 3:
                break
    if count >= 3:
        break

