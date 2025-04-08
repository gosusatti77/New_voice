import streamlit as st
import subprocess
import time

# Set page config to wide mode
st.set_page_config(layout="wide")

st.title("🎙️ Voice Assistant Google Form Filler")

# Google Form URL
form_url = st.text_input("Paste your Google Form URL:", value="https://docs.google.com/forms/d/e/1FAIpQLSeB22-AVkNP4baK1MEOzR8pywn5VhxVlIQ-NdtPqFvduoo67g/viewform")

col1, col2 = st.columns(2)

with col1:
    st.header("🧠 Voice Assistant Panel")

    if st.button("Start Assistant"):
        with st.spinner("Scraping questions and entry IDs..."):
            subprocess.run(["python", "New_scrapper.py"])
        st.success("✅ Scraped questions!")

        with st.spinner("Running voice assistant..."):
            subprocess.run(["python", "assistant.py"])
        st.success("✅ Voice assistant completed.")

        with st.spinner("Submitting form..."):
            subprocess.run(["python", "form_submitter.py"])
        st.success("✅ Form submitted!")

with col2:
    st.header("📄 Google Form Preview")
    st.markdown(
        f'<iframe src="{form_url}" width="100%" height="700" style="border: none;"></iframe>',
        unsafe_allow_html=True
    )
