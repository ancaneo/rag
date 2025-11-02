from typing import Annotated, Literal

from pydantic import BaseModel, Base64Bytes, HttpUrl

class IngestRequest(BaseModel):
    content: Base64Bytes | HttpUrl
    document_type: Literal["pdf", "text", "html", "markdown"]

class IngestResponse(BaseModel):
    status: Literal["success", "error"]
    message: str
    chunks_created: int

class QueryRequest(BaseModel):
    question: str

class QuerySource(BaseModel):
    page: int
    text: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[QuerySource]
