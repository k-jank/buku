import streamlit as st
import zipfile
from bs4 import BeautifulSoup
import os
from gtts import gTTS
import tempfile

# Function to read chapters from toc.ncx
def get_chapters_from_toc_ncx(file_path):
    chapter_list = []
    
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        toc_ncx_filename = 'toc.ncx'
        if toc_ncx_filename in zip_ref.namelist():
            toc_ncx_content = zip_ref.read(toc_ncx_filename)
            soup = BeautifulSoup(toc_ncx_content, 'xml')
            nav_points = soup.find_all('navPoint')
            
            for nav_point in nav_points:
                title = nav_point.find('navLabel').find('text').get_text()
                content = nav_point.find('content')['src']
                chapter_list.append((title, content))
        else:
            st.error("Table of contents (toc.ncx) not found in the EPUB file.")
    
    return chapter_list

# Function to extract metadata from EPUB file
def get_metadata_from_epub(file_path):
    metadata = {
        'title': '',
        'author': '',
        'description': ''
    }
    
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        if 'META-INF/container.xml' in zip_ref.namelist():
            container_xml_content = zip_ref.read('META-INF/container.xml')
            soup = BeautifulSoup(container_xml_content, 'xml')
            rootfile_path = soup.find('rootfile')['full-path']
            
            if rootfile_path:
                opf_content = zip_ref.read(rootfile_path)
                soup = BeautifulSoup(opf_content, 'xml')
                metadata['title'] = soup.find('title').get_text() if soup.find('title') else metadata['title']
                metadata['author'] = soup.find('creator').get_text() if soup.find('creator') else metadata['author']
                metadata['description'] = soup.find('description').get_text() if soup.find('description') else metadata['description']
    
    return metadata

# Function to extract plain text from HTML for gTTS
def extract_text_for_gtts(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Extract only the text, stripping out HTML tags
    return soup.get_text(separator='\n').strip()

# Function to generate formatted HTML for display in Streamlit
def generate_formatted_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    text = ''
    for tag in soup.find_all(['h1', 'h2', 'h3', 'p']):
        if tag.name == 'h1':
            text += f'<h1 style="text-align:center; font-size:2em; font-weight:bold; margin-top:20px; margin-bottom:10px;">{tag.get_text()}</h1>\n'
        elif tag.name == 'h2':
            text += f'<h2 style="text-align:center; font-size:1.5em; font-weight:bold; margin-top:20px; margin-bottom:10px;">{tag.get_text()}</h2>\n'
        elif tag.name == 'h3':
            text += f'<h3 style="text-align:center; font-size:1.2em; font-weight:bold; margin-top:20px; margin-bottom:10px;">{tag.get_text()}</h3>\n'
        elif tag.name == 'p':
            text += f'<p style="margin-bottom:20px;">{tag.get_text()}</p>\n'
    return text.strip()

# Function to convert text to speech using gTTS
def text_to_speech(text):
    tts = gTTS(text=text, lang='id')  # 'id' is for Indonesian, change if needed
    # Save the speech to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
        temp_file.close()
        tts.save(temp_file.name)
        return temp_file.name

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
    chapter_texts = {title: extract_text_for_gtts(zipfile.ZipFile(epub_file_path, 'r').read(content_file)) for title, content_file in chapters}
    formatted_texts = {title: generate_formatted_html(zipfile.ZipFile(epub_file_path, 'r').read(content_file)) for title, content_file in chapters}

    # Display metadata
    st.write(f"**Judul:** {metadata['title']}")
    st.write(f"**Penulis:** {metadata['author']}")

    # Create a sidebar for chapter selection
    selected_chapter = st.sidebar.selectbox("Pilihan Bab", [title for title, _ in chapters])

    if selected_chapter:
        chapter_text = formatted_texts.get(selected_chapter, "Konten tidak ditemukan.")
        text_for_speech = chapter_texts.get(selected_chapter, "Konten tidak ditemukan.")
        
        # Button for converting text to speech
        if st.button("Dengarkan Audio"):
            audio_file_path = text_to_speech(text_for_speech)
            st.audio(audio_file_path, format='audio/mp3')
        
        # Display the selected chapter content in a collapsible section with title
        with st.expander(f"Tampilkan Isi Buku: {selected_chapter}"):
            st.markdown(chapter_text, unsafe_allow_html=True)
    else:
        st.write("Please select a chapter from the sidebar.")

    st.write(f"**Deskripsi Buku:** {metadata['description']}")
else:
    st.write("Please select a book from the sidebar.")
