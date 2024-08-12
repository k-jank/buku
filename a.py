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
        file_path = temp_file.name
        engine.save_to_file(text, file_path)
        engine.runAndWait()
        return file_path

# Streamlit app
st.title("Audio Playback Example")

text = "Hello, this is a test for Streamlit Cloud audio playback."

# Button for converting text to speech
if st.button("Generate and Play Audio"):
    audio_file_path = text_to_speech(text)

    # Print the file path and size for debugging
    st.write(f"Audio file path: {audio_file_path}")
    st.write(f"Audio file size: {os.path.getsize(audio_file_path)} bytes")

    # Check if the file exists and is non-empty
    if os.path.exists(audio_file_path) and os.path.getsize(audio_file_path) > 0:
        # Display the audio file
        st.audio(audio_file_path, format='audio/mp3')
    else:
        st.error("Failed to create audio file or file is empty.")
