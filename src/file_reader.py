import re
import os  
import logging 
from ebooklib import epub, ITEM_DOCUMENT 
from bs4 import BeautifulSoup 
from pypdf import PdfReader  
import pytesseract 
from pdf2image import convert_from_path 
from tqdm import tqdm   

logger = logging.getLogger(__name__)

def read_txt(path):
    # Read plain text file using utf-8 encoding
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def read_epub(path):
    # Parse EPUB book and retrieve all items
    book = epub.read_epub(path)
    text_blocks = []
    items = list(book.get_items())
    
    # Iterate through items with a progress bar
    for item in tqdm(items, desc='Reading EPUB'):
        # Extract text only from document items (HTML content)
        if item.get_type() == ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_body_content(), 'html.parser')
            text_blocks.append(soup.get_text(separator='\n', strip=True))

    return '\n'.join(text_blocks)

def read_fb2(path):
    # Parse FB2 file as XML
    with open(path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'lxml-xml')

        text_blocks = []
        # Find all paragraph (<p>) and verse (<v>) elements
        elements = soup.find_all(['p', 'v'])
        for i in tqdm(elements, desc='Reading FB2'):
            text_blocks.append(i.get_text(strip=True))

        return '\n'.join(text_blocks)

def read_pdf(path):
    text_blocks = []
    # Open PDF file in binary read mode
    with open(path, 'rb') as f:
        reader = PdfReader(f)
        total_pages = len(reader.pages)
        
        # Extract existing text layer from pages
        for page in tqdm(reader.pages, desc='Reading PDF (text layer)'):
            text = page.extract_text()
            if text:
                text_blocks.append(text)
    
    extracted_text = '\n'.join(text_blocks)
    
    # Fallback to OCR if the extracted text is suspiciously short (less than 50 chars)
    if len(extracted_text.strip()) < 50:
        logger.info(f'Text layer not found. Starting OCR for {total_pages} pages in chunks')
        ocr_text = []
        chunk_size = 10  # Number of pages to process at once to prevent memory overload
        
        # Process pages in chunks with a unified progress bar
        with tqdm(total=total_pages, desc='OCR: Processing pages') as pbar:
            for start_page in range(1, total_pages + 1, chunk_size):
                end_page = min(start_page + chunk_size - 1, total_pages)
                
                # Convert a specific range of PDF pages to images
                images = convert_from_path(path, first_page=start_page, last_page=end_page)
                
                # Perform OCR on each image
                for img in images:
                    ocr_text.append(pytesseract.image_to_string(img, lang='eng+rus'))
                    pbar.update(1) 
                    
        extracted_text = '\n'.join(ocr_text)

    return extracted_text 

def clean_text(text):
    if not text:
        return ''
    
    # 1. Remove hyphenation at the end of lines
    text = re.sub(r'-\n+', '', text)
    # 2. Merge lines that are part of the same paragraph
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
    # 3. Collapse multiple spaces and tabs into a single space
    text = re.sub(r'[ \t]+', ' ', text)
    
    return text.strip()

def extract_text(path):
    # Entry point: determine file extension and route to the corresponding reader
    ext = os.path.splitext(path)[1].lower()

    if ext == '.txt':
        raw_text = read_txt(path)
    elif ext == '.epub':
        raw_text = read_epub(path)
    elif ext == '.fb2':
        raw_text = read_fb2(path)
    elif ext == '.pdf':
        raw_text = read_pdf(path)
    else:
        raise ValueError(f'Format {ext} not supported')
        
    # Clean the extracted text before returning
    return clean_text(raw_text)
