import re

import nltk
from loguru import logger
from nltk.stem import PorterStemmer

nltk.download("punkt")
stemmer = PorterStemmer()
from felo.schemas.translations import LanguageModelEnum, TranslationRequest

PUNCTUATION_SET = " !\"#$%&'()*+,./:;<=>?@[\\]^_`{|}~"


def preprocess_chars(translator_request: TranslationRequest) -> TranslationRequest:
    """Заменяем странные пробелы на нормальные"""
    translator_request.context = translator_request.context.replace("\xa0", " ")
    return translator_request


def extend_to_whole_words(translator_request: TranslationRequest) -> TranslationRequest:
    """Расширяем выбранный текст до полных слов"""
    real_start_position = translator_request.text_start_position
    if translator_request.context[real_start_position] not in PUNCTUATION_SET:
        while real_start_position != 0:
            if translator_request.context[real_start_position] not in PUNCTUATION_SET:
                real_start_position -= 1
            else:
                real_start_position += 1
                break

    real_end_position = translator_request.text_start_position + (
        len(translator_request.text) - 1
    )
    if translator_request.context[real_end_position] not in PUNCTUATION_SET:
        while real_end_position != len(translator_request.context):
            if translator_request.context[real_end_position] not in PUNCTUATION_SET:
                real_end_position += 1
            else:
                real_end_position -= 1
                break

    translator_request.text = translator_request.context[
        real_start_position : real_end_position + 1
    ]
    return translator_request


def shorter_context(translator_request: TranslationRequest) -> TranslationRequest:
    """С окращаем контекст при одинаковых корнях для правильного перевода"""

    if len(translator_request.text.split(" ")) != 1:
        return translator_request

    stem_text = stemmer.stem(translator_request.text, to_lowercase=False)

    occurances = [m.start() for m in re.finditer(stem_text, translator_request.context)]
    try:
        assert translator_request.text_start_position in occurances
    except AssertionError:
        logger.warning(f"stem: {stem_text}. context: {translator_request.context}")
        return translator_request
    if len(occurances) == 1:
        return translator_request

    left_border = 0
    right_border = len(translator_request.context)
    for occurance in occurances:
        if occurance < translator_request.text_start_position:
            left_border = translator_request.context.find(" ", occurance)
        elif occurance > translator_request.text_start_position:
            right_border = occurance
            break
    translator_request.context = translator_request.context[left_border:right_border]
    return translator_request


pipelines = {
    LanguageModelEnum.OPENAI: [
        preprocess_chars,
        extend_to_whole_words,
        shorter_context,
    ],
    LanguageModelEnum.ADHOC_OPENAI: [],
}


def preprocess(
    processing_type: LanguageModelEnum, translation_request: TranslationRequest
):
    for func in pipelines[processing_type]:
        translation_request = func(translation_request)
    return translation_request
