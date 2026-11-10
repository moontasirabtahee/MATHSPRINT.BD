import json
from google import genai

def test_keys():
    with open("config/keys.json", encoding="utf-8") as f:
        data = json.load(f)

    for item in data.get("api_keys", []):
        alias = item["alias"]
        key = item["key"]
        proj = item.get("project_name", "unknown")
        try:
            client = genai.Client(api_key=key)
            resp = client.models.generate_content(
                model="gemini-3.5-flash",
                contents="Hello, reply with 'OK'"
            )
            print(f"[SUCCESS] {alias} ({proj}): {resp.text.strip()}")
        except Exception as e:
            print(f"[FAILED] {alias} ({proj}): {e}")

if __name__ == "__main__":
    test_keys()
