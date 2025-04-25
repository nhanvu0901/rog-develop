from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatMessage(BaseModel):
    text: str
    context_files: Optional[List[str]] = None

class ChatResponse(BaseModel):
    response: Optional[str] = None
    timestamp: datetime = datetime.now() 