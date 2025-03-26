from pydantic import BaseModel


class ChatInput(BaseModel):
    question: str
    language: str
    session_id: str


class APIRequest(BaseModel):
    input: ChatInput


class APIResponse(BaseModel):
    output: str
    session_id: str
    language: str
