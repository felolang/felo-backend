from typing import List

from pydantic import BaseModel

extract_phrases_prompt = """


please answer in json list format with this fields  (like this {{phrases: [{{"phrase_text": "...", "phrase_type": "...", "translation": "...", "explanation": "...}}]}}):
1. phrase_text: find idioms, phrasal verbs or slang in this text "{context}". mark the phrase as NOTHING if it doesn't fit other types. But don't try to find such NOTHING phrases on purpose
2. phrase_type: type of extracted phrase (IDIOM, PHRASAL_VERB, SLANG, NOTHING) other types are forbidden!.  
3. translations: lits of possible translations in context of this phrase from {source_language} to {target_language} language.
4. explanation: explanation of this phrase in {target_language}. please explane in like native speaker in {target_language} language
5. normalized_phrase_text: normal form of phrase_text in {source_language} language if possible, else None
6. normalized_translations: list of possible translations of normalized_phrase_text to {target_language} language

If you can't find anything, just return an empty list.
"""


class ExtractPhrasesRequest(BaseModel):
    text: str
    context: str
    source_language: str
    target_language: str


class ExtractedPhrase(BaseModel):
    phrase_text: str
    phrase_type: str
    translations: List[str]
    explanation: str
    normalized_phrase_text: str
    normalized_translations: list[str]


class ExtractPhrasesResponse(BaseModel):
    phrases: List[ExtractedPhrase]


extract_phrases_prompt_examples = [
    (
        ExtractPhrasesRequest(
            text="I",
            context="May I top something off",
            source_language="EN",
            target_language="RU",
        ),
        ExtractPhrasesResponse(
            phrases=[
                ExtractedPhrase(
                    phrase_text="top off",
                    phrase_type="PHRASAL_VERB",
                    translations=["долить", "подлить"],
                    normalized_phrase_text="to top off",
                    normalized_translations=["долить", "подлить"],
                    explanation='"Top off" - это фразовый глагол, который означает добавить или долить что-то до верха.',
                )
            ]
        ),
    ),
    (
        ExtractPhrasesRequest(
            text="off",
            context="May I top off your beverage?",
            source_language="EN",
            target_language="RU",
        ),
        ExtractPhrasesResponse(
            phrases=[
                ExtractedPhrase(
                    phrase_text="top off",
                    phrase_type="PHRASAL_VERB",
                    translations=["долить", "подлить"],
                    normalized_phrase_text="to top off",
                    normalized_translations=["долить", "подлить"],
                    explanation='"Top off" - это фразовый глагол, который означает добавить или долить что-то до верха.',
                )
            ]
        ),
    ),
    (
        ExtractPhrasesRequest(
            text="fill",
            context="Please can you fill this form in?",
            source_language="EN",
            target_language="RU",
        ),
        ExtractPhrasesResponse(
            phrases=[
                ExtractedPhrase(
                    phrase_text="fill in",
                    phrase_type="PHRASAL_VERB",
                    translations=["заполнить"],
                    normalized_phrase_text="to fill in",
                    normalized_translations=["заполнить"],
                    explanation='"Fill in" в данном контексте означает дополнить информацию в указанной форме, документе или месте, вводя необходимые данные.',
                )
            ]
        ),
    ),
    (
        ExtractPhrasesRequest(
            text="be",
            context="To be in the same boat",
            source_language="EN",
            target_language="RU",
        ),
        ExtractPhrasesResponse(
            phrases=[
                ExtractedPhrase(
                    phrase_text="To be in the same boat",
                    phrase_type="IDIOM",
                    translations=[
                        "в одной лодке",
                        "в одинаковом положении",
                        "братья по несчастью",
                    ],
                    normalized_phrase_text="To be in the same boat",
                    normalized_translations=[
                        "в одной лодке",
                        "в одинаковом положении",
                        "братья по несчастью",
                    ],
                    explanation='Фраза "To be in the same boat" в переводе на русский язык означает "быть в одной лодке" и используется в смысле нахождения в похожей ситуации или столкновения с одними и теми же трудностями вместе с кем-то.',
                )
            ]
        ),
    ),
    (
        ExtractPhrasesRequest(
            text="decided",
            context="After a very hard working day, John decided to quit his job, but the day after, his boss changed his work schedule, he was promoted, so he changed his mind.",
            source_language="EN",
            target_language="RU",
        ),
        ExtractPhrasesResponse(
            phrases=[
                ExtractedPhrase(
                    phrase_text="changed his mind",
                    phrase_type="IDIOM",
                    translations=["передумал", "изменил свое мнение"],
                    normalized_phrase_text="to change your mind",
                    normalized_translations=["передумать", "изменить мнение"],
                    explanation='"changed his mind" - Этот идиома означает, что человек изменил своё мнение или решение.',
                )
            ]
        ),
    ),
]


