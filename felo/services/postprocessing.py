from typing import List, Optional

from felo.schemas.cards import Card, CardTypesEnum

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
                and len(phrase.text.split()) < 2
            ):  # TODO: сделать проверку на фразовый глагол
                continue
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
