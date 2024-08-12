import streamlit as st
import pyttsx3
import tempfile
import os

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

    # Membuat file sementara dengan ekstensi .wav
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
        temp_file_path = temp_file.name

    try:
        # Menyimpan audio ke file sementara
        engine.save_to_file(text, temp_file_path)
        engine.runAndWait()
        
        # Kembalikan path file sementara
        return temp_file_path
    finally:
        # Hapus file sementara setelah digunakan
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

# Aplikasi Streamlit
st.title("Text-to-Speech")

text = st.text_area("Enter text to convert to speech:", "Nama saya Jono.")

if st.button("Generate Speech"):
    audio_path = generate_speech(text)
    st.audio(audio_path, format='audio/wav')
