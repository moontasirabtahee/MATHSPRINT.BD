import json
import re

def map_curriculum():
    with open('output/final_json/textbook_master.json', encoding='utf-8') as f:
        data = json.load(f)

    # Let's track chapters by heading_1 and heading_2
    modules = []
    current_module = None
    
    # Common mathematical topics to identify
    key_topics = [
        ("সংখ্যা ও সংখ্যা পদ্ধতি", ["সংখ্যা", "মৌলিক সংখ্যা", "বাস্তব সংখ্যা", "Number", "Digit"]),
        ("ঐকিক নিয়ম", ["ঐকিক", "Unitary"]),
        ("ল.সা.গু ও গ.সা.গু", ["ল.সা.গু", "গ.সা.গু", "L.C.M", "H.C.F"]),
        ("ভগ্নাংশ ও দশমিক", ["ভগ্নাংশ", "দশমিক", "Fraction", "Decimal"]),
        ("বর্গ ও বর্গমূল", ["বর্গ", "বর্গমূল", "Square", "Square root"]),
        ("গড় (Average)", ["গড়", "Average"]),
        ("শতকরা (Percentage)", ["শতকরা", "Percentage"]),
        ("লাভ ও ক্ষতি", ["লাভ-ক্ষতি", "লাভ ও ক্ষতি", "Profit & Loss"]),
        ("সুদকষা ও মুনাফা", ["মুনাফা", "সুদ", "Interest", "Simple Interest"]),
        ("অনুপাত ও সমানুপাত", ["অনুপাত", "সমানুপাত", "Ratio"]),
        ("মিশ্রণ ও এলিগেশন", ["মিশ্রণ", "এলিগেশন", "Mixture", "Allegation"]),
        ("অংশীদারি কারবার", ["অংশীদারি", "Partnership"]),
        ("বয়স সংক্রান্ত সমস্যা", ["বয়স", "Age"]),
        ("সময় ও কাজ", ["কাজ", "দিন", "Time & Work"]),
        ("নল ও চৌবাচ্চা", ["নল", "চৌবাচ্চা", "Pipe", "Cistern"]),
        ("গতিবেগ, দূরত্ব ও ট্রেন", ["গতিবেগ", "দূরত্ব", "ট্রেন", "Speed", "Distance", "Train"]),
        ("নৌকা ও স্রোত", ["নৌকা", "স্রোত", "Boat", "Stream"]),
        ("বীজগাণিতিক সূত্র ও মান নির্ণয়", ["বীজগণিত", "মান নির্ণয়", "Algebra", "Formula"]),
        ("উৎপাদকে বিশ্লেষণ", ["উৎপাদক", "Factorization"]),
        ("সূচক (Exponents)", ["সূচক", "Exponent"]),
        ("লগারিদম (Logarithm)", ["লগারিদম", "Logarithm", "Log"]),
        ("সমান্তর ও গুণোত্তর ধারা", ["ধারা", "সমান্তর", "গুণোত্তর", "Series"]),
        ("সেট ও ভেনচিত্র", ["সেট", "ভেনচিত্র", "Set"]),
        ("বিন্যাস ও সমাবেশ", ["বিন্যাস", "সমাবেশ", "Permutation", "Combination"]),
        ("সম্ভাবনা (Probability)", ["সম্ভাবনা", "Probability"]),
        ("জ্যামিতি ও কোণ", ["জ্যামিতি", "ত্রিভুজ", "চতুর্ভুজ", "বৃত্ত", "Geometry"]),
        ("পরিমিতি ও ক্ষেত্রফল", ["পরিমিতি", "ক্ষেত্রফল", "আয়তন", "Mensuration"])
    ]
    
    pages = data['pages']
    topic_ranges = []
    
    for p in pages:
        p_num = p.get('page_number')
        # check headings
        for b in p.get('blocks', []):
            if b.get('type') in ['heading_1', 'heading_2']:
                txt = b.get('text', '').strip()
                for t_name, keywords in key_topics:
                    if any(kw.lower() in txt.lower() for kw in keywords):
                        # Avoid adding repetitive adjacent same topics
                        if not topic_ranges or topic_ranges[-1]['name'] != t_name:
                            topic_ranges.append({'page': p_num, 'name': t_name, 'raw': txt[:50]})
                        break
                        
    print(f"Detected topic transitions: {len(topic_ranges)}")
    for tr in topic_ranges[:30]:
        print(f"Page {tr['page']}: {tr['name']} (Raw: {tr['raw']})")

if __name__ == '__main__':
    map_curriculum()

