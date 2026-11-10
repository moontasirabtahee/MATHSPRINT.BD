import sqlite3

conn = sqlite3.connect('output/digitizer.db')
c = conn.cursor()

print("--- Query 1: পদ্ধতি-৮ ---")
c.execute("SELECT page_number, block_id, type, text, latex FROM page_blocks WHERE text LIKE '%পদ্ধতি-৮%' OR text LIKE '%ভগ্নাংশের ঐকিক%'")
for r in c.fetchall():
    print(f"Page {r[0]} | Block {r[1]} | Type: {r[2]}")
    print(f"Text:\n{r[3]}")
    print(f"LaTeX:\n{r[4]}")
    print("-" * 50)

print("\n--- Query 2: ৭৫^৩ or পল্লী সঞ্চয় ---")
c.execute("SELECT page_number, block_id, type, text, latex FROM page_blocks WHERE text LIKE '%পল্লী সঞ্চয়%' OR text LIKE '%৪৬০৮%'")
for r in c.fetchall():
    print(f"Page {r[0]} | Block {r[1]} | Type: {r[2]}")
    print(f"Text:\n{r[3]}")
    print(f"LaTeX:\n{r[4]}")
    print("-" * 50)

