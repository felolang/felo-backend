import datetime
import json
from enum import Enum
from typing import Protocol

from loguru import logger
from openai.types.chat import ChatCompletion
from sqlalchemy.ext.asyncio import AsyncSession

from felo.db.models.lookup import (
    Lookup,
    LookupAnswer,
    LookupPhrases,
    PhrasesTypeEnum,
    TranslateEngineEnum,
)
from felo.schemas.lookup import LangModelResponseSchema
from felo.schemas.translations import TranslationRequest
from felo.utils.api_clients import openai_async_client


class LanguageModelApiAadapter(Protocol):
    async def translate(
        self, prompt: str, translator_request: TranslationRequest
    ) -> dict:
        ...

    def get_engine(self) -> str:
        ...


class OpenaiApiAdapter:
    def __init__(self):
        self.client = openai_async_client
        self.engine = TranslateEngineEnum.GPT_3_5_TURBO_1106

    async def translate(
        self, prompt: str, translator_request: TranslationRequest
    ) -> dict:
        response: ChatCompletion = await self.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": translator_request.model_dump_json(
                        exclude={"id"}, by_alias=True
                    ),
                },
            ],
            seed=100,
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        response_dict = response.model_dump()
        response_content = json.loads(response_dict["choices"][0]["message"]["content"])
        return response_content

    def get_engine(self) -> str:
        return self.engine


class LanguageModelTranslation:
    prompt: str

    def __init__(self, session: AsyncSession, adapter: LanguageModelApiAadapter):
        self.api_adapter = adapter
        self.session = session

    async def load_prompt(self):
        # TODO: make prompt constant
        prompt_path = "felo/endpoints/translator/translator_prompt.txt"
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.prompt = f.read()

    async def translate(
        self, translator_request: TranslationRequest, lookup: Lookup
    ) -> LangModelResponseSchema:
        logger.debug(f"lookup: {lookup.lookup_answers}")

        start = datetime.datetime.now()
        logger.debug(f"Time 1: {datetime.datetime.now() - start}")
        await self.load_prompt()
        logger.debug(f"Time 2: {datetime.datetime.now() - start}")

        logger.debug(f"Time 3: {datetime.datetime.now() - start}")
        response = await self.api_adapter.translate(self.prompt, translator_request)
        logger.debug(f"GPT response: {response}")
        logger.debug(f"GPT response: {response['phrases']}")
        logger.debug(f"Time 4: {datetime.datetime.now() - start}")
        lookup_answer = LookupAnswer(
            text_translation=response["text_translation"],
            normalized_text=response["normalized_text"],
            normalized_text_translation=response["normalized_text_translation"],
            pos=response["pos"],
            # phrases=response["phrases"],
            phrases=[
                LookupPhrases(**phrase)
                for phrase in response["phrases"]
                if phrase["type"] != PhrasesTypeEnum.NOTHING.value
            ],
            engine=self.api_adapter.get_engine(),
        )
        lookup.lookup_answers.append(lookup_answer)
        self.session.add(lookup)
        # phrases = [PhrasesSchema(**phrase._mapping) for phrase in lookup_answer.phrases]
        phrases = lookup_answer.phrases
        # logger.debug(f"phrases {phrases}")
        await self.session.commit()

        return LangModelResponseSchema(
            context_translation=lookup.context_translation,
            source_language=lookup.source_language,
            target_language=lookup.target_language,
            text_translation=lookup_answer.text_translation,
            normalized_text=lookup_answer.normalized_text,
            normalized_text_translation=lookup_answer.normalized_text_translation,
            pos=lookup_answer.pos,
            phrases=phrases,
        )


class LanguageModelEnum(str, Enum):
    OPENAI = "openai"


class FastTranslatorEnum(str, Enum):
    GOOGLE = "google"


API_ADAPTERS: dict[LanguageModelEnum, LanguageModelApiAadapter] = {
    LanguageModelEnum.OPENAI: OpenaiApiAdapter(),
}


async def language_model_translation(
    session: AsyncSession,
    translator_request: TranslationRequest,
    lookup: Lookup,
    language_model: LanguageModelEnum,
) -> LangModelResponseSchema:
    api_adapter = API_ADAPTERS[language_model]
    translator = LanguageModelTranslation(session, api_adapter)
    return await translator.translate(translator_request, lookup)


# async def gpt_translte_stream(
#     translator_request: TranslationRequest,
# ) -> AsyncGeneratorType[str, None]:
#     start = datetime.datetime.now()
#     logger.debug(f"Time 1: {datetime.datetime.now() - start}")
#     prompt_path = "felo/endpoints/translator/translator_prompt.txt"
#     with open(prompt_path, "r", encoding="utf-8") as f:
#         prompt = f.read()
#     logger.debug(f"Time 2: {datetime.datetime.now() - start}")
#     response: ChatCompletion = await openai_async_client.chat.completions.create(
#         model="gpt-3.5-turbo-1106",
#         messages=[
#             {"role": "system", "content": prompt},
#             {"role": "user", "content": translator_request.model_dump_json()},
#         ],
#         seed=42,
#         response_format={"type": "json_object"},
#         stream=True,
#     )

#     all_content = ""
#     async for chunk in response:
#         content = chunk.choices[0].delta.content
#         if content:
#             all_content += content
#             yield all_content
