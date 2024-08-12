import streamlit as st
import zipfile
from bs4 import BeautifulSoup
import os
from gtts import gTTS
import io

# Fungsi untuk menghapus tag HTML
def remove_html_tags(html_content):
    """Fungsi untuk menghapus tag HTML dan mengembalikan teks saja."""
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text()

# Fungsi untuk mengonversi HTML menjadi teks
def html_to_text_with_formatting(html_content):
    # Function to convert HTML to text with formatting
    soup = BeautifulSoup(html_content, 'html.parser')
    text = ''
    for tag in soup.find_all(['h1', 'h2', 'h3', 'p']):
        if tag.name == 'h1':
            text += f'{tag.get_text()}\n'
        elif tag.name == 'h2':
            text += f'{tag.get_text()}\n'
        elif tag.name == 'h3':
            text += f'{tag.get_text()}\n'
        elif tag.name == 'p':
            text += f'{tag.get_text()}\n'
    return text.strip()

# Fungsi untuk mengekstrak teks dari bab-bab EPUB
def extract_text_from_chapters(file_path, chapters):
    text_content = {}
    
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        for title, content_file in chapters:
            if content_file in zip_ref.namelist():
                content = zip_ref.read(content_file).decode('utf-8')  # Decode bytes to string
                clean_text = remove_html_tags(content)  # Remove HTML tags
                text_content[title] = clean_text
            else:
                text_content[title] = "Konten tidak ditemukan."
    
    return text_content

# Fungsi untuk mengonversi teks menjadi audio menggunakan gTTS
def text_to_speech(text):
    tts = gTTS(text=text, lang='id')
    with io.BytesIO() as buffer:
        tts.write_to_fp(buffer)
        buffer.seek(0)
        return buffer.getvalue()

# Streamlit app
st.markdown("""
    <style>
    .title {
        text-align: center;
        font-size: 3em;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    </style>
    <div class="title">NDONGENG</div>
""", unsafe_allow_html=True)

st.sidebar.header('Pilihan Buku')

# List available EPUB files in the books directory
books_dir = 'books/'
epub_files = [f for f in os.listdir(books_dir) if f.endswith('.epub')]

# Remove the '.epub' extension for display
book_titles = [os.path.splitext(f)[0] for f in epub_files]

# Add an empty option to the dropdown
book_titles.insert(0, "Pilih Buku...")

# Create the sidebar selectbox with default empty option
selected_title = st.sidebar.selectbox("Pilih Judul Buku", book_titles)

if selected_title != "Pilih Buku...":
    # Resolve the full path of the selected EPUB file
    selected_book = next(f for f in epub_files if os.path.splitext(f)[0] == selected_title)
    epub_file_path = os.path.join(books_dir, selected_book)

    # Load metadata and chapters
    metadata = get_metadata_from_epub(epub_file_path)
    chapters = get_chapters_from_toc_ncx(epub_file_path)
    texts = extract_text_from_chapters(epub_file_path, chapters)

    # Display metadata
    st.write(f"**Judul:** {metadata['title']}")
    st.write(f"**Penulis:** {metadata['author']}")

    # Create a sidebar for chapter selection
    selected_chapter = st.sidebar.selectbox("Pilihan Bab", [title for title, _ in chapters])

    if selected_chapter:
        chapter_text = texts.get(selected_chapter, "Konten tidak ditemukan.")
        
        # Button for converting text to speech
        if st.button("Dengarkan Audio"):
            audio_data = text_to_speech(chapter_text)
            st.audio(audio_data, format='audio/mp3')
        
        # Display the selected chapter content in a collapsible section with title
        with st.expander(f"Tampilkan Isi Buku: {selected_chapter}"):
            st.markdown(chapter_text, unsafe_allow_html=True)
    else:
        st.write("Please select a chapter from the sidebar.")

    st.write(f"**Deskripsi Buku:** {metadata['description']}")
else:
    st.write("Silakan pilih buku terlebih dahulu.")
