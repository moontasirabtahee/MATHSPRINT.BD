import re

sample_text = 'নিজে করুন:\\n৩৯. $|x - 5| = 4$ Ans: $x = 9, 1$'

def clean_question_stem(text):
    if not text:
        return ""
    t = text
    # Replace literal \n
    t = t.replace('\\n', ' ').replace('\n', ' ')
    
    # Strip prefixes
    t = re.sub(r'^(?:☐|➢|❖|►)?\s*(?:নিজে\s*করুন|অনুশীলন|উদাহরণ|নমুনা\s*প্রশ্ন)[\s\:\-]*', '', t, flags=re.IGNORECASE)
    # Strip leading question numbering like "৩৯. " or "39. " or "১) "
    t = re.sub(r'^[০-৯\d]+[\.\)]\s*', '', t)
    
    # Extract Ans/Answer if present
    ans_match = re.search(r'(?:উত্তর|Ans|Answer)\s*[:\.\-]?\s*(.*)$', t, re.IGNORECASE)
    ans = ""
    if ans_match:
        ans = ans_match.group(1).strip()
        t = t[:ans_match.start()].strip()
        
    return t.strip(), ans

stem, ans = clean_question_stem(sample_text)
print("Cleaned stem:", repr(stem))
print("Extracted ans:", repr(ans))

