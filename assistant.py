import openai
import os
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play
from openai import OpenAI
import json
import sys
import io
from dotenv import load_dotenv
load_dotenv()
# Force stdout to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)  # Replace with your key

def generate_conversational_prompt(question):
    system_prompt = "You are a friendly voice assistant helping someone fill out a form. Rewrite the following question to sound more conversational and human-like."
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

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        print("🎙️ Listening...")
        audio = r.listen(source)
        print("✅ Got it. Transcribing...")

        with open("temp_input.wav", "wb") as f:
            f.write(audio.get_wav_data())

        with open("temp_input.wav", "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language="en"
            )
        
        return transcript.text.strip()

def run_voice_assistant():
    print("Starting your voice assistant...\n")

    with open("entry_ids.json", "r", encoding="utf-8") as f:
        questions_data = json.load(f)

    answers = []

    for i, qdata in enumerate(questions_data):
        question = qdata["question"]
        prompt = generate_conversational_prompt(question)
        print(f"\n Asking: {prompt}")
        speak(prompt)

        try:
            answer = listen()
        except Exception as e:
            print(" Something went wrong:", str(e))
            answer = "[Couldn't understand]"

        print(f" Answer: {answer}")
        answers.append(answer)

    with open("answers.txt", "w", encoding="utf-8") as f:
        for a in answers:
            f.write(a + "\n")

if __name__ == "__main__":
    run_voice_assistant()
