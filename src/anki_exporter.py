import genanki

# Фиксированные ID гарантируют, что Anki будет обновлять существующую колоду, а не плодить новые
MODEL_ID = 1607392319
DECK_ID = 2059400110

def export_to_apkg(cards, deck_name, output_path):
    """
    Создает файл .apkg из списка карточек.
    :param cards: Список вида [['Вопрос', 'Ответ'], ...]
    :param deck_name: Имя колоды, которое отобразится в Anki
    :param output_path: Путь к итоговому файлу
    """
    model = genanki.Model(
        MODEL_ID, 
        'Simple Model',
        fields=[{'name': 'Front'}, {'name': 'Back'}],
        templates=[{
            'name': 'Card 1',
            'qfmt': '<div style="text-align:center; font-size:20px;">{{Front}}</div>',
            'afmt': '{{FrontSide}}<hr id="answer"><div style="text-align:center; color:blue;">{{Back}}</div>',
        }]
    )

    deck = genanki.Deck(DECK_ID, deck_name)

    for q, a in cards:
        note = genanki.Note(model=model, fields=[str(q), str(a)])
        deck.add_note(note)

    genanki.Package(deck).write_to_file(output_path)
