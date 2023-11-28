import datetime
import uuid
from typing import Optional

from pydantic import BaseModel


class BaseModelDB(BaseModel):
    id: Optional[uuid.UUID]
    create_time: Optional[datetime.datetime]
    update_time: Optional[datetime.datetime]

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
