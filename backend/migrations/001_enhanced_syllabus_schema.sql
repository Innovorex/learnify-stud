-- ============================================================================
-- ENHANCED SYLLABUS SYSTEM - DATABASE MIGRATION
-- Version: 2.0 - Production Ready with Year-Aware Catalog
-- ============================================================================

-- ============================================================================
-- 1. CURRICULUM CATALOG TABLE
-- Purpose: Dynamic discovery of CBSE syllabus URLs (year-aware)
-- ============================================================================
CREATE TABLE IF NOT EXISTS curriculum_catalog (
    id SERIAL PRIMARY KEY,
    academic_year VARCHAR(20) NOT NULL,                  -- '2024-25', '2025-26'
    stage VARCHAR(20) NOT NULL,                          -- 'secondary', 'sr_secondary'
    subject_display_name VARCHAR(200) NOT NULL,          -- 'Mathematics', 'Science'
    subject_code VARCHAR(10),                            -- '041', '086', etc.
    pdf_url TEXT NOT NULL,                               -- Full URL to PDF
    pdf_filename VARCHAR(300),                           -- Original filename
    discovered_at TIMESTAMP DEFAULT NOW(),
    last_verified TIMESTAMP,                             -- Last time URL was checked
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(academic_year, stage, subject_display_name)
);

CREATE INDEX idx_curriculum_catalog_year_stage ON curriculum_catalog(academic_year, stage);
CREATE INDEX idx_curriculum_catalog_subject ON curriculum_catalog(subject_display_name);

-- ============================================================================
-- 2. ENHANCED SYLLABUS MASTER TABLE
-- Purpose: Store complete syllabus with version control
-- ============================================================================
CREATE TABLE IF NOT EXISTS syllabus_master (
    id SERIAL PRIMARY KEY,
    board VARCHAR(50) DEFAULT 'CBSE',
    class_name VARCHAR(10) NOT NULL,                     -- '9', '10', '11', '12'
    subject VARCHAR(100) NOT NULL,
    subject_code VARCHAR(10),                            -- NEW: CBSE subject code
    stage VARCHAR(20),                                   -- NEW: 'secondary' or 'sr_secondary'
    academic_year VARCHAR(20) NOT NULL,                  -- '2024-25'
    pdf_url TEXT,
    content_extracted TEXT,                              -- Full extracted text
    content_sha256 CHAR(64),                            -- NEW: SHA256 checksum for version control
    last_updated TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    catalog_id INTEGER REFERENCES curriculum_catalog(id), -- Link to catalog entry
    UNIQUE(board, class_name, subject, academic_year)
);

CREATE INDEX idx_syllabus_master_class_subject ON syllabus_master(class_name, subject);
CREATE INDEX idx_syllabus_master_year ON syllabus_master(academic_year);
CREATE INDEX idx_syllabus_master_sha ON syllabus_master(content_sha256);

