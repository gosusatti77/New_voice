import requests
from bs4 import BeautifulSoup
import re
import json

with open("form_url.txt", "r", encoding="utf-8") as f:
    form_url = f.read().strip()
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(form_url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

scripts = soup.find_all('script')
form_data_script = None

for script in scripts:
    if 'var FB_PUBLIC_LOAD_DATA_' in script.text:
        form_data_script = script.text
        break

if not form_data_script:
    print("❌ Could not find form data.")
    exit()

match = re.search(r'var FB_PUBLIC_LOAD_DATA_ = (.*?);\s*</script>', response.text, re.DOTALL)
if not match:
    print("❌ Failed to extract form JSON.")
    exit()

form_json_raw = match.group(1)
form_json = json.loads(form_json_raw)

questions = []

try:
    items = form_json[1][1]
    for item in items:
        question_text = item[1]
        entry_id = item[4][0][0]  # entry ID for the field
        if question_text and entry_id:
            questions.append({
                "question": question_text,
                "entry_id": entry_id
            })
except Exception as e:
    print("❌ Error parsing questions:", e)

# Save to questions.txt (clear first)
with open("questions.txt", "w", encoding="utf-8") as f:
    for i, q in enumerate(questions, 1):
        f.write(f"{i}. {q['question']}\n")

# Save to entry_ids.json
with open("entry_ids.json", "w", encoding="utf-8") as f:
    json.dump(questions, f, indent=4)

print("✅ Questions and entry IDs saved.")
