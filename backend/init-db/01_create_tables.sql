-- Connect to the policybot database
\c policybot;

-- Table for SourceSummary
CREATE TABLE IF NOT EXISTS source_summaries (
    id SERIAL PRIMARY KEY,
    source_name VARCHAR NOT NULL,
    summary TEXT NOT NULL
);

-- Indices for SourceSummary
CREATE UNIQUE INDEX IF NOT EXISTS ix_source_summaries_source_name ON source_summaries (source_name);
CREATE INDEX IF NOT EXISTS ix_source_summaries_id ON source_summaries (id);

-- Table for OverallSummary
CREATE TABLE IF NOT EXISTS overall_summaries (
    id SERIAL PRIMARY KEY,
    pdf_set_hash VARCHAR NOT NULL,
    pdf_file_names TEXT NOT NULL,
    summary TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Indices for OverallSummary
CREATE UNIQUE INDEX IF NOT EXISTS ix_overall_summaries_pdf_set_hash ON overall_summaries (pdf_set_hash);
