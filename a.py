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
            label_element = nav_point.find('ncx:navLabel/ncx:text', namespaces)  # Changed to 'ncx:text'
            title = label_element.text if label_element is not None else 'Untitled'
            content_element = nav_point.find('ncx:content', namespaces)
            content_file = content_element.get('src') if content_element is not None else ''
            chapter_list.append((title, content_file))
    
    return chapter_list

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

else:
    st.write(f"**{selected_book}** format is not supported for chapter extraction.")
