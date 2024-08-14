import streamlit as st
import os
import zipfile
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from gtts import gTTS
import tempfile

# Define the directory containing the books
books_dir = 'books/'

# Get the list of EPUB and PDF files in the directory
book_files = [f for f in os.listdir(books_dir) if f.endswith(('.epub', '.pdf'))]

# Function to read chapters from EPUB using the .ncx file
def get_chapters_from_epub(file_path):
    chapter_list = []
    
    with zipfile.ZipFile(file_path, 'r') as epub_zip:
        possible_paths = ['', 'OPS/', 'OEBPS/']
        toc_ncx_filename = None
        
        # Check each possible path for toc.ncx
        for path in possible_paths:
            toc_ncx = path + 'toc.ncx'
            if toc_ncx in epub_zip.namelist():
                toc_ncx_filename = toc_ncx
                break
        
        if toc_ncx_filename is None:
            return chapter_list
        
        # Read and parse the .ncx file
        with epub_zip.open(toc_ncx_filename) as f:
            ncx_content = f.read().decode('utf-8')
        
        root = ET.fromstring(ncx_content)
        
        # Namespaces used in NCX files
        namespaces = {
            'ncx': 'http://www.daisy.org/z3986/2005/ncx/'
        }
        
        for nav_point in root.findall('.//ncx:navPoint', namespaces):
            label_element = nav_point.find('ncx:navLabel/ncx:text', namespaces)
            title = label_element.text if label_element is not None else 'Untitled'
            content_element = nav_point.find('ncx:content', namespaces)
            content_file = content_element.get('src') if content_element is not None else ''
            chapter_list.append((title, content_file))
    
    return chapter_list

# Function to convert HTML to text with formatting
def html_to_text_with_formatting(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    text = ''
    for tag in soup.find_all(['h1', 'h2', 'h3', 'p']):
        if tag.name == 'h1':
            text += f'<h1 style="text-align:center; font-size:2em; margin-top:20px;">{tag.get_text()}</h1>\n'
        elif tag.name == 'h2':
            text += f'<h2 style="text-align:center; font-size:1.5em; margin-top:15px;">{tag.get_text()}</h2>\n'
        elif tag.name == 'h3':
            text += f'<h3 style="text-align:center; font-size:1.2em; margin-top:10px;">{tag.get_text()}</h3>\n'
        elif tag.name == 'p':
            text += f'<p style="margin-bottom:10px;">{tag.get_text()}</p>\n'
    return text.strip()

# Function to extract text from EPUB chapters
def extract_text_from_chapters(file_path, chapters):
    text_content = {}
    
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        for title, content_file in chapters:
            if content_file in zip_ref.namelist():
                content = zip_ref.read(content_file).decode('utf-8')  # Decode content to string
                text_content[title] = html_to_text_with_formatting(content)
            else:
                text_content[title] = "Konten tidak ditemukan."
    
    return text_content

# Function to convert text to speech using gTTS
def text_to_speech(text):
    try:
        tts = gTTS(text=text, lang='id')  # 'id' is for Indonesian, change if needed
        # Save the speech to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_file.close()
            tts.save(temp_file.name)
            return temp_file.name
    except Exception as e:
        st.error(f"Error generating speech: {str(e)}")
        return None


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

# Sidebar for book selection
st.sidebar.header('Pilihan Buku')

# List available EPUB and PDF files in the books directory
book_files = [f for f in os.listdir(books_dir) if f.endswith(('.epub', '.pdf'))]

# Remove the extensions for display
book_titles = [os.path.splitext(f)[0] for f in book_files]

# Add an empty option to the dropdown
book_titles.insert(0, "Pilih Buku...")

# Create the sidebar selectbox with default empty option
selected_title = st.sidebar.selectbox("Pilih Judul Buku", book_titles)

if selected_title != "Pilih Buku...":
    # Resolve the full path of the selected file
    selected_book = next(f for f in book_files if os.path.splitext(f)[0] == selected_title)
    book_file_path = os.path.join(books_dir, selected_book)

    # Determine file type based on extension
    file_extension = os.path.splitext(selected_book)[1].lower()

    if file_extension == '.epub':
        # Process EPUB file
        chapters = get_chapters_from_epub(book_file_path)
        texts = extract_text_from_chapters(book_file_path, chapters)

        # Create a sidebar for chapter selection
        selected_chapter = st.sidebar.selectbox("Pilihan Bab", [title for title, _ in chapters])

        if selected_chapter:
            chapter_text = texts.get(selected_chapter, "Konten tidak ditemukan.")
            
            # Button for converting text to speech
            if st.button("Dengarkan Audio"):
                audio_file_path = text_to_speech(chapter_text)
                st.audio(audio_file_path, format='audio/mp3')
            
            # Display the selected chapter content in a collapsible section with title
            with st.expander(f"Tampilkan Isi Buku: {selected_chapter}"):
                st.markdown(chapter_text, unsafe_allow_html=True)
        else:
            st.write("Please select a chapter from the sidebar.")
else:
    st.write(f"**{selected_title}** format is not supported for chapter extraction.")
