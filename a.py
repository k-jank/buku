import streamlit as st
import pyttsx3
import tempfile
import shutil

# Inisialisasi pyttsx3
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Mengatur suara
engine.setProperty('rate', 170)  # Mengatur kecepatan bicara

def text_to_speech(text):
    """Fungsi untuk mengubah teks menjadi file audio sementara."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
        temp_path = temp_file.name
        engine.save_to_file(text, temp_path)
        engine.runAndWait()
        return temp_path

st.title("Text-to-Speech dengan pyttsx3")

# Input teks dari pengguna
text_input = st.text_area("Masukkan teks:", "Nama saya Jono.")

if st.button("Convert to Speech"):
    file_path = text_to_speech(text_input)
    
    # Menyalin file ke lokasi yang dapat diakses
    accessible_path = 'audio_output.wav'
    shutil.copy(file_path, accessible_path)
    
    # Menampilkan file audio
    st.audio(accessible_path, format='audio/wav')
    
    # Menghapus file sementara
    os.remove(file_path)
