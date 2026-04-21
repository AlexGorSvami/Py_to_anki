from google import genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    def __init__(self):
        # Use new SDK google-genai
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_id = 'gemini-1.5-flash'

    def generate_cards(self, text):
        prompt = f"""
        Составь Anki-карточки (вопрос;ответ) по тексту Python.
        Верни ТОЛЬКО чистый JSON список объектов.
        Пример: [{{ "question": "...", "answer": "..." }}]
        Текст: {text}
        """
        
        response = self.client.models.generate_content(
            model=self.model_id, 
            contents=prompt
        )
        
        content = response.text.strip()
        
        # Clearing the response of possible ```json ... ```
        start = content.find('[')
        end = content.rfind(']') + 1
        
        if start == -1:
            return []
            
        return json.loads(content[start:end])
