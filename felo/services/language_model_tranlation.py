import asyncio
import datetime
import json
import re
import string
from ast import List
from enum import Enum
from typing import Iterable, Optional, Protocol

import inflect
import nltk
from loguru import logger
from nltk import word_tokenize
from nltk.stem import PorterStemmer
from openai.types.chat import ChatCompletion
from sqlalchemy.ext.asyncio import AsyncSession

from felo.db.models.lookup import (
    Lookup,
    LookupAnswer,
    LookupPhrases,
    PhrasesTypeEnum,
    TranslateEngineEnum,
)
from felo.endpoints.translator.prompt import (
    extract_phrases_prompt,
    extract_phrases_prompt_examples,
    prompt,
    prompt_examples,
)
from felo.schemas.cards import (
    Card,
    CardTypesEnum,
    Explanation,
    NormalizedVersion,
    PossibleTranslation,
)
from felo.schemas.lookup import LangModelResponseSchema
from felo.schemas.translations import (
    PhraseExtractionRequestToLM,
    TranslationRequest,
    TranslationRequestToLM,
)
from felo.utils.api_clients import openai_async_client

nltk.download("punkt")
stemmer = PorterStemmer()


p = inflect.engine()


def substr_occurances(whole_str, sub_str, sub_str_start_pos):
    logger.debug(f"csubstr_occurancesou, {whole_str}, {sub_str}, {sub_str_start_pos}")
    count = 0
    index = 0

    while index != -1:
        index = whole_str.find(sub_str, index)
        if index == sub_str_start_pos:
            return count + 1
        if index != -1:
            count += 1
            index += 1


class LanguageModelApiAadapter(Protocol):
    async def translate(self, translator_request: TranslationRequestToLM) -> dict:
        ...

    async def extract_phrases(
        self, translator_request: PhraseExtractionRequestToLM
    ) -> dict:
        ...

    def get_engine(self) -> str:
        ...


def flatten(xss):
    return [x for xs in xss for x in xs]


