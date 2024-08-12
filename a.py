import streamlit as st
import pyttsx3
import io

def generate_speech(text):
    # Inisialisasi pyttsx3
    engine = pyttsx3.init()

    # Mengambil daftar suara yang tersedia
    voices = engine.getProperty('voices')

    # Menetapkan suara ke suara kedua dalam daftar (jika ada)
    if len(voices) > 1:
        engine.setProperty('voice', voices[1].id)

    # Menetapkan kecepatan bicara
    engine.setProperty('rate', 170)

    # Menggunakan BytesIO untuk menyimpan audio di memori
    audio_buffer = io.BytesIO()

    # Menyimpan audio ke buffer BytesIO
    engine.save_to_file(text, 'output.wav')
    engine.runAndWait()
    
    # Membaca file audio ke dalam buffer BytesIO
    with open('output.wav', 'rb') as f:
        audio_buffer.write(f.read())

    # Reset buffer pointer ke awal
    audio_buffer.seek(0)
    return audio_buffer

# Aplikasi Streamlit
st.title("Text-to-Speech")

text = st.text_area("Enter text to convert to speech:", "Nama saya Jono.")

if st.button("Generate Speech"):
    audio_buffer = generate_speech(text)
    st.audio(audio_buffer, format='audio/wav')
