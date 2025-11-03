import os
from ..main import app, rag
from fastapi.testclient import TestClient
import base64
import pytest
from langchain_postgres import PGVector

client = TestClient(app)

@pytest.fixture
def setup():
    original_vector_store = rag.vector_store
    rag.vector_store = PGVector(
        embeddings=rag.vector_store.embeddings,
        collection_name="test_items",
        connection=os.environ['DB_URI'],
    )
    yield
    rag.vector_store.delete_collection()
    rag.vector_store = original_vector_store

def parse_document(ext):
    with open(f"/app/tests/assets/document.{ext}", 'rb') as file:
        return base64.encodebytes(file.read()).decode()


def test_pdf(setup):
    request_data = {
        'content': parse_document('pdf'),
        'document_type': 'pdf'
    }
    response = client.post('/ingest', json=request_data)
    assert response.status_code == 200
    response_data = response.json()
    expected_data = {
        'status': 'success',
        'message': 'Chunks created',
        'chunks_created': 5
    }
    assert response_data == expected_data
    request_data = {
        'question': "¿Cuál es el propósito del cargo?",
    }
    response = client.post('/query', json=request_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['answer']
    assert response_data['sources']

def test_html(setup):
    request_data = {
        'content': parse_document('html'),
        'document_type': 'html'
    }
    response = client.post('/ingest', json=request_data)
    assert response.status_code == 200
    response_data = response.json()
    expected_data = {
        'status': 'success',
        'message': 'Chunks created',
        'chunks_created': 72
    }
    assert response_data == expected_data
    request_data = {
        'question': "What is the standard method for Task Decomposition?",
    }
    response = client.post('/query', json=request_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['answer']
    assert response_data['sources']

def test_txt(setup):
    request_data = {
        'content': parse_document('txt'),
        'document_type': 'text'
    }
    response = client.post('/ingest', json=request_data)
    assert response.status_code == 200
    response_data = response.json()
    expected_data = {
        'status': 'success',
        'message': 'Chunks created',
        'chunks_created': 5
    }
    assert response_data == expected_data
    request_data = {
        'question': "¿Quién es Carlos Pereira?",
    }
    response = client.post('/query', json=request_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['answer']
    assert response_data['sources']

def test_md(setup):
    request_data = {
        'content': parse_document('md'),
        'document_type': 'markdown'
    }
    response = client.post('/ingest', json=request_data)
    assert response.status_code == 200
    response_data = response.json()
    expected_data = {
        'status': 'success',
        'message': 'Chunks created',
        'chunks_created': 3
    }
    assert response_data == expected_data
    request_data = {
        'question': "¿Cuántos microservicios tiene el proyecto RAG?",
    }
    response = client.post('/query', json=request_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['answer']
    assert response_data['sources']

def test_url(setup):
    request_data = {
        'content': 'https://lilianweng.github.io/posts/2023-06-23-agent/',
        'document_type': 'html'
    }
    response = client.post('/ingest', json=request_data)
    assert response.status_code == 200
    response_data = response.json()
    expected_data = {
        'status': 'success',
        'message': 'Chunks created',
        'chunks_created': 66
    }
    assert response_data == expected_data
    request_data = {
        'question': "What is the standard method for Task Decomposition?",
    }
    response = client.post('/query', json=request_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['answer']
    assert response_data['sources']
