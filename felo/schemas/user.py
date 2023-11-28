from typing import List, Optional

from pydantic import EmailStr

from felo.schemas.base_model_db import BaseModelDB
from felo.schemas.lookup import LookupSchema


class UserSchema(BaseModelDB):
    username: Optional[str]
    password: Optional[str]
    email: EmailStr
    lookups: Optional[List[LookupSchema]] = []
