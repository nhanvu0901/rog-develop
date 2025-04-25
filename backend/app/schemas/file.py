from pydantic import BaseModel
from datetime import datetime

class FileResponse(BaseModel):
    filename: str
    content_type: str
    text_content: str

class FileInfo(BaseModel):
    filename: str
    size: int  # in bytes
    uploaded_at: datetime 