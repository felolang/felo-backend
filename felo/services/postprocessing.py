from typing import List, Optional

import spacy
from loguru import logger

from felo.schemas.cards import Card, CardTypesEnum

# Load the 'en_core_web_sm' model
nlp = spacy.load("en_core_web_sm")

NEED_EXPLANATION = [
    CardTypesEnum.IDIOM,
    CardTypesEnum.SLANG,
    CardTypesEnum.TERM,
]


class PostprocessingPipeline:
    def __init__(self) -> None:
        self.pipeline = [
            self._filter_extracted_phrases,
            self._filter_source_card,
            self._clear_explanation,
            self._remove_unnecessary_normalization,
        ]

    def _filter_extracted_phrases(
        self, source_translation: Optional[Card], extracted_phrases: list[Card]
    ) -> tuple[Optional[Card], list[Card]]:
        """Убираем лишние extracted_phrases карточки"""
        filtered_phrases: List[Card] = []

        for phrase in extracted_phrases:
            if phrase.card_type in [
                CardTypesEnum.NOTHING,
            ]:  # Убираем если пустой тип карточки
                continue
            if (
                phrase.card_type == CardTypesEnum.PHRASAL_VERB
            ):  # TODO: сделать проверку на фразовый глагол
                doc = nlp(phrase.text)
                # if len(pos_tags) != 2:
                # continue
                pos_list = [token.pos_ for token in doc]
                logger.debug(f"pos_tags {pos_list}")
                try:
                    assert "VERB" in pos_list
                    phrasal_verb_second_pos = None
                    if "ADP" in pos_list:
                        phrasal_verb_second_pos = "ADP"
                    if "PRT" in pos_list:
                        phrasal_verb_second_pos = "PRT"
                    assert phrasal_verb_second_pos is not None
                    assert pos_list.index("VERB") < pos_list.index(
                        phrasal_verb_second_pos
                    )
                except AssertionError:
                    phrase.card_type = CardTypesEnum.EXPRESSION

            if (
                phrase.text not in source_translation.text
                and source_translation.text not in phrase.text
            ):  # Убираем если фраза не осносится к изначально выделенному куску
                continue
            filtered_phrases.append(phrase)
        return source_translation, filtered_phrases

    def _filter_source_card(
        self, source_translation: Optional[Card], extracted_phrases: list[Card]
    ) -> tuple[Optional[Card], list[Card]]:
        """Убираем source карточку, если ее текст полностью содержится в какой-либо другой карточке"""
        if any(
            True if source_translation.text in phrase.text else False
            for phrase in extracted_phrases
        ):
            return None, extracted_phrases
        else:
            return source_translation, extracted_phrases

    def _clear_explanation(
        self, source_translation: Optional[Card], extracted_phrases: list[Card]
    ) -> tuple[Optional[Card], list[Card]]:
        for card in extracted_phrases:
            if card.card_type not in NEED_EXPLANATION:
                card.explanation = None
        return source_translation, extracted_phrases

    def _remove_unnecessary_normalization(
        self, source_translation: Optional[Card], extracted_phrases: list[Card]
    ) -> tuple[Optional[Card], list[Card]]:
        if (
            source_translation
            and source_translation.normilized
            and source_translation.normilized.normalized_text == source_translation.text
        ):
            source_translation.normilized = None

        for card in extracted_phrases:
            if card.normilized and card.normilized.normalized_text == card.text:
                card.normilized = None
        return source_translation, extracted_phrases

    def process(
        self, source_translation: Optional[Card], extracted_phrases: list[Card]
    ) -> list[Card]:
        for item in self.pipeline:
            source_translation, extracted_phrases = item(
                source_translation, extracted_phrases
            )
        if source_translation:
            return [source_translation, *extracted_phrases]
        return extracted_phrases
