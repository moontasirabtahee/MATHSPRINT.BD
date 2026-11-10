import json
import re
from google import genai

keys = json.load(open('config/keys.json', encoding='utf-8'))['api_keys']
client = genai.Client(api_key=keys[0]['key'])

prompt = """তুমি বাংলাদেশের বিসিএস প্রিলিমিনারি ও ব্যাংক নিয়োগ গণিত পরীক্ষার জন্য শীর্ষস্থানীয় গণিতবিদ ও শিক্ষক।
টপিক: 'সংখ্যা ও সংখ্যা পদ্ধতি' (topic_01, Arithmetic)

নিচের ৪টি ক্যাটাগরির জন্য ৪টি সুনির্দিষ্ট কার্ড তৈরি করো:
1. formula (মূল সূত্র): ভাজক সংখ্যা ও বিজোড় ভাজক নির্ণয়ের সঠিক KaTeX সূত্র
2. shortcut (শর্টকাট হ্যাক): বিভাজ্যতা যাচাই বা দ্রুত মৌলিক সংখ্যা চেনার বাস্তব টেকনিক
3. concept (মৌলিক তত্ত্ব): মূলদ বনাম অমূলদ সংখ্যার নিখুঁত বৈশিষ্ট্য ও উদাহরণ
4. trap (পরীক্ষার ফাঁদ): xy জোড় হলে xy/2 এর বিভ্রান্তি অথবা ক্ষুদ্রতম মৌলিক সংখ্যা সংক্রান্ত ভুল

কঠোর নির্দেশাবলি:
- কোনো গতানুগতিক ফাঁকা বুলি (যেমন: "Standard Relation for...", "প্রদত্ত উপাত্তের একক একই পদ্ধতিতে রূপান্তর করে নিন") লিখবে না।
- প্রতিটি কার্ডে বাস্তব, সুনির্দিষ্ট গণিত ও উদাহরণ থাকতে হবে।
- সূত্র KaTeX সামঞ্জস্যপূর্ণ হতে হবে ($ দিয়ে ঘেরার দরকার নেই, শুধু KaTeX সিনট্যাক্স যেমন \\frac{a}{b})।
- শুধুমাত্র একটি শুদ্ধ JSON array রিটার্ন করো:
[
  {
    "id": "f_topic_01_01",
    "topic_id": "topic_01",
    "topic_name": "সংখ্যা ও সংখ্যা পদ্ধতি",
    "category": "Arithmetic",
    "concept_type": "formula",
    "title": "মোট ভাজক সংখ্যা ও বিজোড় ভাজক নির্ণয়",
    "formula": "N = 2^p \\cdot a^q \\cdot b^r \\implies \\text{মোট ভাজক} = (p+1)(q+1)(r+1)",
    "explanation": "যেকোনো সংখ্যা N কে মৌলিক উৎপাদকে বিশ্লেষণ করার পর ঘাতগুলোর সাথে ১ যোগ করে গুণ করলে মোট ভাজক সংখ্যা পাওয়া যায়।",
    "rules": [
      "প্রথমে সংখ্যাটিকে মৌলিক সংখ্যাসমূহের গুণফল আকারে প্রকাশ করুন।",
      "বিজোড় ভাজক সংখ্যার ক্ষেত্রে 2 এর ঘাত (p) সম্পূর্ণ বাদ দিয়ে (q+1)(r+1) হিসাব করতে হয়।"
    ],
    "example": "৭২ = 2^3 \\times 3^2 হলে মোট ভাজক = (3+1)(2+1) = 12 টি এবং বিজোড় ভাজক = (2+1) = 3 টি।"
  }
]
"""

resp = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=prompt
)

def robust_json_decode(s: str):
    s = s.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*", "", s)
        s = re.sub(r"\s*```$", "", s)
    # Fix unescaped backslashes in JSON (common with LaTeX)
    cleaned = re.sub(r'\\(?![/"\\bfnrtu])', r'\\\\', s)
    return json.loads(cleaned)

data = robust_json_decode(resp.text)
print(f"Successfully generated {len(data)} cards:")
for c in data:
    print(f"- [{c['concept_type']}] {c['title']} | Formula: {c['formula'][:40]}...")

