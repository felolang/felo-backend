prompt = """



Please answer only in JSON format. fields are following:
1. "extended_text": Optional[string]
2. "extended_text_translation": list[PossibleTranslation]
3. "text_translation": list[PossibleTranslation]
4. "phrases": List[Phrase]
5. "normalized_text": Optional[string]
6. "normalized_text_translation": list[PossibleTranslation]

ADDITIONAL MODELS
PossibleTranslation:
  translation: string 
  pos: string 

Steps to do:
1) extended_text.
Given the following sentence:
"{context}"
Is the {occurance} occurance of phrase "{text}" in this context a:
a) Phrasal verb
b) Idiom
c) Slang
d) Term
If not, leave None here.
2) extended_text_translation: 
this field is list of PossibleTranslation model. where
* "translation" is -
translation of step 1 according to {occurance} occurance in context "{context}" from {source_language} lang to {target_language} lang. If step 1 is None, then here None also
* "pos" is part of speech of translation if possible

3) text_translation: 
this field is list of PossibleTranslation model. where
* "translation" is -
translation "{text}" according to {occurance} occurance in context "{context}" from {source_language} lang to {target_language} lang.
* "pos" is part of speech of translation if possible

3) phrases: []
4) normalized_text: None
5) normalized_text_translation: []

"""

user_questions = [
    # {
    #     "source_language": "EN",
    #     "target_language": "RU",
    #     "text": "decided",
    #     "context": "i decided to break a law and it was a piece of cake",
    #     "small_context": "i decided to",
    # },
    # {
    #     "source_language": "EN",
    #     "target_language": "RU",
    #     "text": "decided",
    #     "context": "After a very hard working day, John decided to quit his job, but the day after, his boss changed his work schedule, he was promoted, so he changed his mind.",
    #     "small_context": "John decided to",
    # },
]

assistant_answers = [
    # {
    #     "extended_text": "decided",
    #     "text_translation": [{"translation": "решил", "pos": "verb"}],
    #     "phrases": [],
    #     "pos": "verb",
    #     "normalized_text": "to decide",
    #     "normalized_text_translation": [{"translation": "решить", "pos": "verb"}],
    # },
    # {
    #     "extended_text": "decided",
    #     "text_translation": [{"translation": "решил", "pos": "verb"}],
    #     "phrases": [],
    #     "pos": "verb",
    #     "normalized_text": "to decide",
    #     "normalized_text_translation": [{"translation": "решить", "pos": "verb"}],
    # },
]
