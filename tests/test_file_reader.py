import pytest
from unittest.mock import patch
from src.file_reader import clean_text, extract_text, read_txt

# --- Тесты для очистки текста (clean_text) ---

def test_clean_text_removes_hyphens():
    text = "Py-\nthon"
    assert clean_text(text) == "Python"

def test_clean_text_merges_lines():
    text = "Hello\nWorld"
    assert clean_text(text) == "Hello World"

def test_clean_text_keeps_paragraphs():
    text = "Paragraph 1.\n\nParagraph 2."
    assert clean_text(text) == "Paragraph 1.\n\nParagraph 2."

def test_clean_text_removes_extra_spaces():
    text = "Too   many \t spaces."
    assert clean_text(text) == "Too many spaces."

def test_clean_text_handles_empty():
    assert clean_text("") == ""
    assert clean_text(None) == ""

# --- Тесты для чтения файлов ---

def test_read_txt(tmp_path):
    # Создаем временный файл
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test\nline", encoding="utf-8")
    
    assert read_txt(str(test_file)) == "Test\nline"

# --- Тесты для маршрутизатора форматов (extract_text) ---

@patch('src.file_reader.read_txt')
def test_extract_text_routes_txt(mock_read_txt):
    mock_read_txt.return_value = "Mocked TXT"
    
    result = extract_text("dummy.txt")
    mock_read_txt.assert_called_once_with("dummy.txt")
    assert result == "Mocked TXT"

@patch('src.file_reader.read_epub')
def test_extract_text_routes_epub(mock_read_epub):
    mock_read_epub.return_value = "Mocked EPUB"
    
    extract_text("book.epub")
    mock_read_epub.assert_called_once_with("book.epub")

@patch('src.file_reader.read_pdf')
def test_extract_text_routes_pdf(mock_read_pdf):
    mock_read_pdf.return_value = "Mocked PDF"
    
    extract_text("document.pdf")
    mock_read_pdf.assert_called_once_with("document.pdf")

def test_extract_text_unsupported_format():
    with pytest.raises(ValueError, match="Format .doc not supported"):
        extract_text("file.doc")
