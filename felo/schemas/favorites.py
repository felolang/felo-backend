import uuid
from typing import List, Optional

from pydantic import BaseModel, Field

from felo.db.models.lookup import PhrasesTypeEnum, TranslateEngineEnum
from felo.schemas.base_model_db import BaseModelDB
from felo.schemas.languages.iso639 import Language


class FavoriteResponseSchema:
    lookup_id: uuid.UUID


# class PhrasesSchema(BaseModelDB):
#     phrase_text: str
#     phrase_normalized_text: str
#     phrase_text_translation: str
#     phrase_normalized_text_translation: str
#     type: PhrasesTypeEnum
#     lookup_answer_id: Optional[uuid.UUID] = None
#     explanation: Optional[str] = None
#     explanation_translation: Optional[str] = None
