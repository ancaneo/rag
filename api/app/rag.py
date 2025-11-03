import os
import tempfile
from pydantic import HttpUrl 
from langchain.chat_models import init_chat_model
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.tools import tool
from langchain_core.messages import ToolMessage
from langchain_community.document_loaders import (
    WebBaseLoader,
    PyPDFLoader,
    BSHTMLLoader,
    TextLoader
    )

import requests
from langchain.agents import create_agent
from langchain_postgres import PGVector

EMBEDDINGS_FACTORIES = {
    'gemini': GoogleGenerativeAIEmbeddings,
    'open_ai': OpenAIEmbeddings
}

chat_model = os.environ.get('CHAT_MODEL', 'google_genai:gemini-2.5-flash-lite').lower()
embeddings_provider = os.environ.get('EMBEDDINGS_PROVIDER', 'gemini').lower()
EmbeddingsFactory = EMBEDDINGS_FACTORIES[embeddings_provider]
embeddings_model = os.environ.get('EMBEDDINGS_MODEL', 'models/gemini-embedding-001').lower()

class RagManager:
    model = init_chat_model(chat_model)
    embeddings = EmbeddingsFactory(model=embeddings_model)
    vector_store = PGVector(
        embeddings=embeddings,
        collection_name="items",
        connection=os.environ['DB_URI'],
    )
    loaders = {
        "pdf": PyPDFLoader,
        "text": TextLoader,
        "html": BSHTMLLoader,
        "markdown": TextLoader
    }

    def __init__(self):
        prompt = (
            "You have access to a tool that retrieves context. "
            "Use the tool to help answer user queries."
        )
        @tool(response_format="content_and_artifact")
        def retrieve_context(query: str):
            """Retrieve information to help answer a query."""
            retrieved_docs = self.vector_store.similarity_search(query, k=2)
            serialized = "\n\n".join(
                (f"Source: {doc.metadata}\nContent: {doc.page_content}")
                for doc in retrieved_docs
            )
            return serialized, retrieved_docs

        tools = [retrieve_context]
        self.agent = create_agent(self.model, tools, system_prompt=prompt)

    def ingest(self, content, document_type):
        if isinstance(content, HttpUrl):
            loader = WebBaseLoader(web_paths=(str(content),))
            docs = loader.load()
        elif isinstance(content, bytes):
            with tempfile.NamedTemporaryFile() as file:
                file.write(content)
                file.seek(0)
                loader = self.loaders[document_type](file.name)
                docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # chunk size (characters)
            chunk_overlap=200,  # chunk overlap (characters)
            add_start_index=True,  # track index in original document
        )
        all_splits = text_splitter.split_documents(docs)
        document_ids = []
        if all_splits:
            document_ids = self.vector_store.add_documents(documents=all_splits)
        return len(document_ids)

    def query(self, question):
        response = self.agent.invoke({"messages": [{"role": "user", "content": question}]})
        messages = response['messages']
        sources = []
        for message in messages:
            if isinstance(message, ToolMessage):
                for document in message.artifact:
                    sources.append({
                        'page': document.metadata.get('page_label', 1),
                        'text': document.page_content
                    })
        return {
            'answer': messages[-1].content,
            'sources': sources
            }
        return