# ---------------- translation prompt --------------


prompt = """
answer in json format with this fields:
1. translations: list of possible translations of text "{text}" in context "{context}" from {source_language} language to {target_language} language. It is very important to keep meaning of context. Keep original part of speech. translate in the original tense and declension. translate with original gender (he/she/it). Please translate full "{text}"
2. normalized_text: normal form of "{text}" in {source_language} language if possible, else None
3. normalized_text_translations: list of possible translations of normalized_text to {target_language} language

"""

# 3. idiom_explanation: if it is idiom, then fill this field. explanation of idiom in {target_language} language


class UserQuestion(BaseModel):
    text: str
    context: str
    source_language: str
    target_language: str


class ModelAnswer(BaseModel):
    translations: List[str]
    normalized_text: str
    normalized_text_translations: list[str]
    # grammar: str
    # idiom_explanation: str


prompt_examples = [
    (
        UserQuestion(
            text="I",
            context="May I top off your beverage?",
            source_language="EN",
            target_language="RU",
        ),
        ModelAnswer(
            translations=["Я"],
            normalized_text="I",
            normalized_text_translations=["Я"],
            # idiom_explanation="",
            # grammar="",
        ),
    ),
    (
        UserQuestion(
            text="off",
            context="May I top off your beverage?",
            source_language="EN",
            target_language="RU",
        ),
        ModelAnswer(
            translations=["долить", "подлить"],
            normalized_text="to top off",
            normalized_text_translations=["долить", "подлить"],
            # idiom_explanation="",
            # grammar='"Top off" - это фразовый глагол, который означает добавить или долить что-то до верха. В данном контексте, "May I top off your beverage?" переводится как "Могу ли я долить ваш напиток?"',
        ),
    ),
    (
        UserQuestion(
            text="fill",
            context="Please can you fill this form in?",
            source_language="EN",
            target_language="RU",
        ),
        ModelAnswer(
            translations=["заполнить"],
            normalized_text="to fill in",
            normalized_text_translations=["заполнить"],
            # idiom_explanation="",
            # grammar='"Fill in" в данном контексте означает дополнить информацию в указанной форме, документе или месте, вводя необходимые данные.',
        ),
    ),
    # (
    #     UserQuestion(
    #         text="be",
    #         context="To be in the same boat",
    #         source_language="EN",
    #         target_language="RU",
    #     ),
    #     ModelAnswer(
    #         translations=[
    #             "в одной лодке",
    #             "в одинаковом положении",
    #             "братья по несчастью",
    #         ],
    #         # idiom_explanation='Фраза "To be in the same boat" в переводе на русский язык означает "быть в одной лодке" и используется в смысле нахождения в похожей ситуации или столкновения с одними и теми же трудностями вместе с кем-то.',
    #         # grammar="",
    #     ),
    # ),
    # (
    #     UserQuestion(
    #         text="pick",
    #         context="I'll pick you up from the station at 8 p.m.",
    #         source_language="EN",
    #         target_language="RU",
    #     ),
    #     ModelAnswer(
    #         source="pick up",
    #         transtations=["заберу"],
    #     ),
    # ),
]
