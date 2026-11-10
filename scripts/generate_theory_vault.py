import json
import time
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from google import genai
from google.genai import types

sys.stdout.reconfigure(line_buffering=True)

# Load API Keys
with open("config/keys.json", encoding="utf-8") as f:
    keys_data = json.load(f)

api_keys = [item["key"] for item in keys_data.get("api_keys", [])]
print(f"Loaded {len(api_keys)} API keys.", flush=True)

# Load Curriculum
with open("web/src/data/curriculum.json", encoding="utf-8") as f:
    topics = json.load(f)

print(f"Loaded {len(topics)} topics from curriculum.", flush=True)

def build_prompt(topic):
    title_bn = topic.get("title_bn", "")
    title_en = topic.get("title_en", "")
    category = topic.get("category", "")
    core_idea = topic.get("concept_summary", {}).get("core_idea", "")

    return f"""
তুমি বাংলাদেশের বিসিএস (BCS), ব্যাংক এবং সরকারি চাকরি পরীক্ষার শীর্ষস্থানীয় সিনিয়র গণিতবিদ ও শিক্ষক।

অধ্যায়: "{title_bn}" ({title_en})
শাখা: {category}
মৌলিক ধারণা: {core_idea[:150]}

এই অধ্যায়ের জন্য ৬ থেকে ৮টি অতি গুরুত্বপূর্ণ, প্রমাণ্য এবং প্রিমিয়াম গাণিতিক "থিওরি ও সূত্র কার্ড" প্রস্তুত করো।
কার্ডগুলোতে অবশ্যই নিম্নলিখিত চার ধরনের উপাদান থাকতে হবে:
1. "formula" — মূল প্রামাণ্য গাণিতিক সূত্রাবলি (LaTeX KaTeX ফরম্যাটে)
2. "concept" — মৌলিক তাত্ত্বিক ভিত্তি, সংজ্ঞা ও মূল নিয়ম
3. "shortcut" — বিসিএস ও ব্যাংকে দ্রুত ৩-১০ সেকেন্ডে সমাধানের শর্টকাট টেকনিক ও হ্যাক
4. "trap" — পরীক্ষার হলে শিক্ষার্থীরা সচরাচর যে ফাঁদে পড়ে বা যে ভুল করে

প্রতিটি আইটেমের জন্য নিচের JSON স্কিমা অনুসরণ করো:
[
  {{
    "title": "পরিচ্ছন্ন ও অর্থবহ বাংলা শিরোনাম (যেমন: কার্যকর শতকরা পরিবর্তন, বা ভাজক সংখ্যা নির্ণয়)",
    "concept_type": "formula" | "concept" | "shortcut" | "trap",
    "formula": "প্রামাণ্য গাণিতিক সমীকরণ বা সম্পর্কটি অবশ্যই সম্পূর্ণ বৈধ KaTeX LaTeX-এ ($$ বা $ সহকারে)",
    "explanation": "বিশদ ও প্রাঞ্জল বাংলা গাণিতিক ব্যাখ্যা ও যুক্তি",
    "rules": ["ব্যবহারিক নিয়ম বা ধাপ ১", "নিয়ম বা ধাপ ২"],
    "example": "একটি দ্রুত বাস্তব উদাহরণ (যদি প্রযোজ্য হয়)"
  }}
]

শুধুমাত্র বৈধ JSON অ্যারে প্রদান করো, কোনো ভূমিকা বা মার্কডাউন ব্যাকটিক কোডব্লক ছাড়া।
"""

def generate_for_topic(index, topic, key_index):
    api_key = api_keys[key_index % len(api_keys)]
    client = genai.Client(api_key=api_key)
    prompt = build_prompt(topic)

    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"[{index+1}/36 STARTING] {topic['title_bn']} with Key {key_index%len(api_keys)+1}...", flush=True)
            resp = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2
                )
            )
            raw = resp.text.strip()
            if raw.startswith("```json"):
                raw = raw[7:]
            if raw.startswith("```"):
                raw = raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()

            cards = json.loads(raw)
            formatted_cards = []
            for i, c in enumerate(cards):
                c_id = f"theory_{topic['id']}_{i+1:02d}"
                formatted_cards.append({
                    "id": c_id,
                    "topic_id": topic["id"],
                    "topic_name": topic["title_bn"],
                    "category": topic.get("category", "Arithmetic"),
                    "concept_type": c.get("concept_type", "concept"),
                    "title": c.get("title", f"{topic['title_bn']} তত্ত্ব {i+1}"),
                    "formula": c.get("formula", "$$E = mc^2$$"),
                    "explanation": c.get("explanation", ""),
                    "rules": c.get("rules", []),
                    "example": c.get("example", ""),
                    "is_memorized": False,
                    "is_bookmarked": False
                })
            print(f"[{index+1}/36 SUCCESS] {topic['title_bn']}: Generated {len(formatted_cards)} cards", flush=True)
            return (topic["id"], formatted_cards)
        except Exception as e:
            print(f"[{index+1}/36 RETRY {attempt+1}] {topic['title_bn']} Error: {e}", flush=True)
            time.sleep(2 * (attempt + 1))

    print(f"[{index+1}/36 FAILED] {topic['title_bn']}", flush=True)
    return (topic["id"], [])

def main():
    start_time = time.time()
    all_results = {}

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(generate_for_topic, i, topic, i % len(api_keys)): topic
            for i, topic in enumerate(topics)
        }

        for future in as_completed(futures):
            topic_id, cards = future.result()
            all_results[topic_id] = cards

    final_formula_list = []
    for topic in topics:
        tid = topic["id"]
        cards = all_results.get(tid, [])
        final_formula_list.extend(cards)

    print(f"\n==========================================", flush=True)
    print(f"Total Theory Cards Generated: {len(final_formula_list)}", flush=True)
    print(f"Time Taken: {time.time() - start_time:.2f} seconds", flush=True)
    print(f"==========================================", flush=True)

    out_path = "web/src/data/formulas.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(final_formula_list, f, ensure_ascii=False, indent=2)

    print(f"Saved to {out_path}", flush=True)

if __name__ == "__main__":
    main()
