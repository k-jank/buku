import streamlit as st
import pyttsx3
import tempfile
import os

# Function to convert text to speech and return a path to the audio file
def text_to_speech(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  # Set the voice to the second option
    engine.setProperty('rate', 170)  # Set speech rate to 170 words per minute

    # Save the speech to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
        temp_file.close()
        engine.save_to_file(text, temp_file.name)
        engine.runAndWait()
        return temp_file.name

# Streamlit app
st.title("Audio Playback Example")

text = "Hello, this is a test for Streamlit Cloud audio playback."

# Button for converting text to speech
if st.button("Generate and Play Audio"):
    audio_file_path = text_to_speech(text)

    # Print the file path and size for debugging
    st.write(f"Audio file path: {audio_file_path}")
    st.write(f"Audio file size: {os.path.getsize(audio_file_path)} bytes")

    # Display the audio file
    st.audio(audio_file_path, format='audio/mp3')
