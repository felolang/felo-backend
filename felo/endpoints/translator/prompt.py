from typing import List

from pydantic import BaseModel

extract_phrases_prompt = """
please find all idioms, phrasal verbs, slang, terms
and answer in json list format with this fields  (like this {{phrases: [{{"phrase_text": "...", "phrase_type": "...", "translation": "...", "explanation": "...}}]}}):
1. phrase_text: try to extract phrases (idioms, phrasal verbs, slang, terms) from this text "{context}"
2. phrase_type: type of extracted phrase (IDIOM, PHRASAL_VERB, SLANG, TERM)
3. translation: translation of this phrase from {source_language} to {target_language} language.
4. explanation: explanation of this phrase in {target_language}. please explane in like native speaker in {target_language} language
"""


class ExtractPhrasesRequest(BaseModel):
    text: str
    source_language: str
    target_language: str


prompt = """
answer in json format with this fields:
1. source: try to extend {order} occurance of "{text}" in context "{context}" to phrasal verb, idiom or slang or leave it as is. result must include original text "{text}". result should be >= than text
2. translations: list of possible translations of field "source" from {source_language} to {target_language}. But meaning of translations must match {order} occurnce in original context "{context}". It is very important to keep original context and meaning. Keep original part of speech. translate in the original tense and declension. translate with original gender (he/she/it)
"""

# 3. idiom_explanation: if it is idiom, then fill this field. explanation of idiom in {target_language} language


class UserQuestion(BaseModel):
    text: str
    context: str
    source_language: str
    target_language: str


class ModelAnswer(BaseModel):
    source: str
    transtations: List[str]
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
            transtations=["Я"],
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
            transtations=["долить", "подлить"],
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
            transtations=["заполнить"],
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
            transtations=[
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
