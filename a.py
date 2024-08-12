import streamlit as st
from gtts import gTTS
import io

def text_to_speech(text):
    """Fungsi untuk mengubah teks menjadi file audio dalam buffer."""
    tts = gTTS(text=text, lang='id')
    with io.BytesIO() as buffer:
        tts.write_to_fp(buffer)
        buffer.seek(0)
        return buffer.getvalue()

st.title("Text-to-Speech dengan gTTS")

# Input teks dari pengguna
text_input = st.text_area("Masukkan teks:", "Nama saya Jono.")

if st.button("Convert to Speech"):
    audio_data = text_to_speech(text_input)
    st.audio(audio_data, format='audio/mp3')
