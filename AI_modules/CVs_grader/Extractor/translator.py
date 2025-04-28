import asyncio
from googletrans import Translator

translator = Translator()


async def translate_vi_to_en_async(text: str) -> str:
    """
    Translate Vietnamese text to English using googletrans (v4+).
    This coroutine must be awaited.

    :param text: Input string in Vietnamese.
    :return: Translated string in English.
    """
    translation = await translator.translate(text, src="vi", dest="en")
    return translation.text
