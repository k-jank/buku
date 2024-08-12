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
text_input = st.text_area("Masukkan teks:", "Tidaklah tepat untuk mengatakan bahwa semua orang di negara-negara industri yang belum berkembang yang tidak dipengaruhi oleh agama Kristen atau Islam ortodoks percaya pada reinkarnasi. 
Beberapa orang tetap bertahan dengan ajaran-ajaran ini dan tetap mempertahankan agama-agama tradisional yang tidak menyertakan kepercayaan ini.

Namun, beberapa pengecualian ini, sedikit mengurangi generalisasi bahwa hampir semua orang di luar jangkauan Kristen ortodoks, Yahudi, Islam, dan Sains - yang terakhir adalah agama sekuler bagi banyak orang - percaya pada reinkarnasi.

Saya akan mempertimbangkan selanjutnya bagaimana hal ini bisa terjadi.")

if st.button("Convert to Speech"):
    audio_data = text_to_speech(text_input)
    st.audio(audio_data, format='audio/mp3')
