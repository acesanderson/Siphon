```sql
CREATE TABLE processed_content (
    id SERIAL PRIMARY KEY,
    uri_key TEXT UNIQUE NOT NULL,  -- Cache on uri.uri
    data JSONB NOT NULL,           -- Entire ProcessedContent as JSON
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for cache lookups
CREATE INDEX idx_processed_content_uri_key ON processed_content(uri_key);

-- Optional: Index for basic searches within JSONB
CREATE INDEX idx_processed_content_source_type ON processed_content 
USING gin((data->>'sourcetype'));
```
