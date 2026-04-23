import os  
from ebooklib import epub, ITEM_DOCUMENT 
from bs4 import BeautifulSoup 
from pypdf import PdfReader  
def read_txt(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def read_epub(path):
    book = epub.read_epub(path)
    text_blocks = []

    # Go trough all book elements
    for item in book.get_items():
        # We need only text documents (HTML inside EPUB)
        if item.get_type() == ITEM_DOCUMENT:
            #BeautifulSoup clearing text from HTML-tags 
            soup = BeautifulSoup(item.get_body_content(), 'html.parser')
            text_blocks.append(soup.get_text(separator='\n', strip=True))

    return '\n'.join(text_blocks)
def read_fb2(path):
    with open(path, 'r', encoding='utf-8') as file:
        #FB2 - it's XML, so we use lxml-xml parser 
        soup = BeautifulSoup(file, 'lxml-xml')

        #The main text in Fb2 stored in <p> and <v> tags 
        text_blocks = []
        for i in soup.find_all(['p', 'v']):
            text_blocks.append(i.get_text(strip=True))

        return '\n'.join(text_blocks)

def read_pdf(path):
    text_blocks = []
    # Reading file in rb format 
    with open(path, 'rb') as f:
        reader = PdfReader(f)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_blocks.append(text)
    return '\n'.join(text_blocks)

def extract_text(path):
    #Entry point for reading files 
    ext = os.path.splitext(path)[1].lower()

    if ext == '.txt':
        return read_txt(path)
    elif ext == '.epub':
        return read_epub(path)
    elif ext == '.fb2':
        return read_fb2(path)
    elif ext == '.pdf':
        return read_pdf(path)
    else:
        raise ValueError(f'Format {ext} not supported')
            

