import logging 
import time
import os
import json
from src.file_reader import extract_text 
from src.api_client import DeepSeekClient 
from src.file_handler import save_to_csv 

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('project.log'), # Save logs to this file
        logging.StreamHandler() # Output logs to console
    ]
)
logger = logging.getLogger(__name__)

def main():
    # Get the path to the source file
    path = input('Please, enter the book path: ').strip()
    # Get the output filename from user
    user_filename = input('Enter output filename (Enter for auto-naming): ').strip()
    # Logic for determining the final CSV filename
    if not user_filename:
        # Generate name based on the book title
        base_name = os.path.splitext(os.path.basename(path))[0]
        output_file = f"{base_name}.csv"
    else:
        # Ensure the filename has .csv extension
        base_name = os.path.splitext(os.path.basename(path))[0]
        output_file = user_filename if user_filename.endswith('.csv') else f"{user_filename}.csv"
        
    cache_file = f'{base_name}_progress.json' #Cache file 

    try:
        # Extract text from the source file
        raw_text = extract_text(path)
        logger.info(f'Successfully read {len(raw_text)} symbols from {path}')
    except Exception as e:
        logger.error(f'Failed to read file: {e}')
        return # Stop execution if file reading fails

    # Split text into chunks for API processing
    chunk_size = 5000 
    chunks = [raw_text[i:i+chunk_size] for i in range(0, len(raw_text), chunk_size)]

    logger.info(f'Begin processing {len(chunks)} blocks. Output: {output_file}')
    
    client = DeepSeekClient()
    #Load progress if there is 
    processed_ind = []
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            processed_ind = json.load(f)
            logger.info(f'Resuming from cache. {len(processed_ind)} block already done.')

    # Main processing loop
    for i, chunk in enumerate(chunks, 1):
        if i in processed_ind:
            logger.info(f'[-] Block {i}/{len(chunks)} skipped (cached)')
            continue 
        try:
            # Generate Anki cards via API
            cards = client.generate_cards(chunk)
            if cards:
                # Save generated cards to the determined CSV file
                # Assuming save_to_csv accepts (data, filename)
                save_to_csv(cards, output_file) 
                logger.info(f'[+] Block {i}/{len(chunks)} processed and saved to {output_file}.')
                #We update the cache after each Successfull block 
                processed_ind.append(i)
                with open(cache_file, 'w') as f:
                    json.dump(processed_ind, f)
            # Rate limiting pause
            time.sleep(5) 
        except Exception as err:
            logger.error(f'[!] Error processing block {i}: {err}')
            logger.info('[~] Waiting 60 seconds before retry...')
            time.sleep(60)

if __name__ == '__main__':
    main()
