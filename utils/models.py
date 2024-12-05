from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Metadata(BaseModel):
    category: Optional[str] = "Uncategorized"
    description: str
    file_location: str
    filename: str
    summary: str
    created_at: Optional[datetime] = None


class CaseStatement(BaseModel):
    case_statement: str
    created_at: Optional[datetime] = None
