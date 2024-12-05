from pydantic import BaseModel
from typing import Optional

class DocumentMetadata(BaseModel):
    category: str
    description: str
    file_location: str
    filename: str
    summary: str

