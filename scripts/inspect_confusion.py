import json

with open('output/final_json/textbook_master.json', encoding='utf-8') as f:
    master = json.load(f)

for p in master['pages']:
    for b in p.get('blocks', []):
        if 'Confusion clear' in b.get('text', ''):
            print(f"Page {p['page_number']}, block {b['block_id']}, type {b['type']}:")
            print(repr(b.get('text')))
            break

