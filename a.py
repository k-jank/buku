import streamlit as st
import pyttsx3
import io
import wave

def text_to_speech(text):
    """Fungsi untuk mengubah teks menjadi file audio."""
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  # Mengatur suara
    engine.setProperty('rate', 170)  # Mengatur kecepatan bicara

    # Simpan output suara dalam buffer
    with io.BytesIO() as buffer:
        # Output ke file WAV
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(22050)
            engine.save_to_file(text, 'temp.wav')
            engine.runAndWait()

            with open('temp.wav', 'rb') as f:
                wav_file.writeframes(f.read())

            buffer.seek(0)
            return buffer.getvalue()

st.title("Text-to-Speech dengan pyttsx3")

# Input teks dari pengguna
text_input = st.text_area("Masukkan teks:", "Nama saya Jono.")

if st.button("Convert to Speech"):
    audio_data = text_to_speech(text_input)
    st.audio(audio_data, format='audio/wav')
