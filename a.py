import streamlit as st
import zipfile
from bs4 import BeautifulSoup
import os
from lxml import etree

# Define the directory containing the books
books_dir = 'books/'

# Get the list of EPUB and PDF files in the directory
book_files = [f for f in os.listdir(books_dir) if f.endswith(('.epub', '.pdf'))]

def get_chapters_from_epub(file_path):
    chapter_list = []
    
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        possible_paths = ['', 'OPS/', 'OEBPS/']
        toc_ncx_filename = None
        
        for path in possible_paths:
            toc_ncx = path + 'toc.ncx'
            if toc_ncx in zip_ref.namelist():
                toc_ncx_filename = toc_ncx
                base_path = path
                break
        
        if toc_ncx_filename:
            try:
                toc_ncx_content = zip_ref.read(toc_ncx_filename).decode('utf-8')
                root = etree.fromstring(toc_ncx_content)
                
                nav_points = root.findall('.//navPoint')
                
                for nav_point in nav_points:
                    nav_label = nav_point.find('navLabel')
                    title = nav_label.find('text').text if nav_label is not None else 'Unknown Title'
                    
                    content_src = nav_point.find('content').get('src') if nav_point.find('content') is not None else 'Unknown Content'
                    content_file = base_path + content_src
                    
                    chapter_list.append((title, content_file))
            
            except Exception as e:
                print(f"Error reading or parsing {toc_ncx_filename}: {e}")
        else:
            print("Table of contents (toc.ncx) not found in the EPUB file.")
    
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