class OpenaiApiAdapter:
    def __init__(self):
        self.client = openai_async_client
        self.engine = TranslateEngineEnum.GPT_3_5_TURBO_1106

    async def extract_phrases(
        self, translator_request: PhraseExtractionRequestToLM
    ) -> dict:
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

    async def translate(self, translator_request: TranslationRequestToLM) -> dict:
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
                        order=p.ordinal(1),
                    ),
                },
                {
                    "role": "assistant",
                    "content": answer.model_dump_json(),
                },
            )
            for question, answer in prompt_examples
        ]
        # examples = [*e for e in examples]
        # builded_prompt = prompt.format(
        #     source_language=translator_request.source_language.value,
        #     target_language=translator_request.target_language.value,
        #     text=translator_request.text,
        #     context=translator_request.context,
        #     occurance=p.ordinal(
        #         substr_occurances(
        #             translator_request.context,
        #             translator_request.text,
        #             translator_request.start_position,
        #         )
        #     ),
        # )
        ordinal = substr_occurances(
            translator_request.context,
            translator_request.text,
            translator_request.start_position,
        )
        logger.debug(f"ordinal {ordinal}")
        messages = [
            *flatten(examples),
            {
                "role": "user",
                "content": prompt.format(
                    text=translator_request.text,
                    context=translator_request.context,
                    source_language=translator_request.source_language.value,
                    target_language=translator_request.target_language.value,
                    # order=p.ordinal(ordinal),
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

    def _get_normilized(
        self, normilized_text: str, normilized_text_translation: list
    ) -> Optional[NormalizedVersion]:
        if normilized_text is None:
            return None
        return NormalizedVersion(
            normalized_text=normilized_text,
            normilized_text_translation=normilized_text_translation,
        )

    def _get_explanation(
        self, explanation: str, explanation_translation: str
    ) -> Optional[Explanation]:
        if explanation is None:
            return None
        return Explanation(
            explanation=explanation,
            explanation_translation=explanation_translation,
        )

    def _lang_model_answer_to_cards(
        self, sourse_text: str, lang_model_answer: LookupAnswer
    ) -> list[Card]:
        cards = []
        main_card = Card(
            id=lang_model_answer.id,
            text=lang_model_answer.extended_text or sourse_text,
            text_translation=lang_model_answer.text_translation,
            normilized=self._get_normilized(
                lang_model_answer.normalized_text,
                lang_model_answer.normalized_text_translation,
            ),
            card_type=CardTypesEnum.SOURCE,
        )
        cards.append(main_card)

        for phrase in lang_model_answer.phrases:
            cards.append(
                Card(
                    id=phrase.id,
                    text=phrase.phrase_text,
                    text_translation=[
                        {
                            "translation": phrase.phrase_text_translation,
                            "pos": None,
                        }
                    ],
                    card_type=CardTypesEnum(phrase.type),
                    normilized=self._get_normilized(
                        phrase.phrase_normalized_text,
                        [
                            {
                                "translation": phrase.phrase_normalized_text_translation,
                                "pos": None,
                            }
                        ],
                    ),
                    explanation=self._get_explanation(
                        phrase.explanation, phrase.explanation_translation
                    ),
                )
            )
        return cards

    def _filter_cards(self, cards: list[Card]) -> list[Card]:
        main_card = cards[0]
        other_cards = cards[1:]
        for card in other_cards:
            if card.text == main_card.text:
                return cards[1:]
        return cards

    async def translate(
        self, translator_request: TranslationRequestToLM, lookup: Lookup
    ) -> list[Card]:
        # logger.debug(f"lookup: {lookup.lookup_answers}")

        # start = datetime.datetime.now()
        # logger.debug(f"Time 1: {datetime.datetime.now() - start}")
        # await self.load_prompt()
        # logger.debug(f"Time 2: {datetime.datetime.now() - start}")

        # logger.debug(f"Time 3: {datetime.datetime.now() - start}")
        # response = await self.api_adapter.translate(translator_request)
        # logger.debug(f"GPT response: {response}")
        # logger.debug(f"GPT response: {response['phrases']}")
        # logger.debug(f"Time 4: {datetime.datetime.now() - start}")
        # lookup_answer = LookupAnswer(
        #     text_translation=response["text_translation"],
        #     normalized_text=response["normalized_text"],
        #     normalized_text_translation=response["normalized_text_translation"],
        #     # phrases=response["phrases"],
        #     phrases=[LookupPhrases(**phrase) for phrase in response["phrases"]],
        #     engine=self.api_adapter.get_engine(),
        #     extended_text=response["extended_text"],
        # )
        # lookup.lookup_answers.append(lookup_answer)
        # self.session.add(lookup)
        # phrases = [PhrasesSchema(**phrase._mapping) for phrase in lookup_answer.phrases]
        # phrases = lookup_answer.phrases
        # logger.debug(f"phrases {phrases}")
        # await self.session.commit()

        # cards = self._lang_model_answer_to_cards(lookup.text, lookup_answer)
        # cards = self._filter_cards(cards)
        translate_coroutine = self.api_adapter.translate(translator_request)
        extract_coroutine = self.api_adapter.extract_phrases(
            PhraseExtractionRequestToLM(
                lookup_id=translator_request.id,
                context=translator_request.context,
                source_language=translator_request.source_language,
                target_language=translator_request.target_language,
                text=translator_request.text,
            )
        )
        [translate_response, extract_response] = await asyncio.gather(
            translate_coroutine, extract_coroutine
        )
        logger.debug(f"translate_response: {translate_response}")
        logger.debug(f"extract_response: {extract_response}")

        source_card = Card(
            text=translator_request.text,
            card_type=CardTypesEnum.SOURCE,
            text_translation=[
                PossibleTranslation(
                    pos=None,
                    translation=translation,
                )
                for translation in set(translate_response["translations"])
            ],
            # explanation=Explanation(
            #     explanation_translation=response["idiom_explanation"]
            # ),
            # grammar=response["grammar"],
        )

        extracted_phrases = [
            Card(
                text=r["phrase_text"],
                card_type=r["phrase_type"],
                text_translation=[
                    PossibleTranslation(
                        pos=None,
                        translation=translation,
                    )
                    for translation in set(r["translations"])
                ],
                explanation=Explanation(explanation_translation=r["explanation"]),
            )
            for r in extract_response
            if "phrase_type" in r and r["phrase_type"] in CardTypesEnum._member_names_
        ]
        filtered_phrases: List[Card] = []

        for phrase in extracted_phrases:
            # if phrase.card_type.value not in CardTypesEnum._member_names_:
            #     continue
            if phrase.card_type in [
                CardTypesEnum.NOTHING,
                # CardTypesEnum.ORDINARY_PHRASE,
            ]:
                continue
            if (
                phrase.card_type == CardTypesEnum.PHRASAL_VERB
                and len(phrase.text.split()) < 2
            ):
                continue
            if (
                phrase.text not in source_card.text
                and source_card.text not in phrase.text
            ):
                continue
            filtered_phrases.append(phrase)

        # filter 1
        if any(
            True if source_card.text in phrase.text else False
            for phrase in filtered_phrases
        ):
            cards = filtered_phrases
        else:
            cards = [source_card, *filtered_phrases]

        # filter 2
        NEED_EXPLANATION = [
            CardTypesEnum.IDIOM,
            CardTypesEnum.SLANG,
            CardTypesEnum.TERM,
        ]
        for card in cards:
            if card.card_type not in NEED_EXPLANATION:
                card.explanation = None

        return cards


class LanguageModelEnum(str, Enum):
    OPENAI = "openai"


class FastTranslatorEnum(str, Enum):
    GOOGLE = "google"


API_ADAPTERS: dict[LanguageModelEnum, LanguageModelApiAadapter] = {
    LanguageModelEnum.OPENAI: OpenaiApiAdapter(),
}

# def preprocess_translor_request(
#     translator_request: TranslationRequest,
# ) -> TranslationRequest:


class PreprocessingPipeline:
    def __init__(self) -> None:
        self.pipeline = [self.shorter_context]

    def process(
        self, translator_request: TranslationRequestToLM
    ) -> TranslationRequestToLM:
        for item in self.pipeline:
            translator_request = item(translator_request)
        return translator_request

    def rm_characters(
        self, translator_request: TranslationRequestToLM
    ) -> TranslationRequestToLM:
        characters_to_rm = "\n|\t"
        translator_request.context = re.sub(
            characters_to_rm, "", translator_request.context
        )
        translator_request.text = re.sub(characters_to_rm, "", translator_request.text)
        return translator_request

    def shorter_context(
        self, translator_request: TranslationRequestToLM
    ) -> TranslationRequestToLM:
        if len(translator_request.text.split(" ")) != 1:
            return translator_request

        stem_text = stemmer.stem(translator_request.text, to_lowercase=False)

        # n_token = 0
        # for i, c in enumerate(translator_request.context):
        #     if i == translator_request.start_position:
        #         break
        #     if c == " ":
        #         n_token += 1

        occurances = [
            m.start() for m in re.finditer(stem_text, translator_request.context)
        ]
        try:
            assert translator_request.start_position in occurances
        except AssertionError:
            logger.warning(f"stem: {stem_text}. context: {translator_request.context}")
            return translator_request
        if len(occurances) == 1:
            return translator_request

        left_border = 0
        right_border = len(translator_request.context)
        for occurance in occurances:
            if occurance < translator_request.start_position:
                left_border = translator_request.context.find(" ", occurance)
            elif occurance > translator_request.start_position:
                right_border = occurance
                break
        translator_request.context = translator_request.context[
            left_border:right_border
        ]
        return translator_request


async def language_model_translation(
    session: AsyncSession,
    translator_request: TranslationRequest,
    lookup: Lookup,
    language_model: LanguageModelEnum,
) -> list[Card]:
    api_adapter = API_ADAPTERS[language_model]
    lm_request = TranslationRequestToLM.from_translation_request(translator_request)
    pipeline = PreprocessingPipeline()

    lm_request = pipeline.process(lm_request)
    logger.debug(f"lm_request after pipeline {lm_request}")
    translator = LanguageModelTranslation(session, api_adapter)
    return await translator.translate(lm_request, lookup)


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
