from google.cloud import translate_v3
from openai import AsyncOpenAI

google_translator_client = translate_v3.TranslationServiceAsyncClient()
openai_async_client = AsyncOpenAI()
