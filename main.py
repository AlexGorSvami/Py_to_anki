import asyncio
import os
import json
import logging
from tqdm.asyncio import tqdm

from src.file_reader import extract_text 
from src.api_client import DeepSeekClient 
from src.file_handler import save_to_csv 
from src.anki_exporter import export_to_apkg 

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

async def process_chunk(client, chunk, i, total, output_file, cache_file, processed_ind, sem, lock):
    """Асинхронная обработка одного куска текста с возвратом результата"""
    async with sem:
        # Если блок уже обработан, возвращаем пустой список
        if i in processed_ind:
            logger.info(f'[-] Block {i}/{total} skipped (cached)')
            return [] 
            
        try:
            # Асинхронно ждем ответ от API
            cards = await client.generate_cards(chunk)
            
            if cards:
                # Синхронная запись в CSV через поток (thread) для безопасности
                async with lock:
                    await asyncio.to_thread(save_to_csv, cards, output_file) 
                    
                    # Обновляем кэш
                    processed_ind.append(i)
                    with open(cache_file, 'w') as f:
                        json.dump(processed_ind, f)
                
                logger.info(f'[+] Block {i}/{total} processed and saved to {output_file}.')
                
                # Небольшая пауза, чтобы соблюдать лимиты API
                await asyncio.sleep(1) 
                
                # ВАЖНО: возвращаем список карточек для дальнейшей упаковки в .apkg
                return cards
                
        except Exception as err:
            logger.error(f'[!] Error processing block {i}: {err}')
            
    # Если карточек нет или произошла ошибка, возвращаем пустой список
    return []

async def main_async():
    path = input('Please, enter the book path: ').strip()
    user_filename = input('Enter output file_name(Enter for auto-naming): ').strip()
    base_name = os.path.splitext(os.path.basename(path))[0]
     
    if not user_filename:
       output_file = f"{base_name}.csv"
    else:
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
    lock = asyncio.Lock() #Create blocking
    
    # Создаем список задач
    tasks = []
    for i, chunk in enumerate(chunks, 1):
        task = process_chunk(client, chunk, i, len(chunks), output_file, cache_file, processed_ind, sem, lock)
        tasks.append(task)

    results= await tqdm.gather(*tasks, desc='Обработка блоков')

    all_cards = []
    for chunk_result in results:
        if chunk_result:
            all_cards.extend(chunk_result)

    if all_cards:
        anki_output = output_file.replace('.csv', '.apkg')
        try:
            export_to_apkg(all_cards, base_name, anki_output) 
            logger.info(f'[#] Success! Create Anki deck: {anki_output} ({len(all_cards)} pieces.)')
        except Exception as e:
            logger.error(f'[!] Error while creating .apkg: {e}')
    else:
         logger.warning('No cards were created. Export to Anki was skipped.')


if __name__ == '__main__':
    asyncio.run(main_async())
