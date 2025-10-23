from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Text, Boolean, ARRAY, UniqueConstraint
from app.db import Base
from datetime import datetime, timezone, timedelta

# IST timezone (UTC + 5:30)
IST = timezone(timedelta(hours=5, minutes=30))

def ist_now():
    """Get current time in IST as naive datetime"""
    return datetime.now(IST).replace(tzinfo=None)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="student")  # 'teacher' or 'student'
    class_name = Column(String, nullable=True)  # Only for students
    section = Column(String, nullable=True)  # Only for students

class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    class_name = Column(String, nullable=False)
    section = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    chapter = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=ist_now)

class Question(Base):
    __tablename__ = "question_bank"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)
    correct_answer = Column(String, nullable=False)
    difficulty = Column(String, default="medium")

class Result(Base):
    __tablename__ = "exam_results"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    answers = Column(JSON)  # store {question_id: selected_option}
    score = Column(Integer, default=0)
    submitted_at = Column(DateTime, default=ist_now)


# ============================================================================
# ENHANCED SYLLABUS MODELS
# ============================================================================

class CurriculumCatalog(Base):
    """
    Dynamic catalog of CBSE syllabus URLs (year-aware)
    Automatically discovered from CBSE website
    """
    __tablename__ = "curriculum_catalog"

    id = Column(Integer, primary_key=True, index=True)
    academic_year = Column(String(20), nullable=False)               # '2024-25', '2025-26'
    stage = Column(String(20), nullable=False)                       # 'secondary', 'sr_secondary'
    subject_display_name = Column(String(200), nullable=False)       # 'Mathematics', 'Science'
    subject_code = Column(String(10))                                # '041', '086', etc.
    pdf_url = Column(Text, nullable=False)                           # Full URL to PDF
    pdf_filename = Column(String(300))                               # Original filename
    discovered_at = Column(DateTime, default=ist_now)
    last_verified = Column(DateTime)                                 # Last time URL was checked
    is_active = Column(Boolean, default=True)


class SyllabusMaster(Base):
    """
    Master table storing complete syllabus content with SHA256 versioning
    Supports both CBSE and State Boards
    """
    __tablename__ = "syllabus_master"

    id = Column(Integer, primary_key=True, index=True)
    board = Column(String(50), default="CBSE")
    class_name = Column(String(10), nullable=False)                  # '9', '10', '11', '12'
    subject = Column(String(100), nullable=False)
    subject_code = Column(String(10))                                # CBSE subject code
    stage = Column(String(20))                                       # 'secondary' or 'sr_secondary'
    academic_year = Column(String(20), nullable=False)               # '2024-25'
    pdf_url = Column(Text)
    content_extracted = Column(Text)                                 # Full extracted text
    content_sha256 = Column(String(64))                             # SHA256 checksum for version control
    last_updated = Column(DateTime, default=ist_now)
    is_active = Column(Boolean, default=True)
    catalog_id = Column(Integer, ForeignKey("curriculum_catalog.id"))  # Link to catalog entry

    # State Board Support (added 2025-10-15)
    board_type = Column(String(20), default='CBSE')                  # 'CBSE' or 'STATE'
    state_board_id = Column(Integer, ForeignKey("state_boards.id"))  # Foreign key to state_boards
    medium = Column(String(20), default='English')                   # 'English', 'Telugu', 'Hindi', etc.
    textbook_name = Column(String(200))                              # State board specific textbook name
    publisher = Column(String(100))                                  # e.g., 'SCERT Telangana', 'SCERT AP'

    # Three Language Formula Support (added 2025-10-15)
    language_position = Column(String(20))                           # 'FL' (First), 'SL' (Second), 'TL' (Third), or NULL


