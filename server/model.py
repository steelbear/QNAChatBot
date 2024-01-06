from fastapi import UploadFile
from pydantic import BaseModel


class Question(BaseModel):
    question: str
    filename: str


class Response(BaseModel):
    content: str
    error: str|None = None


class Metadata(BaseModel):
    filename: str
    page: int


class Document(BaseModel):
    id: str
    content: str
    metadata: Metadata