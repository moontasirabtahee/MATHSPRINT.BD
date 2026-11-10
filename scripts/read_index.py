import json

def read_index():
    with open('output/final_json/textbook_master.json', encoding='utf-8') as f:
        data = json.load(f)
        
    for p in data['pages']:
        p_num = p.get('page_number')
        if 9 <= p_num <= 15:
            print(f"=== PAGE {p_num} ===")
            for b in p.get('blocks', []):
                t = b.get('type')
                txt = b.get('text', '')
                if t in ['heading_1', 'heading_2', 'paragraph', 'table', 'callout_box']:
                    print(f"[{t}]: {txt.strip()}")

if __name__ == '__main__':
    read_index()

