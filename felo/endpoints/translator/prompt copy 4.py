from typing import List

from pydantic import BaseModel

extract_phrases_prompt = """


please answer in json list format with this fields  (like this {{phrases: [{{"phrase_text": "...", "phrase_type": "...", "translation": "...", "explanation": "...}}]}}):
1. phrase_text: find idioms, phrasal verbs or slang in this text "{text}" in context "{context}". do not confuse idioms and phrasal verbs
2. phrase_type: type of extracted phrase (IDIOM, PHRASAL_VERB, SLANG, NOTHING, ORDINARY_PHRASE) other types are forbidden!.  
3. translations: lits of possible translations in context of this phrase from {source_language} to {target_language} language.
4. explanation: explanation of this phrase in {target_language}. please explane in like native speaker in {target_language} language

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


class ExtractPhrasesResponse(BaseModel):
    phrases: List[ExtractedPhrase]


extract_phrases_prompt_examples = [
    (
        ExtractPhrasesRequest(
            text="I",
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
                    explanation='"changed his mind" - Этот идиома означает, что человек изменил своё мнение или решение.',
                )
            ]
        ),
    ),
]


# ---------------- translation prompt --------------


prompt = """
answer in json format with this fields:
# 1. source: try to extend "{text}" in context "{context}" to phrasal verb, idiom or slang or leave it as is. result must include original text "{text}". result should be >= than text. 
2. translations: list of possible translations of "{text}" in "{context}" from {source_language} to {target_language}. It is very important to keep original context and meaning. Keep original part of speech. translate in the original tense and declension. translate with original gender (he/she/it)
"""

# 3. idiom_explanation: if it is idiom, then fill this field. explanation of idiom in {target_language} language


class UserQuestion(BaseModel):
    text: str
    context: str
    source_language: str
    target_language: str


class ModelAnswer(BaseModel):
    source: str
    translations: List[str]
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
            source="I",
            translations=["Я"],
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
            source="top off",
            translations=["долить", "подлить"],
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
            source="fill in",
            translations=["заполнить"],
            # idiom_explanation="",
            # grammar='"Fill in" в данном контексте означает дополнить информацию в указанной форме, документе или месте, вводя необходимые данные.',
        ),
    ),
    (
        UserQuestion(
            text="be",
            context="To be in the same boat",
            source_language="EN",
            target_language="RU",
        ),
        ModelAnswer(
            source="To be in the same boat",
            translations=[
                "в одной лодке",
                "в одинаковом положении",
                "братья по несчастью",
            ],
            # idiom_explanation='Фраза "To be in the same boat" в переводе на русский язык означает "быть в одной лодке" и используется в смысле нахождения в похожей ситуации или столкновения с одними и теми же трудностями вместе с кем-то.',
            # grammar="",
        ),
    ),
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
