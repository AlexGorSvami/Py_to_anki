import logging 
from google import genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self):
        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY"),
            http_options={'api_version': 'v1'}
        )
        # First find the model, then we test the connection
        self.model_id = self._find_working_model()

    def _find_working_model(self):
        """Автоматически выбирает лучшую доступную модель из твоего списка"""
        try:
            available_models = []
            for m in self.client.models.list():
                available_models.append(m.name)
            
            # Priority of choice
            priority = [
                'models/gemini-2.0-flash-lite', 
                'models/gemini-2.0-flash',
                'models/gemini-1.5-flash'
            ]
            
            for target in priority:
                if target in available_models:
                    logger.info(f"Используем модель: {target}")
                    return target
            
            # If we didn't find anything, we take the first availible one
            logger.warning(f"Приоритетные модели не найдены, берем: {available_models[0]}")
            return available_models[0]
            
        except Exception as err:
            logger.error(f'Failed to get list of models: {err}')
            return 'models/gemini-2.0-flash-lite' # Фолбэк

    def generate_cards(self, text):
        prompt = f"""Составь Anki-карточки (вопрос;ответ) по тексту Python. 
        Верни ТОЛЬКО JSON список объектов [{{ "question": "...", "answer": "..." }}]. 
        Текст: {text}"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id, 
                contents=prompt
            )
            
            content = response.text.strip()
            start = content.find('[')
            end = content.rfind(']') + 1
            
            if start == -1: return []
            return json.loads(content[start:end])
        except Exception as e:
            logger.error(f"Error generation in {self.model_id}: {e}")
            raise e
