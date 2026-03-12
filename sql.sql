-- Check if the column exists
ALTER TABLE evidence_reports ADD COLUMN IF NOT EXISTS mode VARCHAR DEFAULT 'hiring';

-- If it already existed but was causing issues, try renaming it temporarily or ensure it's not a reserved type
-- No action needed if the above command confirms the column is there.

ALTER TABLE users ADD COLUMN typing_profile JSON;
ALTER TABLE evidence_reports ADD COLUMN integrity_score FLOAT DEFAULT 1.0;
ALTER TABLE evidence_reports ADD COLUMN identity_verified BOOLEAN DEFAULT TRUE;
ALTER TABLE evidence_reports 
ADD COLUMN visual_evidence JSONB DEFAULT '[]'::jsonb;