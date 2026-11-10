import json

def inspect_rows():
    with open('output/final_json/textbook_master.json', encoding='utf-8') as f:
        data = json.load(f)
        
    for p in data['pages']:
        p_num = p.get('page_number')
        if 9 <= p_num <= 15:
            for b in p.get('blocks', []):
                if b.get('type') == 'table' and b.get('table_data'):
                    td = b['table_data']
                    print(f"\n=== Page {p_num} Headers: {td.get('headers')} ===")
                    for r in td.get('rows', []):
                        print(" | ".join(str(cell) for cell in r))

if __name__ == '__main__':
    inspect_rows()
