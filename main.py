import logging 
import time 
from src.api_client import DeepSeekClient 
from src.file_handler import save_to_csv 

# Logging settings
logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler('project.log'), #Logs saves in this file 
            logging.StreamHandler()
        ]
)
logger = logging.getLogger(__name__)

def main():
    input_file = '/home/alex/Documents/Python/Справочники/Лутц Марк - Python. Карманный справочник - 2015.pdf.txt'

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        logger.error(f'File not found: {input_file}')
        return 
    
    chunk_size = 5000 
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    logger.info(f'Begin processing {len(chunks)} blocks...')
    
    client = DeepSeekClient()

    #Processing cycle
    for i, chunk in enumerate(chunks, 1):
        try:
            cards = client.generate_cards(chunk)
            if cards:
                save_to_csv(cards)
                logger.info(f'[+] Block {i}/{len(chunks)} is ready.')
            time.sleep(5) # small pause for stability 
        except Exception as err:
            logger.error(f'[!] Error for block {i}: {err}')
            logger.info('[~] Waiting 60 seconds before retry')
            time.sleep(60)

if __name__ == '__main__':
    main()
