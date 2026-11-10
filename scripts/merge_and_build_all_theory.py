import json
import re

import sys
import os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("scripts"))

# Load curriculum
with open("web/src/data/curriculum.json", encoding="utf-8") as f:
    curriculum = json.load(f)

topic_map = {t["id"]: t for t in curriculum}

# Import batch 1 from build_complete_theory_vault
from build_complete_theory_vault import THEORY_DATA as TOPIC_THEORY_BATCH_1

# Import batch 2 from complete_curriculum_vault
from complete_curriculum_vault import MODULES as TOPIC_THEORY_BATCH_2

all_topics_data = {}
all_topics_data.update(TOPIC_THEORY_BATCH_1)
all_topics_data.update(TOPIC_THEORY_BATCH_2)

print(f"Total topics covered in master registry: {len(all_topics_data)}")

final_formulas = []
formula_id_counter = 1

for t in curriculum:
    topic_id = t["id"]
    topic_name = t["title_bn"]
    category = t.get("category", "General")
    
    cards = all_topics_data.get(topic_id, [])
    if not cards:
        print(f"WARNING: Topic {topic_id} ({topic_name}) has no curated cards!")
        continue

    for card in cards:
        card_id = f"f_{topic_id}_{formula_id_counter:03d}"
        formula_id_counter += 1
        
        # Clean title
        title = card.get("title", "").strip()
        # Clean formula
        raw_formula = card.get("formula", "").strip()
        
        # Build clean formula item
        item = {
            "id": card_id,
            "topic_id": topic_id,
            "topic_name": topic_name,
            "category": category,
            "title": title,
            "formula": raw_formula,
            "concept_type": card.get("concept_type", "formula"),
            "explanation": card.get("explanation", "").strip(),
            "rules": card.get("rules", []),
            "example": card.get("example", "").strip(),
            "is_memorized": False,
            "is_bookmarked": False
        }
        final_formulas.append(item)

print(f"Total authentic cards prepared across all 36 topics: {len(final_formulas)}")

# Validate zero boilerplate strings
boilerplate_patterns = [
    r"Standard Relation for",
    r"Fast Solving Rule for",
    r"Common Pitfalls in",
    r"Core Principles of",
    r"প্রদত্ত উপাত্তের একক একই পদ্ধতিতে রূপান্তর করে নিন",
    r"বিকল্পগুলোর মান বসিয়ে উভয় পাশ দ্রুত সিদ্ধ করে সঠিক অপশন চেনা যায়",
    r"ঐতিহ্যবাহী বিস্তারিত পদ্ধতির বাইরে গিয়ে ৩ থেকে ৫ সেকেন্ডে",
]

boilerplate_found = 0
for f in final_formulas:
    text_blob = json.dumps(f, ensure_ascii=False)
    for bp in boilerplate_patterns:
        if re.search(bp, text_blob):
            print(f"ERROR: Boilerplate '{bp}' found in {f['id']} ({f['topic_name']})")
            boilerplate_found += 1

if boilerplate_found == 0:
    print("SUCCESS: 100% zero placeholder boilerplate detected across all cards!")
else:
    raise RuntimeError(f"Found {boilerplate_found} boilerplate strings!")

# Write to web/src/data/formulas.json
with open("web/src/data/formulas.json", "w", encoding="utf-8") as fp:
    json.dump(final_formulas, fp, ensure_ascii=False, indent=2)

print(f"Written {len(final_formulas)} cards into web/src/data/formulas.json successfully!")
