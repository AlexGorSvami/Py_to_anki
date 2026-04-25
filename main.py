import asyncio
import os
import json
import logging
from src.file_reader import extract_text 
from src.api_client import DeepSeekClient 
from src.file_handler import save_to_csv 

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('project.log'), 
        logging.StreamHandler() 
    ]
)
logger = logging.getLogger(__name__)

async def process_chunk(client, chunk, i, total, output_file, cache_file, processed_ind, sem):
    """Асинхронная обработка одного куска текста"""
    async with sem:
        if i in processed_ind:
            logger.info(f'[-] Block {i}/{total} skipped (cached)')
            return 
            
        try:
            # Асинхронно ждем ответ от API
            cards = await client.generate_cards(chunk)
            
            if cards:
                # Отправляем быструю синхронную запись в отдельный поток, чтобы не блокировать цикл
                await asyncio.to_thread(save_to_csv, cards, output_file) 
                logger.info(f'[+] Block {i}/{total} processed and saved to {output_file}.')
                
                # Обновляем кэш
                processed_ind.append(i)
                # Быстрая файловая операция, можно оставить синхронной
                with open(cache_file, 'w') as f:
                    json.dump(processed_ind, f)
                    
            # Небольшая пауза, чтобы не спамить API одновременно сотней запросов
            await asyncio.sleep(1) 
            
        except Exception as err:
            logger.error(f'[!] Error processing block {i}: {err}')

async def main_async():
    path = input('Please, enter the book path: ').strip()
    user_filename = input('Enter output filename (Enter for auto-naming): ').strip()
    
    if not user_filename:
        base_name = os.path.splitext(os.path.basename(path))[0]
        output_file = f"{base_name}.csv"
    else:
        base_name = os.path.splitext(os.path.basename(path))[0]
        output_file = user_filename if user_filename.endswith('.csv') else f"{user_filename}.csv"
        
    cache_file = f'{base_name}_progress.json'

    try:
        raw_text = extract_text(path)
        logger.info(f'Successfully read {len(raw_text)} symbols from {path}')
    except Exception as e:
        logger.error(f'Failed to read file: {e}')
        return 

    chunk_size = 5000 
    chunks = [raw_text[i:i+chunk_size] for i in range(0, len(raw_text), chunk_size)]

    logger.info(f'Begin processing {len(chunks)} blocks. Output: {output_file}')
    
    client = DeepSeekClient()
    
    processed_ind = []
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            processed_ind = json.load(f)
            logger.info(f'Resuming from cache. {len(processed_ind)} block already done.')

    # Семафор ограничивает количество ОДНОВРЕМЕННЫХ запросов к API. 
    # Ставим 5, чтобы не нарваться на ошибку 429 (Rate Limit).
    sem = asyncio.Semaphore(5)
    
    # Создаем список задач
    tasks = []
    for i, chunk in enumerate(chunks, 1):
        task = process_chunk(client, chunk, i, len(chunks), output_file, cache_file, processed_ind, sem)
        tasks.append(task)
        
    # Запускаем все задачи параллельно
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    # Точка входа в асинхронную программу
    asyncio.run(main_async())
