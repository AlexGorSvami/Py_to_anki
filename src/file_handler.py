import csv 

def save_to_csv(cards, filename='python-anki.csv'):
    with open(filename, mode='a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        for card in cards:
            if card.get('question') and card.get('answer'):
                writer.writerow([card['question'], card['answer']])


