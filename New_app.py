import streamlit as st
import subprocess
import time
from pydub import AudioSegment
from pydub.playback import play
import os
import json
import speech_recognition as sr
from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)  # Replace with your key

def generate_conversational_prompt(question):
    system_prompt = "You are a friendly voice assistant helping someone fill out a form. Ask the user this question conversationally."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content.strip()


def speak(text, filename="temp.mp3"):
    response = client.audio.speech.create(model="tts-1", voice="nova", input=text)
    with client.audio.speech.with_streaming_response.create(model="tts-1", voice="nova", input=text) as response:
        with open(filename, "wb") as f:
            for chunk in response.iter_bytes():
                f.write(chunk)

    audio = AudioSegment.from_file(filename, format="mp3")
    play(audio)
    os.remove(filename)

# def listen():
#     r = sr.Recognizer()
#     with sr.Microphone() as source:
#         r.adjust_for_ambient_noise(source, duration=1)
#         print("🎙️ Listening...")
#         audio = r.listen(source)
#         print("✅ Got it. Transcribing...")

#         with open("temp_input.wav", "wb") as f:
#             f.write(audio.get_wav_data())

#         with open("temp_input.wav", "rb") as f:
#             transcript = client.audio.transcriptions.create(
#                 model="whisper-1",
#                 file=f,
#                 language="en"
#             )
        
#         return transcript.text.strip()


def run_voice_assistant_streamlit(entry_data):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    answers = []

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)

    for i, item in enumerate(entry_data):
        question = item["question"]
        st.session_state["current_question"] = question
        st.session_state["current_answer"] = ""

        # Show current question in Streamlit
        question_placeholder = st.empty()
        answer_placeholder = st.empty()

        question_placeholder.markdown(f"###  Question {i + 1}: {question}")

        # Generate prompt (you might want to use GPT here)
        prompt = generate_conversational_prompt(question)
        speak(prompt)

        with mic as source:
            st.info("🎙️ Listening...") 
            audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio)
            st.success(f"🗣️ Answer: {text}")
            answers.append(text)
            # answer_placeholder.markdown(f"**Answer:** {text}")
            # st.session_state["current_answer"] = text

        except Exception as e:
            st.error("😞 Could not understand.")
            answers.append("[Couldn't understand]")
            answer_placeholder.markdown(f"**Answer:** [Couldn't understand]")

        time.sleep(1)

    with open("answers.txt", "w", encoding="utf-8") as f:
        for ans in answers:
            f.write(ans + "\n")

    return answers

st.set_page_config(page_title="Voice Assistant for Google Forms", layout="wide")
st.title("🎤 Voice Assistant for Google Form")

form_url = st.text_input("Paste your Google Form URL here:")

col1, col2 = st.columns(2)

with col1:
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
                    # Load entry data
                    with open("entry_ids.json", "r", encoding="utf-8") as f:
                        entry_data = json.load(f)

                    st.info("🧠 Running assistant...")
                    assistant_result = run_voice_assistant_streamlit(entry_data)
                    st.success("✅ Assistant completed!")
                    # st.text("✅ Assistant completed.")
                    # st.text("📤 STDOUT:\n" + assistant_result.stdout)
                    # st.text("❌ STDERR:\n" + assistant_result.stderr)
                except subprocess.CalledProcessError as e:
                    st.error(f"❌ Assistant failed with error:\n{e.stderr}")

                if os.path.exists("answers.txt"):
                    # st.success("Here are the responses:")
                    with open("answers.txt", "r", encoding="utf-8") as af:
                        answers = af.readlines()
                    # for i, ans in enumerate(answers, 1):
                    #     st.markdown(f"### ❓ Question {i}: {ans.strip()}")

                    st.info("📤 Submitting form...")
                    try:
                        submission = subprocess.run(["python", "form_submitter.py"], capture_output=True, text=True, check=True, encoding='utf-8', errors='replace')
                        st.success("✅ Form submitted successfully!")
                    except subprocess.CalledProcessError as e:
                        st.error(f"❌ Form submission failed:\n{e.stderr}")
            else:
                st.error("❌ Could not find entry_ids.json or it's empty.")

with col2:
    st.header("📄 Google Form Preview")
    st.markdown(
        f'<iframe src="{form_url}" width="100%" height="700" style="border: none;"></iframe>',
        unsafe_allow_html=True
    )