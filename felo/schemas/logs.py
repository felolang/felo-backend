from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr

from felo.schemas.lookup import LookupSchema


class LogsLevelEnum(Enum):
    DEBUG = "DEBUG"
    WARNING = "WARNING"
    INFO = "INFO"
    ERROR = "ERROR"


class PostLogsIn(BaseModel):
    message: str
    level: LogsLevelEnum
    datetime: Optional[datetime] = None
