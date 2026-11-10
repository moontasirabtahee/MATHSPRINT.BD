import re

symbols_to_strip = r'[☐➢❖►□■❑▲•\*\-]'

def clean_question_stem_v2(text):
    if not text:
        return "", ""
    t = text.replace('\\n', ' ').replace('\n', ' ')
    
    # Strip any leading bullets or symbols repeatedly
    t = re.sub(r'^(?:' + symbols_to_strip + r'|\s)+', '', t)
    
    # Strip prefixes like "নিজে করুন:", "অনুশীলন:", etc.
    t = re.sub(r'^(?:নিজে\s*করুন|অনুশীলন|উদাহরণ|নমুনা\s*প্রশ্ন)[\s\:\-]*', '', t, flags=re.IGNORECASE)
    
    # Strip bullets again in case they were after the prefix or before numbering
    t = re.sub(r'^(?:' + symbols_to_strip + r'|\s)+', '', t)
    
    # Strip leading question numbering like "৩৯. " or "৮. " or "1) "
    t = re.sub(r'^[০-৯\d]+[\.\)]\s*', '', t)

    # Strip bullets again
    t = re.sub(r'^(?:' + symbols_to_strip + r'|\s)+', '', t)
    
    # Extract Ans/Answer if present
    ans = ""
    ans_match = re.search(r'(?:উত্তর|Ans|Answer)\s*[:\.\-]?\s*(.*)$', t, re.IGNORECASE)
    if ans_match:
        ans = ans_match.group(1).strip()
        t = t[:ans_match.start()].strip()
        
    return t.strip(), ans

test1 = "□ নিজে করুন:"
test2 = "□ নিজে করুন: ৮. ৬০ টাকা কিলোগ্রাম দরের চায়ের সঙ্গে ৪০ টাকা কিলোগ্রাম দরের চা..."
print("Test 1:", repr(clean_question_stem_v2(test1)))
print("Test 2:", repr(clean_question_stem_v2(test2)))

