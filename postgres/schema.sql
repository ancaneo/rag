-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    embedding vector(1536) -- vector data
);