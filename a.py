import io
import pyttsx3
import streamlit as st
from IPython.display import Audio

# Function to convert text to speech and return an audio stream
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
    
    # Create an HTML audio player
    st.markdown(
        f"""
        <audio controls>
            <source src="data:audio/mp3;base64,{audio_stream.getvalue().decode('latin1')}" type="audio/mp3">
            Your browser does not support the audio tag.
        </audio>
        """,
        unsafe_allow_html=True
    )
