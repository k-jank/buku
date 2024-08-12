import io
import pyttsx3
import streamlit as st

def text_to_speech(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  # Set the voice to the second option
    engine.setProperty('rate', 170)  # Set speech rate to 170 words per minute
    
    # Save the speech to a BytesIO stream
    audio_stream = io.BytesIO()
    engine.save_to_file(text, audio_stream)
    engine.runAndWait()
    audio_stream.seek(0)  # Rewind the stream to the beginning
    return audio_stream

# Streamlit app
st.title("Audio Playback Example")

text = "Hello, this is a test for Streamlit Cloud audio playback."

# Button for converting text to speech
if st.button("Generate and Play Audio"):
    audio_stream = text_to_speech(text)
    st.audio(audio_stream, format='audio/mp3')
