import requests
import json

# Load form URL from file
with open("form_url.txt", "r", encoding="utf-8") as f:
    form_url_raw = f.read().strip()

# Convert view URL to formResponse URL
if "viewform" in form_url_raw:
    form_url = form_url_raw.replace("viewform", "formResponse")
else:
    print("❌ Invalid Google Form URL format.")
    exit()

# Load entry IDs
with open("entry_ids.json", "r", encoding="utf-8") as f:
    entry_data = json.load(f)

# Load answers
with open("answers.txt", "r", encoding="utf-8") as f:
    answers = [line.strip() for line in f if line.strip()]

# Build form data
form_data = {}
for i, item in enumerate(entry_data):
    if i < len(answers):
        entry_id = f"entry.{item['entry_id']}"
        form_data[entry_id] = answers[i]

# Submit form
response = requests.post(form_url, data=form_data)

# Status
if response.status_code == 200:
    print("Form submitted successfully!")
else:
    print("Form submission failed.")
    print("Status code:", response.status_code)
    print(response.text)
