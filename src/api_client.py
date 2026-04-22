import os
import json
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class DeepSeekClient:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        # DeepSeek использует базовый URL для совместимости с OpenAI
        self.client = OpenAI(
            api_key=self.api_key, 
            base_url="https://api.deepseek.com"
        )
        # Основная модель для чата и кодинга
        self.model_id = "deepseek-chat" 

    def generate_cards(self, text):
        prompt = f"""
        Составь Anki-карточки (вопрос;ответ) по тексту Python.
        Верни ТОЛЬКО чистый JSON список объектов [{{ "question": "...", "answer": "..." }}].
        Текст: {text}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that outputs only JSON."},
                    {"role": "user", "content": prompt},
                ],
                stream=False
            )
            
            content = response.choices[0].message.content.strip()
            
            # Очистка ответа от Markdown-оберток ```json ... ```
            start = content.find('[')
            end = content.rfind(']') + 1
            
            if start == -1:
                logger.warning("JSON not found in response")
                return []
                
            return json.loads(content[start:end])
            
        except Exception as e:
            logger.error(f"DeepSeek Error: {e}")
            raise e
