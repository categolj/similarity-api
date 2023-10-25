CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgml;

CREATE TABLE IF NOT EXISTS entry
(
    entry_id           INT8         NOT NULL,
    title              VARCHAR(512) NOT NULL,
    content            TEXT         NOT NULL,
    last_modified_date TIMESTAMP WITH TIME ZONE,
    embedding          vector(1024),
    PRIMARY KEY (entry_id)
);

CREATE TABLE metadata
(
    last_imported_date TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS entry_embedding ON entry USING ivfflat (embedding vector_cosine_ops) WITH (lists = 1024);
CREATE INDEX IF NOT EXISTS entry_last_modified_date ON entry (last_modified_date);