-- ============================================================================
-- 3. ENHANCED SYLLABUS TOPICS TABLE
-- Purpose: Hierarchical topic structure with parent-child relationships
-- ============================================================================
CREATE TABLE IF NOT EXISTS syllabus_topics (
    id SERIAL PRIMARY KEY,
    syllabus_id INTEGER REFERENCES syllabus_master(id) ON DELETE CASCADE,

    -- Hierarchy fields
    parent_topic_id INTEGER REFERENCES syllabus_topics(id),  -- NEW: For nested topics
    is_chapter BOOLEAN DEFAULT TRUE,                         -- NEW: Distinguish chapters from subtopics

    -- Structure fields
    unit_number INTEGER,                                 -- Unit 1, 2, 3...
    unit_name VARCHAR(200),                             -- "Chemical Reactions"
    chapter_number INTEGER,                             -- Chapter 1, 2, 3...
    chapter_name VARCHAR(200) NOT NULL,                 -- "Real Numbers"
    topic_name VARCHAR(300),                            -- "Euclid's Division Lemma"

    -- Content fields
    subtopics TEXT[],                                   -- Array of subtopic strings
    learning_outcomes TEXT[],                           -- Expected learning outcomes
    content_details TEXT,                               -- Detailed syllabus content
    key_concepts TEXT[],                                -- Key concepts covered

    -- Metadata
    difficulty_level VARCHAR(20),                       -- 'easy', 'medium', 'hard'
    weightage INTEGER,                                  -- Marks weightage in exam
    sequence_order INTEGER,                             -- Display order

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_syllabus_topics_syllabus ON syllabus_topics(syllabus_id);
CREATE INDEX idx_syllabus_topics_parent ON syllabus_topics(parent_topic_id);
CREATE INDEX idx_syllabus_topics_chapter ON syllabus_topics(is_chapter);
CREATE INDEX idx_syllabus_topics_order ON syllabus_topics(syllabus_id, sequence_order);

-- ============================================================================
-- 4. ENHANCED SYLLABUS FETCH LOG TABLE
-- Purpose: Detailed logging with retry tracking and performance metrics
-- ============================================================================
CREATE TABLE IF NOT EXISTS syllabus_fetch_log (
    id SERIAL PRIMARY KEY,
    board VARCHAR(50),
    class_name VARCHAR(10),
    subject VARCHAR(100),
    academic_year VARCHAR(20),

    -- Status tracking
    fetch_status VARCHAR(50),                           -- 'success', 'failed', 'pending', 'retrying'
    source VARCHAR(200),                                -- URL or AI agent

    -- NEW: Enhanced logging
    http_status INTEGER,                                -- HTTP response code
    attempt INTEGER DEFAULT 1,                          -- Retry attempt number
    duration_ms INTEGER,                                -- Time taken in milliseconds

    -- Error handling
    error_message TEXT,
    error_type VARCHAR(100),                            -- 'network', 'parsing', 'validation'

    fetched_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE INDEX idx_fetch_log_status ON syllabus_fetch_log(fetch_status);
CREATE INDEX idx_fetch_log_date ON syllabus_fetch_log(fetched_at);

-- ============================================================================
-- 5. UPDATE ASSESSMENTS TABLE
-- Purpose: Link assessments to specific syllabus topics
-- ============================================================================
ALTER TABLE assessments
    ADD COLUMN IF NOT EXISTS syllabus_topic_id INTEGER REFERENCES syllabus_topics(id);

CREATE INDEX IF NOT EXISTS idx_assessments_topic ON assessments(syllabus_topic_id);

-- ============================================================================
-- 6. CBSE SUBJECT CODE MAPPING TABLE (Reference Data)
-- Purpose: Standard CBSE subject codes for validation
-- ============================================================================
CREATE TABLE IF NOT EXISTS cbse_subject_codes (
    id SERIAL PRIMARY KEY,
    subject_code VARCHAR(10) UNIQUE NOT NULL,
    subject_name VARCHAR(200) NOT NULL,
    stage VARCHAR(20) NOT NULL,                         -- 'secondary', 'sr_secondary'
    is_major BOOLEAN DEFAULT TRUE,                      -- Major vs elective subject
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert common CBSE subject codes
INSERT INTO cbse_subject_codes (subject_code, subject_name, stage, is_major) VALUES
    -- Secondary (IX-X)
    ('041', 'Mathematics', 'secondary', TRUE),
    ('086', 'Science', 'secondary', TRUE),
    ('087', 'Social Science', 'secondary', TRUE),
    ('184', 'English Language and Literature', 'secondary', TRUE),
    ('085', 'Information Technology', 'secondary', FALSE),

    -- Senior Secondary (XI-XII)
    ('041', 'Mathematics', 'sr_secondary', TRUE),
    ('042', 'Physics', 'sr_secondary', TRUE),
    ('043', 'Chemistry', 'sr_secondary', TRUE),
    ('044', 'Biology', 'sr_secondary', TRUE),
    ('030', 'Economics', 'sr_secondary', TRUE),
    ('039', 'Sociology', 'sr_secondary', TRUE),
    ('028', 'Political Science', 'sr_secondary', TRUE),
    ('027', 'History', 'sr_secondary', TRUE),
    ('029', 'Geography', 'sr_secondary', TRUE),
    ('055', 'Accountancy', 'sr_secondary', TRUE),
    ('054', 'Business Studies', 'sr_secondary', TRUE),
    ('083', 'Computer Science', 'sr_secondary', TRUE)
ON CONFLICT (subject_code) DO NOTHING;

-- ============================================================================
-- 7. VIEWS FOR EASY QUERYING
-- ============================================================================

-- View: Complete syllabus hierarchy
CREATE OR REPLACE VIEW v_syllabus_hierarchy AS
SELECT
    sm.id as syllabus_id,
    sm.board,
    sm.class_name,
    sm.subject,
    sm.subject_code,
    sm.academic_year,
    st.id as topic_id,
    st.parent_topic_id,
    st.is_chapter,
    st.unit_number,
    st.unit_name,
    st.chapter_number,
    st.chapter_name,
    st.topic_name,
    st.weightage,
    st.difficulty_level,
    st.sequence_order
FROM syllabus_master sm
LEFT JOIN syllabus_topics st ON sm.id = st.syllabus_id
WHERE sm.is_active = TRUE
ORDER BY sm.class_name, st.sequence_order;

-- View: Latest active catalog
CREATE OR REPLACE VIEW v_latest_catalog AS
SELECT DISTINCT ON (stage, subject_display_name)
    *
FROM curriculum_catalog
WHERE is_active = TRUE
ORDER BY stage, subject_display_name, academic_year DESC;

-- ============================================================================
-- 8. FUNCTIONS & TRIGGERS
-- ============================================================================

-- Function to update syllabus_topics.updated_at
CREATE OR REPLACE FUNCTION update_topic_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for auto-updating timestamps
CREATE TRIGGER trigger_update_topic_timestamp
    BEFORE UPDATE ON syllabus_topics
    FOR EACH ROW
    EXECUTE FUNCTION update_topic_timestamp();

-- Function to determine stage from class
CREATE OR REPLACE FUNCTION get_stage_from_class(class_num VARCHAR)
RETURNS VARCHAR AS $$
BEGIN
    IF class_num IN ('9', '10') THEN
        RETURN 'secondary';
    ELSIF class_num IN ('11', '12') THEN
        RETURN 'sr_secondary';
    ELSE
        RETURN 'unknown';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 9. COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE curriculum_catalog IS 'Dynamic catalog of CBSE syllabus URLs, auto-discovered each academic year';
COMMENT ON TABLE syllabus_master IS 'Master table storing complete syllabus content with SHA256 versioning';
COMMENT ON TABLE syllabus_topics IS 'Hierarchical topic structure with parent-child relationships';
COMMENT ON TABLE syllabus_fetch_log IS 'Detailed audit log for syllabus fetching operations';
COMMENT ON TABLE cbse_subject_codes IS 'Reference table for standard CBSE subject codes';

COMMENT ON COLUMN syllabus_master.content_sha256 IS 'SHA256 checksum for detecting syllabus changes';
COMMENT ON COLUMN syllabus_topics.parent_topic_id IS 'Self-referencing FK for nested topic hierarchy';
COMMENT ON COLUMN syllabus_topics.is_chapter IS 'TRUE for chapters, FALSE for subtopics';
COMMENT ON COLUMN syllabus_fetch_log.duration_ms IS 'Fetch duration in milliseconds for performance monitoring';

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