class SyllabusTopics(Base):
    """
    Hierarchical topic structure with parent-child relationships
    """
    __tablename__ = "syllabus_topics"

    id = Column(Integer, primary_key=True, index=True)
    syllabus_id = Column(Integer, ForeignKey("syllabus_master.id"))

    # Hierarchy fields
    parent_topic_id = Column(Integer, ForeignKey("syllabus_topics.id"))  # For nested topics
    is_chapter = Column(Boolean, default=True)                           # Distinguish chapters from subtopics

    # Structure fields
    unit_number = Column(Integer)                                    # Unit 1, 2, 3...
    unit_name = Column(String(200))                                  # "Chemical Reactions"
    chapter_number = Column(Integer)                                 # Chapter 1, 2, 3...
    chapter_name = Column(String(200), nullable=False)               # "Real Numbers"
    topic_name = Column(String(300))                                 # "Euclid's Division Lemma"

    # Content fields - using JSON for PostgreSQL array support
    subtopics = Column(JSON)                                         # Array of subtopic strings
    learning_outcomes = Column(JSON)                                 # Expected learning outcomes
    content_details = Column(Text)                                   # Detailed syllabus content
    key_concepts = Column(JSON)                                      # Key concepts covered

    # Metadata
    difficulty_level = Column(String(20))                            # 'easy', 'medium', 'hard'
    weightage = Column(Integer)                                      # Marks weightage in exam
    sequence_order = Column(Integer)                                 # Display order

    created_at = Column(DateTime, default=ist_now)
    updated_at = Column(DateTime, default=ist_now)


class SyllabusFetchLog(Base):
    """
    Detailed audit log for syllabus fetching operations
    """
    __tablename__ = "syllabus_fetch_log"

    id = Column(Integer, primary_key=True, index=True)
    board = Column(String(50))
    class_name = Column(String(10))
    subject = Column(String(100))
    academic_year = Column(String(20))

    # Status tracking
    fetch_status = Column(String(50))                                # 'success', 'failed', 'pending', 'retrying'
    source = Column(String(200))                                     # URL or AI agent

    # Enhanced logging
    http_status = Column(Integer)                                    # HTTP response code
    attempt = Column(Integer, default=1)                             # Retry attempt number
    duration_ms = Column(Integer)                                    # Time taken in milliseconds

    # Error handling
    error_message = Column(Text)
    error_type = Column(String(100))                                 # 'network', 'parsing', 'validation'

    fetched_at = Column(DateTime, default=ist_now)
    completed_at = Column(DateTime)


class CBSESubjectCode(Base):
    """
    Reference table for standard CBSE subject codes
    """
    __tablename__ = "cbse_subject_codes"

    id = Column(Integer, primary_key=True, index=True)
    subject_code = Column(String(10), unique=True, nullable=False)
    subject_name = Column(String(200), nullable=False)
    stage = Column(String(20), nullable=False)                       # 'secondary', 'sr_secondary'
    is_major = Column(Boolean, default=True)                         # Major vs elective subject
    created_at = Column(DateTime, default=ist_now)


# ============================================================================
# STATE BOARD MODELS (Added 2025-10-15)
# ============================================================================

class StateBoard(Base):
    """
    State education boards (Telangana, Andhra Pradesh, etc.)
    """
    __tablename__ = "state_boards"

    id = Column(Integer, primary_key=True, index=True)
    board_code = Column(String(20), unique=True, nullable=False)     # 'TSBSE', 'BSEAP', etc.
    board_name = Column(String(100), nullable=False)                 # Full board name
    state_name = Column(String(50), nullable=False)                  # 'Telangana', 'Andhra Pradesh'
    website_url = Column(Text)                                       # Official website
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=ist_now)


class StateBoardResource(Base):
    """
    Track state board textbook PDFs and syllabus documents
    """
    __tablename__ = "state_board_resources"

    id = Column(Integer, primary_key=True, index=True)
    state_board_id = Column(Integer, ForeignKey("state_boards.id"))
    class_name = Column(String(10), nullable=False)
    subject = Column(String(100), nullable=False)
    medium = Column(String(20), nullable=False, default='English')   # 'English', 'Telugu', 'Hindi'
    resource_type = Column(String(20), nullable=False)               # 'textbook_pdf', 'syllabus_doc', 'question_bank'
    resource_url = Column(Text)
    pdf_available = Column(Boolean, default=False)
    last_verified = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=ist_now)

    __table_args__ = (
        UniqueConstraint('state_board_id', 'class_name', 'subject', 'medium', 'resource_type',
                        name='uix_state_board_resource'),
    )
