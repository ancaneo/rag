from typing import Union

from fastapi import FastAPI, HTTPException,status, Response
from .rag import RagManager
from .models import (
    IngestRequest,
    IngestResponse,
    QueryRequest,
    QueryResponse
    )

app = FastAPI()
rag = RagManager()

@app.get("/health")
def get_health():
    return 'OK'

@app.post("/ingest")
def post_ingest(request: IngestRequest, response: Response) -> IngestResponse:
    try:
        chunks = rag.ingest(
            content=request.content,
            document_type=request.document_type)
        return {
            "status": "success",
            "message": "Chunks created",
            "chunks_created": chunks
        }
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "status": "error",
            "message": str(e),
            "chunks_created": 0
        }

@app.post("/query")
def post_query(request: QueryRequest) -> QueryResponse:
    return rag.query(request.question)
