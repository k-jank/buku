import streamlit as st
import zipfile
from bs4 import BeautifulSoup
import os
from html.parser import HTMLParser

# Define the directory containing the books
books_dir = 'books/'

# Get the list of EPUB and PDF files in the directory
book_files = [f for f in os.listdir(books_dir) if f.endswith(('.epub', '.pdf'))]

lass MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.chapter_list = []
        self.current_tag = None
        self.current_title = None
        self.current_src = None

    def handle_starttag(self, tag, attrs):
        if tag == 'navPoint':
            self.current_title = None
            self.current_src = None
        elif tag == 'navLabel':
            self.current_tag = 'navLabel'
        elif tag == 'content':
            for attr in attrs:
                if attr[0] == 'src':
                    self.current_src = attr[1]

    def handle_endtag(self, tag):
        if tag == 'navPoint':
            if self.current_title and self.current_src:
                self.chapter_list.append((self.current_title, self.current_src))
        elif tag == 'navLabel':
            self.current_tag = None

    def handle_data(self, data):
        if self.current_tag == 'navLabel':
            self.current_title = data

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
                parser = MyHTMLParser()
                parser.feed(toc_ncx_content)
                
                for title, src in parser.chapter_list:
                    content_file = base_path + src
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
