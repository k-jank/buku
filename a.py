import streamlit as st
import pyttsx3
import os

# Inisialisasi pyttsx3
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Mengatur suara
engine.setProperty('rate', 170)  # Mengatur kecepatan bicara

def text_to_speech(text, file_path):
    """Fungsi untuk mengubah teks menjadi file audio."""
    engine.save_to_file(text, file_path)
    engine.runAndWait()

st.title("Text-to-Speech dengan pyttsx3")

# Input teks dari pengguna
text_input = st.text_area("Masukkan teks:", "Nama saya Jono.")

if st.button("Convert to Speech"):
    # Menyimpan file audio sementara
    file_path = 'temp_audio.wav'
    text_to_speech(text_input, file_path)
    
    # Memutar file audio
    st.audio(file_path, format='audio/wav')

    # Menghapus file audio sementara
    os.remove(file_path)
