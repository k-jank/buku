import streamlit as st
import os
import zipfile
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from gtts import gTTS
import tempfile
import fitz
import re
import io
from PIL import Image
from io import BytesIO
import base64

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
                base_path = path
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
            
            # Correct the path prefix based on the base path
            if not content_file.startswith(('OPS/', 'OEBPS/')):
                content_file = base_path + content_file
            
            chapter_list.append((title, content_file))
    
    return chapter_list

# Function to convert HTML to formatted text for display
def generate_formatted_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    text = ''
    
    for tag in soup.find_all(['h1', 'h2', 'h3', 'p', 'div']):
        if tag.name == 'h1':
            text += f'<h1 style="text-align:center; font-size:2em; margin-top:20px;">{tag.get_text()}</h1>\n'
        elif tag.name == 'h2':
            text += f'<h2 style="text-align:center; font-size:1.5em; margin-top:15px;">{tag.get_text()}</h2>\n'
        elif tag.name == 'h3':
            text += f'<h3 style="text-align:center; font-size:1.2em; margin-top:10px;">{tag.get_text()}</h3>\n'
        elif tag.name == 'p':
            text += f'<p style="margin-bottom:10px;">{tag.get_text()}</p>\n'

    return text.strip()

# Function to extract plain text for gTTS
def extract_text_for_gtts(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text(separator='\n').strip()

# Function to extract text from EPUB chapters
def extract_text_from_chapters(file_path, chapters):
    text_content = {}
    
    with zipfile.ZipFile(file_path, 'r') as epub_zip:
        for title, content_file in chapters:
            if content_file in epub_zip.namelist():
                content = epub_zip.read(content_file).decode('utf-8')
                text_content[title] = generate_formatted_html(content)
            else:
                text_content[title] = "Konten tidak ditemukan."
    
    return text_content

#Epub Cover
def epub_cover(epub_path, thumbnail_size=(150, 250)):
    # Open the EPUB file as a zip
    with zipfile.ZipFile(epub_path, 'r') as z:
        # Find the cover image
        cover_file = None
        for file in z.namelist():
            if 'cover' in file.lower() and file.lower().endswith(('.jpg', '.jpeg', '.png')):
                cover_file = file
                break

        if cover_file is None:
            return None  # No cover image found, return None
        
        # Read the cover image as a byte stream
        with z.open(cover_file) as f:
            cover_image = BytesIO(f.read())
        
        # Open the image from the byte stream
        image = Image.open(cover_image)
        
        # Resize the image to the thumbnail size
        image.thumbnail(thumbnail_size)
        
        return image

def remove_page_numbers(text):
    # Regex pattern to identify page numbers, assuming they are on their own line or separated by newlines
    pattern = r'^\d+$'
    lines = text.split('\n')
    cleaned_lines = [line for line in lines if not re.match(pattern, line.strip())]
    return '\n'.join(cleaned_lines)

def get_chapters_from_pdf(file_path):
    chapter_list = []
    
    # Open PDF file
    with fitz.open(file_path) as doc:
        num_pages = doc.page_count
        text_by_page = []
        
        # Extract text from each page
        for i in range(num_pages):
            page = doc.load_page(i)
            text = page.get_text()
            text_by_page.append(text)
        
        # Combine all text for analysis
        full_text = "\n".join(text_by_page)
        
        # Remove page numbers from the text
        cleaned_text = remove_page_numbers(full_text)
        
        # Patterns to match chapter titles
        pattern_with_prefix = r'\bBAB\s+[IVXLCDM]+\b|\bBAB\s+\d+'
        pattern_textual = r'\bBagian\s+(Pertama|Kedua|Ketiga|Keempat|Kelima)\b'
        
        # Find all matches for chapter titles
        combined_pattern = f'{pattern_with_prefix}|{pattern_textual}'
        chapter_titles = re.findall(combined_pattern, cleaned_text, flags=re.IGNORECASE)
        
        # Create a list of positions for each title
        positions = [m.start() for m in re.finditer(combined_pattern, cleaned_text, flags=re.IGNORECASE)]
        
        # Add end position for the last chapter
        positions.append(len(cleaned_text))
        
        for i in range(len(positions) - 1):
            start_pos = positions[i]
            end_pos = positions[i + 1]
            
            # Extract the chapter content
            chapter_content = cleaned_text[start_pos:end_pos].strip()
            
            # Extract the title of the chapter
            title_match = re.search(combined_pattern, chapter_content, flags=re.IGNORECASE)
            title = title_match.group() if title_match else 'Unknown Title'
            
            # Extract first line after title to include in output
            lines = chapter_content.split('\n')
            first_line_after_title = lines[1] if len(lines) > 1 else ""
            
            chapter_list.append((title, chapter_content))
            print(f"Detected {title}: {first_line_after_title}")
    
    return chapter_list

#PDF Cover
def pdf_cover(pdf_path, page_number=0, thumbnail_size=(150, 250)):
    pdf_document = fitz.open(pdf_path)
    page = pdf_document.load_page(page_number)
    pix = page.get_pixmap()
    img = Image.open(BytesIO(pix.tobytes()))
    img.thumbnail(thumbnail_size)  # Resize the image to the thumbnail size
    pdf_document.close()
    return img
    
# Function to convert text to speech using gTTS
def text_to_speech(text):
    try:
        tts = gTTS(text=text, lang='id')  
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
book_files.sort()

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
        # Get the cover image from the EPUB file
        cover_image = epub_cover(book_file_path)
        
        if cover_image is not None:
            # If cover image is available, process and display it
            buffered = io.BytesIO()
            cover_image.save(buffered, format="PNG")
            cover_image_bytes = buffered.getvalue()
            
            st.markdown(
                f"<div style='text-align: center;'>"
                f"<img src='data:image/png;base64,{base64.b64encode(cover_image_bytes).decode()}' style='display: inline-block;' />"
                f"</div>",
                unsafe_allow_html=True
            )
            # Handle the case where no cover image is available
            title_parts = [part.strip() for part in selected_title.split(' - ')]
            st.markdown(
                f"<div style='text-align: center;'>"
                f"<strong>{title_parts[0]}</strong> <br>"
                f"{title_parts[1]}"
                f"</div>",
                unsafe_allow_html=True
            )
        else:
            # Handle the case where no cover image is available
            title_parts = [part.strip() for part in selected_title.split(' - ')]
            st.markdown(
                f"<div style='text-align: center;'>"
                f"<strong>{title_parts[0]}</strong> <br>"
                f"{title_parts[1]}"
                f"</div>",
                unsafe_allow_html=True
            )
        
        # Process EPUB file
        chapters = get_chapters_from_epub(book_file_path)
        formatted_texts = extract_text_from_chapters(book_file_path, chapters)
        text_for_speech = {title: extract_text_for_gtts(html_content) for title, html_content in formatted_texts.items()}

        # Create a sidebar for chapter selection
        selected_chapter = st.sidebar.selectbox("Pilihan Bab", [title for title, _ in chapters])

        if selected_chapter:
            chapter_text = formatted_texts.get(selected_chapter, "Konten tidak ditemukan.")
            text_for_speech_content = text_for_speech.get(selected_chapter, "Konten tidak ditemukan.")

            # Button for converting text to speech
            if st.button("Dengarkan Audio"):
                audio_file_path = text_to_speech(text_for_speech_content)
                if audio_file_path:
                    st.audio(audio_file_path, format='audio/mp3')
            
            # Display the selected chapter content in a collapsible section with title
            with st.expander(f"Tampilkan Isi Buku: {selected_chapter}"):
                st.markdown(chapter_text, unsafe_allow_html=True)
        else:
            st.write("Please select a chapter from the sidebar.")
    
    elif file_extension == '.pdf':
        # Get the cover image from the PDF file
        cover_image = pdf_cover(book_file_path)
        buffered = io.BytesIO()
        cover_image.save(buffered, format="PNG")
        cover_image_bytes = buffered.getvalue()
            
        st.markdown(
            f"<div style='text-align: center;'>"
            f"<img src='data:image/png;base64,{base64.b64encode(cover_image_bytes).decode()}' style='display: inline-block;' />"
            f"</div>",
            unsafe_allow_html=True
        )
        
        # Handle the case where no cover image is available
        title_parts = [part.strip() for part in selected_title.split(' - ')]
        st.markdown(
            f"<div style='text-align: center;'>"
            f"<strong>{title_parts[0]}</strong><br>"
            f"{title_parts[1]}"
            f"</div>",
            unsafe_allow_html=True
        )
        
        # Process PDF file
        chapters = get_chapters_from_pdf(book_file_path)
        text_for_speech = {title: extract_text_for_gtts(text) for title, text in chapters}
    
        # Create a sidebar for chapter selection
        selected_chapter = st.sidebar.selectbox("Pilihan Bab", [title for title, _ in chapters])

        if selected_chapter:
            chapter_text = next((text for title, text in chapters if title == selected_chapter), "Konten tidak ditemukan.")
            text_for_speech_content = text_for_speech.get(selected_chapter, "Konten tidak ditemukan.")
            
            # Button for converting text to speech
            if st.button("Dengarkan Audio"):
                audio_file_path = text_to_speech(text_for_speech_content)
                if audio_file_path:
                    st.audio(audio_file_path, format='audio/mp3')
            
            # Display the selected chapter content in a collapsible section with title
            with st.expander(f"Tampilkan Isi Buku: {selected_chapter}"):
                st.markdown(chapter_text)
        else:
            st.write("Please select a chapter from the sidebar.")
else:
    st.write(f"{selected_title}")
