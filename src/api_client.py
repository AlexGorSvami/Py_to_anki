import google.generativeai as genai 
import os 
import json 
from dotenv import load_dotenv 

load_dotenv()

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        #Принудительно используем 1.5-flash из-за высоких лимитов
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_cards(self, text):
        prompt = f'''
        Составь Anki-карточки (вопрос;ответ) по тексту Python.
        Верни ТОЛЬКО чистый JSON список объектов.
        Пример: [{{ "question": "...", "answer": "..." }}]
        Текст: {text}
        '''
        response = self.model.generate_content(prompt)
        content = response.text.strip()

        #Parsing json
        start = content.find('[')
        end = content.rfind(']') + 1 
        return json.loads(content[start:end])




