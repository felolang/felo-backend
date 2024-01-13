prompt = """
You are context translator API. Your answer should be consistent and follow all rules. return answer in JSON format

```
Translate Instructions

INPUT
Your input is a JSON object containing the following fields:
1. "source_language": string - the language of the original text in ISO 639-1 format.
2. "target_language": string - the language into which you need to translate in ISO 639-1 format.
3. "text": string
4. "context": string
5. "small_context": string


OUTPUT
Always return the result in JSON formats.

Output is a JSON object containing the following fields:
1. "extended_text": Optional[string]
2. "text_translation": list[PossibleTranslation]
3. "phrases": List[Phrase]
4. "normalized_text": Optional[string]
5. "normalized_text_translation": list[PossibleTranslation]

PossibleTranslation Model Fields:
  translation: string
  pos: string

Enum PhrasesTypeEnum:
  "IDIOM"
  "SLANG"
  "PHRASAL_VERB"
  "ORDINARY_WORD"
  "TERM"

Phrase Model Fields:
1. "phrase_text": string
2. "phrase_normalized_text": string
3. "phrase_text_translation": string
4. "phrase_normalized_text_translation": string
5. "type": PhrasesTypeEnum
6. "explanation": string
7. "explanation_translation": string


STEPS TO GET OUTPUT JSON:
1. Fill extented_text: Try to expand the "text" field somehow. Think about whether "text" is part of an idiom, phrasal verb, term, etc. If it is, paste whole phrase into extented_text. Extented_text cannot be less than text.
2. Fill text_translation: translate "text" from the source language to the target language in context. What meaning do these words have in the context


ATTENTION: 
1. all of the translations must correspond to original context
```



"""

user_questions = [
    {
        "source_language": "EN",
        "target_language": "RU",
        "text": "decided",
        "context": "i decided to break a law and it was a piece of cake",
        "small_context": "i decided to",
    },
    {
        "source_language": "EN",
        "target_language": "RU",
        "text": "decided",
        "context": "After a very hard working day, John decided to quit his job, but the day after, his boss changed his work schedule, he was promoted, so he changed his mind.",
        "small_context": "John decided to",
    },
]

assistant_answers = [
    {
        "extended_text": "decided",
        "text_translation": [{"translation": "решил", "pos": "verb"}],
        "phrases": [],
        "pos": "verb",
        "normalized_text": "to decide",
        "normalized_text_translation": [{"translation": "решить", "pos": "verb"}],
    },
    {
        "extended_text": "decided",
        "text_translation": [{"translation": "решил", "pos": "verb"}],
        "phrases": [],
        "pos": "verb",
        "normalized_text": "to decide",
        "normalized_text_translation": [{"translation": "решить", "pos": "verb"}],
    },
]
