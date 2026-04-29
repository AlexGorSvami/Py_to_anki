import os
import pytest
from src.anki_exporter import export_to_apkg

def test_export_to_apkg_creates_file(tmp_path):
    # Подготовка данных
    test_cards = [["Apple", "Яблоко"], ["Book", "Книга"]]
    deck_name = "Test Deck"
    # Создаем путь во временной папке pytest
    output_file = tmp_path / "test_deck.apkg"
    
    # Действие
    export_to_apkg(test_cards, deck_name, str(output_file))
    
    # Проверка
    assert output_file.exists(), "Файл .apkg не был создан"
    assert output_file.stat().st_size > 0, "Файл .apkg пустой"

def test_export_to_apkg_handles_special_chars(tmp_path):
    # Проверка на кириллицу и спецсимволы, что важно для изучения языков
    test_cards = [["Wait & See", "Поживем — увидим"]]
    output_file = tmp_path / "special_chars.apkg"
    
    # Ожидаем, что функция не упадет с ошибкой кодировки
    export_to_apkg(test_cards, "Special", str(output_file))
    assert output_file.exists()
