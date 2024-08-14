import streamlit as st
import os
import zipfile
import xml.etree.ElementTree as ET

# Define the directory containing the books
books_dir = 'books/'

# Get the list of EPUB and PDF files in the directory
book_files = [f for f in os.listdir(books_dir) if f.endswith(('.epub', '.pdf'))]

# Function to read chapters from EPUB using the .ncx file
def get_chapters_from_epub(file_path):
    chapters = []
    
    with zipfile.ZipFile(file_path, 'r') as epub_zip:
        # Locate .ncx file
        ncx_files = [name for name in epub_zip.namelist() if name.endswith('.ncx')]
        if not ncx_files:
            return chapters
        
        ncx_file = ncx_files[0]
        
        # Read and parse the .ncx file
        with epub_zip.open(ncx_file) as f:
            ncx_content = f.read().decode('utf-8')
        
        root = ET.fromstring(ncx_content)
        
        # Namespaces used in NCX files
        namespaces = {
            'ncx': 'http://www.daisy.org/z3986/2005/ncx/'
        }
        
        for nav_point in root.findall('.//ncx:navPoint', namespaces):
            label_element = nav_point.find('ncx:navLabel/ncx:label', namespaces)
            title = label_element.text if label_element is not None else 'Untitled'
            content_element = nav_point.find('ncx:content', namespaces)
            content_file = content_element.get('src') if content_element is not None else ''
            chapters.append((title, content_file))
    
    return chapters

# Streamlit app
st.sidebar.title("Available Books")
selected_book = st.sidebar.selectbox("Select a book:", book_files)

if selected_book.endswith('.epub'):
    # Path to the selected EPUB book
    selected_book_path = os.path.join(books_dir, selected_book)
    
    # Get chapters from the selected EPUB book
    chapters = get_chapters_from_epub(selected_book_path)
    
    # Display chapter list in sidebar
    st.sidebar.title("Chapters")
    selected_chapter = st.sidebar.selectbox("Select a chapter:", [title for title, _ in chapters])
    
    # Display the selected chapter title
    st.write(f"### You selected chapter: {selected_chapter}")

    # Optionally, display content of the selected chapter
    content_file = next((content for title, content in chapters if title == selected_chapter), None)
    if content_file:
        with zipfile.ZipFile(selected_book_path, 'r') as epub_zip:
            content_path = content_file
            if content_path.startswith('/'):
                content_path = content_path[1:]
            with epub_zip.open(content_path) as f:
                chapter_content = f.read().decode('utf-8')
        st.write(f"**Content of {selected_chapter}:**")
        st.write(chapter_content)
else:
    st.write(f"**{selected_book}** format is not supported for chapter extraction.")
