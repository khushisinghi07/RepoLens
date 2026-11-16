from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    repository_id: str = Field(min_length=1)
    question: str = Field(min_length=2, max_length=2000)
