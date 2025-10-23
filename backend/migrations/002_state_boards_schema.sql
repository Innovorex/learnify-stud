-- Migration: Add State Board Support (Telangana & Andhra Pradesh)
-- Date: 2025-10-15
-- Purpose: Enable state board syllabi storage alongside CBSE

-- ============================================================================
-- 1. CREATE STATE BOARDS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS state_boards (
    id SERIAL PRIMARY KEY,
    board_code VARCHAR(20) UNIQUE NOT NULL,
    board_name VARCHAR(100) NOT NULL,
    state_name VARCHAR(50) NOT NULL,
    website_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Seed data for Telangana and Andhra Pradesh
INSERT INTO state_boards (board_code, board_name, state_name, website_url) VALUES
('TSBSE', 'Telangana State Board of Secondary Education', 'Telangana', 'https://bse.telangana.gov.in/'),
('BSEAP', 'Board of Secondary Education, Andhra Pradesh', 'Andhra Pradesh', 'https://bse.ap.gov.in/')
ON CONFLICT (board_code) DO NOTHING;

-- ============================================================================
-- 2. ALTER SYLLABUS_MASTER TABLE
-- ============================================================================

-- Add columns for state board support
ALTER TABLE syllabus_master
ADD COLUMN IF NOT EXISTS board_type VARCHAR(20) DEFAULT 'CBSE';
-- Values: 'CBSE', 'STATE'

ALTER TABLE syllabus_master
ADD COLUMN IF NOT EXISTS state_board_id INT REFERENCES state_boards(id);

ALTER TABLE syllabus_master
ADD COLUMN IF NOT EXISTS medium VARCHAR(20) DEFAULT 'English';
-- Values: 'English', 'Telugu', 'Hindi', etc.

ALTER TABLE syllabus_master
ADD COLUMN IF NOT EXISTS textbook_name VARCHAR(200);
-- State board specific textbook name

ALTER TABLE syllabus_master
ADD COLUMN IF NOT EXISTS publisher VARCHAR(100);
-- e.g., 'SCERT Telangana', 'SCERT Andhra Pradesh'

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_syllabus_board_type ON syllabus_master(board_type);
CREATE INDEX IF NOT EXISTS idx_syllabus_state_board ON syllabus_master(state_board_id);
CREATE INDEX IF NOT EXISTS idx_syllabus_medium ON syllabus_master(medium);

-- ============================================================================
-- 3. CREATE STATE BOARD RESOURCES TABLE (for tracking URLs)
-- ============================================================================

CREATE TABLE IF NOT EXISTS state_board_resources (
    id SERIAL PRIMARY KEY,
    state_board_id INT REFERENCES state_boards(id),
    class_name VARCHAR(10) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    medium VARCHAR(20) NOT NULL DEFAULT 'English',
    resource_type VARCHAR(20) NOT NULL,
    -- Values: 'textbook_pdf', 'syllabus_doc', 'question_bank'
    resource_url TEXT,
    pdf_available BOOLEAN DEFAULT FALSE,
    last_verified TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(state_board_id, class_name, subject, medium, resource_type)
);

CREATE INDEX IF NOT EXISTS idx_resources_board_class ON state_board_resources(state_board_id, class_name);

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check state boards added
SELECT * FROM state_boards;

-- Check new columns in syllabus_master
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'syllabus_master'
  AND column_name IN ('board_type', 'state_board_id', 'medium', 'textbook_name', 'publisher');

-- ============================================================================
-- ROLLBACK (if needed)
-- ============================================================================

-- To rollback this migration:
-- DROP TABLE IF EXISTS state_board_resources;
-- ALTER TABLE syllabus_master DROP COLUMN IF EXISTS board_type;
-- ALTER TABLE syllabus_master DROP COLUMN IF EXISTS state_board_id;
-- ALTER TABLE syllabus_master DROP COLUMN IF EXISTS medium;
-- ALTER TABLE syllabus_master DROP COLUMN IF EXISTS textbook_name;
-- ALTER TABLE syllabus_master DROP COLUMN IF EXISTS publisher;
-- DROP TABLE IF EXISTS state_boards;
