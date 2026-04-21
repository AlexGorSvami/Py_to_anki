import time 
from src.api_client import GeminiClient 
from src.file_handler import save_to_csv 

def main():
    client = GeminiClient()
    input_file = '/home/alex/Documents/Python/Справочники/Лутц Марк - Python. Карманный справочник - 2015.pdf.txt'

    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    chunk_size = 5000 
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    # Start with last stop 
    for i, chunk in enumerate(chunks, 1):
        try:
            cards = client.generate_cards(chunk)
            if cards:
                save_to_csv(cards)
                print(f'[+] Block {i} is ready.')
            time.sleep(5) # small pause for stability 
        except Exception as err:
            print(f'[!] Error for block {i}: {err}')
            print('[~] Waiting 60 seconds after repeat')
            time.sleep(60)

if __name__ == '__main__':
    main()
