import re

test_p129 = '৩. নিচের কোন ভগ্নাংশটি বৃহত্তম? [৩৯-তম বিসিএস- (বিশেষ)]\nক. $\\frac{৩}{৫}$ খ. $\\frac{৫}{৮}$ গ. $\\frac{৬}{১১}$ ঘ. $\\frac{৮}{১৪}$ উত্তর: খ'
test_p31 = 'কোনটি মূলদ সংখ্যা? [টেক্সটাইল ইঞ্জিনিয়ারিং কলেজের ইনস্ট্রাক্টর ২০১৮]\nক. $\\sqrt{11}$ খ. $\\frac{\\sqrt{7}}{\\sqrt{23}}$ গ. $\\sqrt{\\frac{27}{48}}$ ঘ. $\\frac{\\sqrt{27}}{\\sqrt{48}}$ উত্তর: ঘ'

def parse_options_robust(text):
    # Find all option markers: (label, start_pos, end_pos)
    marker_regex = re.compile(r'(?:^|\s+)([কখগঘABCDabcd])[\.\)]\s+')
    markers = list(marker_regex.finditer(text))
    
    if len(markers) >= 3:
        stem = text[:markers[0].start()].strip()
        options = []
        for i, m in enumerate(markers):
            label = m.group(1)
            content_start = m.end()
            content_end = markers[i+1].start() if i + 1 < len(markers) else len(text)
            opt_val = text[content_start:content_end].strip()
            # If Ans / উত্তর is inside the last option, strip it
            ans_match = re.search(r'(?:উত্তর|Ans|Answer)\s*[:\.\-]?\s*(.*)$', opt_val, re.IGNORECASE)
            ans = ""
            if ans_match:
                ans = ans_match.group(1).strip()
                opt_val = opt_val[:ans_match.start()].strip()
            options.append(f"{label}. {opt_val}")
        return stem, options
    return text, []

stem1, opts1 = parse_options_robust(test_p129)
print("Stem 1:", stem1)
print("Opts 1:", opts1)

stem2, opts2 = parse_options_robust(test_p31)
print("\nStem 2:", stem2)
print("Opts 2:", opts2)

