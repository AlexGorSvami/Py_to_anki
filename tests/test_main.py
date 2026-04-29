import pytest
from unittest.mock import AsyncMock, MagicMock
from main import process_chunk

@pytest.mark.asyncio
async def test_process_chunk_returns_cards():
    # Мокаем (подменяем) API клиент
    mock_client = MagicMock()
    # Эмулируем успешный ответ от DeepSeek
    mock_client.generate_cards = AsyncMock(return_value=[["Hello", "Привет"]])
    
    # Мокаем семафор и лок (чтобы не создавать реальные объекты синхронизации)
    sem = MagicMock()
    lock = MagicMock()
    
    # Настраиваем контекстные менеджеры для моков (чтобы работало 'async with')
    sem.__aenter__ = AsyncMock()
    sem.__aexit__ = AsyncMock()
    lock.__aenter__ = AsyncMock()
    lock.__aexit__ = AsyncMock()

    # Запускаем тест функции
    result = await process_chunk(
        client=mock_client,
        chunk="test text",
        i=1,
        total=1,
        output_file="test.csv",
        cache_file="test_cache.json",
        processed_ind=[],
        sem=sem,
        lock=lock
    )
    
    # Проверяем, что функция вернула именно те карточки, которые дал API
    assert result == [["Hello", "Привет"]]
    # Проверяем, что вызов API вообще был
    mock_client.generate_cards.assert_called_once()

@pytest.mark.asyncio
async def test_process_chunk_handles_error():
    # Проверка поведения при ошибке API
    mock_client = MagicMock()
    mock_client.generate_cards = AsyncMock(side_effect=Exception("API Error"))
    
    sem = MagicMock()
    lock = MagicMock()
    sem.__aenter__ = AsyncMock()
    sem.__aexit__ = AsyncMock()

    result = await process_chunk(
        mock_client, "text", 1, 1, "out.csv", "cache.json", [], sem, lock
    )
    
    # Функция не должна падать, она должна вернуть пустой список
    assert result == []
