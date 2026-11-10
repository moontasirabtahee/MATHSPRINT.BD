import json
import re

def analyze():
    with open('output/final_json/textbook_master.json', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Total pages: {len(data['pages'])}")
    
    # Check page 25
    for p in data['pages']:
        if p.get('page_number') == 25:
            print("--- PAGE 25 BLOCKS ---")
            for b in p.get('blocks', []):
                txt = b.get('text', '').replace('\n', ' ')
                print(f"[{b.get('type')}] (Order: {b.get('reading_order')}): {txt[:90]}")
            break

    # Look at some exercise items and see how options/answers are formatted
    mcq_count = 0
    written_count = 0
    sample_mcqs = []
    
    for p in data['pages']:
        for b in p.get('blocks', []):
            if b.get('type') == 'exercise_item':
                txt = b.get('text', '')
                if any(opt in txt for opt in ['Ans:', 'উত্তর', 'Ans.', 'Ans :']):
                    mcq_count += 1
                    if len(sample_mcqs) < 3:
                        sample_mcqs.append(txt)
                else:
                    written_count += 1
                    
    print(f"\nMCQ questions found: {mcq_count}")
    print(f"Written/Problem items: {written_count}")
    print("\nSample MCQs:")
    for i, sm in enumerate(sample_mcqs, 1):
        print(f"\n--- Sample {i} ---")
        print(sm)

if __name__ == '__main__':
    analyze()

