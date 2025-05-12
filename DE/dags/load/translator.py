import asyncio
from googletrans import Translator
import time
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VietnameseDetector:
    """
    Rule-based Vietnamese language detector.
    """

    def __init__(self):
        # Vietnamese characters pattern
        self.pattern = re.compile(
            r"[ăâđêôơưáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩị"
            r"óòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ]", re.IGNORECASE
        )

    def contains_vietnamese(self, text: str) -> bool:
        """
        Check if the given text contains Vietnamese characters.
        
        :param text: Input text
        :return: True if Vietnamese characters are detected, otherwise False
        """
        return bool(self.pattern.search(text))

class VietnameseTranslator:
    """
    Vietnamese-to-English translation component.
    """

    def __init__(self):
        self.translator = Translator()
        self.detector = VietnameseDetector()

    async def translate_if_vietnamese(self, text: str) -> str:
        """
        Detect and translate Vietnamese text to English.
        If the text doesn't contain Vietnamese, return it unchanged.

        :param text: Input text
        :return: Translated text if Vietnamese detected, otherwise original
        """
      
        if self.detector.contains_vietnamese(text):
            try:
                result = await self._translate_vi_to_en(text)
                return result
            except Exception as e:
                logger.error(f"Error translating text: {e}")
                return text  
        return text

    async def _translate_vi_to_en(self, text: str) -> str:
        """
        Internal method to perform translation using googletrans.
        
        :param text: Vietnamese text
        :return: English translation
        """
        retry_attempts = 3
        delay = 1 
        
        for attempt in range(retry_attempts):
            try:
                translation = await self.translator.translate(text, src="vi", dest="en")
                return translation.text
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retry_attempts - 1:
                    logger.info(f"Retrying after {delay} seconds...")
                    await asyncio.sleep(delay) 
                    delay *= 2  
                else:
                    logger.error(f"Max retry attempts reached for text: {text}")
                    return text

