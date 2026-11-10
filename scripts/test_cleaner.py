import json
import re

def robust_json_decode(s: str):
    s = s.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*", "", s)
        s = re.sub(r"\s*```$", "", s)
    # Fix single backslashes that are not valid JSON escapes (\", \\, \/, \b, \f, \n, \r, \t, \uXXXX)
    # Replace single backslash with double backslash if followed by a LaTeX command or char
    cleaned = re.sub(r'\\(?![/"\\bfnrtu])', r'\\\\', s)
    return json.loads(cleaned)

with open("scripts/test_gemini_topic.py", "r", encoding="utf-8") as f:
    text = f.read()

# Let's inspect how to parse resp.text

