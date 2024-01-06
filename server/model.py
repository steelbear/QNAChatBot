from pydantic import BaseModel


class Question(BaseModel):
    question: str


class Response(BaseModel):
    content: str
    error: str|None