import json
import time
from google import genai
from google.genai import types

def get_client(key):
    return genai.Client(api_key=key)

with open("config/keys.json", encoding="utf-8") as f:
    keys_data = json.load(f)

keys = [item["key"] for item in keys_data.get("api_keys", [])]
print(f"Loaded {len(keys)} API keys.")

client = get_client(keys[0])

prompt = """
তুমি বাংলাদেশের বিসিএস (BCS), ব্যাংক ও সরকারি নিয়োগ পরীক্ষার গণিত বিশেষজ্ঞ শিক্ষক ও পাঠ্যক্রম প্রণেতা।

অধ্যায়: "লাভ ও ক্ষতি" (Profit and Loss)
ক্যাটাগরি: Commercial Math

এই অধ্যায়ের জন্য ৬টি অত্যন্ত গুরুত্বপূর্ণ ও খাঁটি গাণিতিক থিওরি কার্ড তৈরি করো। কার্ডগুলোতে নিচের বিষয়গুলো অবশ্যই থাকবে:
1. মূল সূত্রাবলি (Core Formulas - যেমন ক্রয়মূল্য, বিক্রয়মূল্য, লাভ-ক্ষতির হার, ধার্যমূল্য ও কমিশন)
2. শর্টকাট টেকনিক (যেমন: দুটি পণ্যের বিক্রয়মূল্য সমান এবং একটিতে x% লাভ ও অন্যটিতে x% ক্ষতি হলে সার্বিক ক্ষতি)
3. মৌলিক তত্ত্ব ও নিয়ম (ক্রয়মূল্যকে সর্বদা ১০০% ধরার মূল ভিত্তি)
4. পরীক্ষার সতর্কতামূলক ফাঁদ (ক্রয়মূল্যের বদলে বিক্রয়মূল্যের ওপর লাভ হিসেব করার বিভ্রান্তি)

প্রতিটি কার্ডের জন্য নিচের JSON স্কিমা অনুসরণ করো:
[
  {
    "title": "কার্ডের বাংলা শিরোনাম",
    "concept_type": "formula" | "concept" | "shortcut" | "trap",
    "formula": "মূল গাণিতিক সূত্র বা সম্পর্কটি অবশ্যই বৈধ KaTeX LaTeX-এ ($$ বা $ দিয়ে ঘেরা)",
    "explanation": "বিশদ, সুস্পষ্ট ও প্রাঞ্জল বাংলা গাণিতিক ব্যাখ্যা ও যুক্তি",
    "rules": ["নিয়ম বা ধাপ ১", "নিয়ম বা ধাপ ২"],
    "example": "একটি দ্রুত বাস্তব গাণিতিক উদাহরণ"
  }
]

শুধুমাত্র বৈধ JSON অ্যারে প্রদান করো, অন্য কোনো ভূমিকা বা ব্যাকটিক কোডব্লক ছাড়া।
"""

resp = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0.2
    )
)

print("Response preview:")
print(resp.text[:500])
try:
    parsed = json.loads(resp.text)
    print(f"Successfully parsed {len(parsed)} items!")
    print(json.dumps(parsed[0], ensure_ascii=False, indent=2))
except Exception as e:
    print("Failed to parse JSON:", e)
