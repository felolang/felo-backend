import json

from loguru import logger
from openai.types.chat import ChatCompletion

from felo.db.models.lookup import TranslateEngineEnum
from felo.endpoints.translator.prompt import (
    extract_phrases_prompt,
    extract_phrases_prompt_examples,
    prompt,
    prompt_examples,
)
from felo.schemas.translations import TranslationRequest
from felo.utils.api_clients import openai_async_client
from felo.utils.structures import flatten


class OpenaiApiAdapter:
    def __init__(self):
        self.client = openai_async_client
        self.engine = TranslateEngineEnum.GPT_3_5_TURBO_1106

    async def extract_phrases(self, translator_request: TranslationRequest) -> dict:
        logger.debug(f"translator_request: {translator_request}")
        examples: list[tuple] = [
            (
                {
                    "role": "user",
                    "content": extract_phrases_prompt.format(
                        text=question.text,
                        context=question.context,
                        source_language=question.source_language,
                        target_language=question.target_language,
                    ),
                },
                {
                    "role": "assistant",
                    "content": answer.model_dump_json(),
                },
            )
            for question, answer in extract_phrases_prompt_examples
        ]
        messages = [
            *flatten(examples),
            {
                "role": "user",
                "content": extract_phrases_prompt.format(
                    text=translator_request.text,
                    context=translator_request.context,
                    source_language=translator_request.source_language.value,
                    target_language=translator_request.target_language.value,
                ),
            },
        ]
        # logger.debug(f"messages: {messages}")

        response: ChatCompletion = await self.client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=messages,
            seed=100,
            response_format={"type": "json_object"},
            temperature=0,
        )
        response_dict = response.model_dump()
        response_content = json.loads(response_dict["choices"][0]["message"]["content"])
        return response_content["phrases"]

    async def translate(self, translator_request: TranslationRequest) -> dict:
        logger.debug(f"translator_request: {translator_request}")
        examples: list[tuple] = [
            (
                {
                    "role": "user",
                    "content": prompt.format(
                        text=question.text,
                        context=question.context,
                        source_language=question.source_language,
                        target_language=question.target_language,
                    ),
                },
                {
                    "role": "assistant",
                    "content": answer.model_dump_json(),
                },
            )
            for question, answer in prompt_examples
        ]
        messages = [
            *flatten(examples),
            {
                "role": "user",
                "content": prompt.format(
                    text=translator_request.text,
                    context=translator_request.context,
                    source_language=translator_request.source_language.value,
                    target_language=translator_request.target_language.value,
                ),
            },
        ]
        logger.debug(f"messages: {messages}")

        response: ChatCompletion = await self.client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=messages,
            seed=100,
            response_format={"type": "json_object"},
            temperature=0,
        )
        response_dict = response.model_dump()
        response_content = json.loads(response_dict["choices"][0]["message"]["content"])
        return response_content

    def get_engine(self) -> str:
        return self.engine
