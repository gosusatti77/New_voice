import streamlit as st
import subprocess
import time
import os
import json

st.set_page_config(page_title="Voice Assistant for Google Forms", layout="centered")
st.title("🎤 Voice Assistant for Google Form")

form_url = st.text_input("Paste your Google Form URL here:")

if st.button("Run Assistant"):
    if not form_url:
        st.warning("Please enter a valid URL!")
    else:
        with open("form_url.txt", "w", encoding="utf-8") as f:
            f.write(form_url)

        st.info("🔍 Scraping questions and entry IDs from form...")
        result = subprocess.run(["python", "New_scrapper.py"], capture_output=True, text=True, encoding='utf-8', errors='replace')
        st.text(result.stdout)

        if os.path.exists("entry_ids.json") and os.path.getsize("entry_ids.json") > 0:
            st.success("✅ Questions and entry IDs scraped successfully!")

            try:
                st.info("🧠 Running assistant...")
                assistant_result = subprocess.run(["python", "assistant.py"], capture_output=True, text=True, check=True, encoding='utf-8', errors='replace')
                st.text("✅ Assistant completed.")
                st.text("📤 STDOUT:\n" + assistant_result.stdout)
                st.text("❌ STDERR:\n" + assistant_result.stderr)
            except subprocess.CalledProcessError as e:
                st.error(f"❌ Assistant failed with error:\n{e.stderr}")

            if os.path.exists("answers.txt"):
                st.success("Here are the responses:")
                with open("answers.txt", "r", encoding="utf-8") as af:
                    answers = af.readlines()
                for i, ans in enumerate(answers, 1):
                    st.markdown(f"### ❓ Question {i}: {ans.strip()}")

                st.info("📤 Submitting form...")
                try:
                    submission = subprocess.run(["python", "form_submitter.py"], capture_output=True, text=True, check=True, encoding='utf-8', errors='replace')
                    st.success("✅ Form submitted successfully!")
                except subprocess.CalledProcessError as e:
                    st.error(f"❌ Form submission failed:\n{e.stderr}")
        else:
            st.error("❌ Could not find entry_ids.json or it's empty.")
