"""
Enhanced CBSE Syllabus Service v2.0
====================================
Production-ready syllabus management with:
- Dynamic URL resolution from curriculum_catalog
- PyMuPDF (fitz) for better PDF extraction (fallback to PyPDF2)
- SHA256 checksumming for version control
- Intelligent caching and updates
- Retry logic with exponential backoff
"""

import os
import re
import json
import hashlib
import time
import requests
from io import BytesIO
from typing import Optional, List, Dict, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# PDF extraction libraries (with fallbacks)
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    print("⚠️  PyMuPDF not available, falling back to PyPDF2")

import PyPDF2

from app.models import (
    SyllabusMaster, SyllabusTopics, SyllabusFetchLog,
    CurriculumCatalog, ist_now
)
from app.syllabus_scraper import CBSESyllabusDiscovery, get_catalog_entry
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


class EnhancedSyllabusService:
    """
    Production-ready syllabus service with advanced features
    """

    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    REQUEST_TIMEOUT = 30

    # Cache validity period
    CACHE_VALIDITY_DAYS = 180  # 6 months

    def __init__(self, db: Session):
        self.db = db
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    # ========================================================================
    # PDF EXTRACTION (with multiple fallbacks)
    # ========================================================================

    def extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """
        Extract text from PDF using best available method
        Priority: PyMuPDF > PyPDF2
        """
        if HAS_PYMUPDF:
            text = self._extract_with_pymupdf(pdf_content)
            if text and len(text.strip()) > 100:
                print("  ✅ Extracted with PyMuPDF")
                return text

        # Fallback to PyPDF2
        text = self._extract_with_pypdf2(pdf_content)
        if text:
            print("  ✅ Extracted with PyPDF2")
        return text

    def _extract_with_pymupdf(self, pdf_content: bytes) -> Optional[str]:
        """
        Extract text using PyMuPDF (fitz) - better formatting
        """
        try:
            text = ""
            with fitz.open(stream=pdf_content, filetype="pdf") as doc:
                for page_num, page in enumerate(doc):
                    # Extract text with layout preservation
                    page_text = page.get_text("text")
                    text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
            return text
        except Exception as e:
            print(f"  ⚠️  PyMuPDF extraction failed: {e}")
            return None

    def _extract_with_pypdf2(self, pdf_content: bytes) -> Optional[str]:
        """
        Fallback: Extract text using PyPDF2
        """
        try:
            pdf_file = BytesIO(pdf_content)
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
            return text
        except Exception as e:
            print(f"  ❌ PyPDF2 extraction failed: {e}")
            return None

    # ========================================================================
    # SHA256 CHECKSUMMING
    # ========================================================================

    def compute_sha256(self, content: bytes) -> str:
        """
        Compute SHA256 checksum of PDF content
        """
        return hashlib.sha256(content).hexdigest()

    def has_syllabus_changed(self, syllabus_id: int, new_content_hash: str) -> bool:
        """
        Check if syllabus content has changed based on SHA256
        """
        syllabus = self.db.query(SyllabusMaster).filter_by(id=syllabus_id).first()
        if not syllabus:
            return True

        if syllabus.content_sha256 != new_content_hash:
            print(f"  🔄 Content changed! Old: {syllabus.content_sha256[:16]}... New: {new_content_hash[:16]}...")
            return True

        return False

    # ========================================================================
    # ENHANCED PDF FETCHING (with retry logic)
    # ========================================================================

    def fetch_pdf_with_retry(self, url: str, max_retries: int = MAX_RETRIES) -> Optional[bytes]:
        """
        Fetch PDF with exponential backoff retry logic
        """
        for attempt in range(1, max_retries + 1):
            try:
                print(f"  📥 Fetching PDF (attempt {attempt}/{max_retries})...")
                response = self.session.get(url, timeout=self.REQUEST_TIMEOUT)
                response.raise_for_status()

                # Verify it's actually a PDF
                content_type = response.headers.get('Content-Type', '')
                if 'pdf' not in content_type.lower() and not url.endswith('.pdf'):
                    print(f"  ⚠️  Warning: Content-Type is {content_type}")

                return response.content

            except requests.exceptions.RequestException as e:
                print(f"  ❌ Attempt {attempt} failed: {e}")

                if attempt < max_retries:
                    delay = self.RETRY_DELAY * (2 ** (attempt - 1))  # Exponential backoff
                    print(f"  ⏳ Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    print(f"  ❌ All {max_retries} attempts failed")
                    return None

        return None

    # ========================================================================
    # DYNAMIC URL RESOLUTION (using curriculum_catalog)
    # ========================================================================

    def get_syllabus_url(self, class_name: str, subject: str,
                        academic_year: Optional[str] = None) -> Optional[str]:
        """
        Get syllabus URL from curriculum_catalog
        Auto-discovers if not found
        """
        catalog_entry = get_catalog_entry(self.db, subject, class_name, academic_year)

        if catalog_entry:
            return catalog_entry.pdf_url

        print(f"  ⚠️  No catalog entry found for Class {class_name} - {subject}")
        return None

    # ========================================================================
    # INTELLIGENT SYLLABUS RETRIEVAL
    # ========================================================================

    def get_syllabus(self, class_name: str, subject: str,
                    academic_year: Optional[str] = None,
                    force_refresh: bool = False,
                    board_code: Optional[str] = None,
                    medium: Optional[str] = None,
                    language_position: Optional[str] = None) -> Optional[SyllabusMaster]:
        """
        Smart syllabus retrieval (supports CBSE and State Boards):
        1. Check cache (if valid and not expired)
        2. If not found or expired → fetch from CBSE
        3. If content changed (SHA256) → re-parse

        Params:
        - board_code: 'CBSE' (default), 'TSBSE', 'BSEAP', etc.
        - medium: 'English' (default), 'Telugu', 'Hindi', etc.
        - language_position: 'FL' (First), 'SL' (Second), 'TL' (Third), or None for core subjects
        """
        if not academic_year:
            academic_year = self._get_current_academic_year()

        # Determine stage based on class
        class_num = int(class_name) if class_name.isdigit() else 0
        if class_num <= 5:
            stage = 'primary'
        elif class_num <= 8:
            stage = 'middle'
        elif class_num <= 10:
            stage = 'secondary'
        else:
            stage = 'sr_secondary'

        # Build query for database lookup
        query = self.db.query(SyllabusMaster).filter(
            SyllabusMaster.class_name == class_name,
            SyllabusMaster.subject.ilike(subject),
            SyllabusMaster.is_active == True
        )

        # Filter by board if specified
        if board_code:
            query = query.filter(SyllabusMaster.board == board_code)
        else:
            # Default to CBSE
            query = query.filter(SyllabusMaster.board == 'CBSE')

        # Filter by medium if specified (for state boards)
        if medium:
            query = query.filter(SyllabusMaster.medium.ilike(medium))

        # Filter by language_position for Classes 6-10 (Three Language Formula)
        if language_position:
            query = query.filter(SyllabusMaster.language_position == language_position)
        elif class_num >= 6:
            # For core subjects (Math, Science, etc.), ensure no language position
            query = query.filter(SyllabusMaster.language_position.is_(None))

        syllabus = query.first()

        # If found, return it (for Classes 1-8 NCERT and State Boards, we don't have PDFs to refresh)
        if syllabus:
            cache_age = datetime.now() - syllabus.last_updated.replace(tzinfo=None)

            # For Classes 1-8 (NCERT/State Board), always use cached (no PDF to refresh)
            if class_num <= 8:
                board_type = syllabus.board_type if syllabus.board_type else 'CBSE'
                print(f"✅ Using {board_type} syllabus for Class {class_name}")
                return syllabus

            # For Classes 9-10 (CBSE), check cache validity
            if not force_refresh and cache_age.days < self.CACHE_VALIDITY_DAYS:
                print(f"✅ Using cached syllabus (age: {cache_age.days} days)")
                return syllabus
            elif force_refresh or cache_age.days >= self.CACHE_VALIDITY_DAYS:
                print(f"🔄 Fetching fresh syllabus for Class {class_name} - {subject}...")
                return self.fetch_and_store_syllabus(class_name, subject, academic_year, stage)

        # Not found in database - try to fetch (only works for CBSE Classes 9-12 with PDFs)
        if class_num >= 9 and (not board_code or board_code == 'CBSE'):
            print(f"🔄 Fetching fresh syllabus for Class {class_name} - {subject}...")
            return self.fetch_and_store_syllabus(class_name, subject, academic_year, stage)
        else:
            board_info = f"{board_code} " if board_code else ""
            print(f"⚠️ No syllabus found for {board_info}Class {class_name} - {subject}")
            return None

    # ========================================================================
    # COMPLETE FETCH & STORE WORKFLOW
    # ========================================================================

    def fetch_and_store_syllabus(self, class_name: str, subject: str,
                                academic_year: str, stage: str) -> Optional[SyllabusMaster]:
        """
        Complete workflow: Fetch → Extract → Checksum → Parse → Store
        """
        start_time = time.time()

        # Create log entry
        log = SyllabusFetchLog(
            board='CBSE',
            class_name=class_name,
            subject=subject,
            academic_year=academic_year,
            fetch_status='pending',
            source='syllabus_service_v2'
        )
        self.db.add(log)
        self.db.commit()

        try:
            # 1. Get URL from catalog
            url = self.get_syllabus_url(class_name, subject, academic_year)
            if not url:
                raise ValueError("No PDF URL found in catalog")

            log.source = url

            # 2. Fetch PDF with retry
            pdf_content = self.fetch_pdf_with_retry(url)
            if not pdf_content:
                raise ValueError("Failed to fetch PDF after retries")

            log.http_status = 200

            # 3. Compute SHA256 checksum
            content_hash = self.compute_sha256(pdf_content)
            print(f"  🔐 SHA256: {content_hash[:16]}...")

            # 4. Check if syllabus already exists (case-insensitive)
            existing = self.db.query(SyllabusMaster).filter(
                SyllabusMaster.class_name == class_name,
                SyllabusMaster.subject.ilike(subject),
                SyllabusMaster.academic_year == academic_year
            ).first()

            # If exists and hash matches → skip
            if existing and existing.content_sha256 == content_hash:
                print(f"  ✅ Syllabus unchanged (SHA256 match)")
                existing.last_updated = ist_now()
                self.db.commit()

                log.fetch_status = 'success'
                log.duration_ms = int((time.time() - start_time) * 1000)
                log.completed_at = ist_now()
                self.db.commit()

                return existing

            # 5. Extract text
            print("  📄 Extracting text from PDF...")
            syllabus_text = self.extract_text_from_pdf(pdf_content)
            if not syllabus_text or len(syllabus_text.strip()) < 100:
                raise ValueError("PDF extraction failed or content too short")

            # 6. Get catalog entry for subject code
            catalog = get_catalog_entry(self.db, subject, class_name, academic_year)
            subject_code = catalog.subject_code if catalog else None

            # 7. Update or create syllabus master
            if existing:
                existing.content_extracted = syllabus_text
                existing.content_sha256 = content_hash
                existing.pdf_url = url
                existing.subject_code = subject_code
                existing.stage = stage
                existing.last_updated = ist_now()
                syllabus_master = existing
                print(f"  🔄 Updated existing syllabus")
            else:
                syllabus_master = SyllabusMaster(
                    class_name=class_name,
                    subject=subject,
                    subject_code=subject_code,
                    stage=stage,
                    academic_year=academic_year,
                    pdf_url=url,
                    content_extracted=syllabus_text,
                    content_sha256=content_hash,
                    catalog_id=catalog.id if catalog else None
                )
                self.db.add(syllabus_master)
                print(f"  ✅ Created new syllabus entry")

            self.db.commit()
            self.db.refresh(syllabus_master)

            # 8. Parse and store topics (if new or changed)
            if not existing or existing.content_sha256 != content_hash:
                print("  🤖 Parsing syllabus structure with AI...")
                self.parse_and_store_topics(syllabus_master, syllabus_text)

            # Update log
            duration_ms = int((time.time() - start_time) * 1000)
            log.fetch_status = 'success'
            log.duration_ms = duration_ms
            log.completed_at = ist_now()
            self.db.commit()

            print(f"  ✅ Syllabus stored successfully ({duration_ms}ms)")
            return syllabus_master

        except Exception as e:
            # Log error
            log.fetch_status = 'failed'
            log.error_message = str(e)
            log.error_type = type(e).__name__
            log.duration_ms = int((time.time() - start_time) * 1000)
            log.completed_at = ist_now()
            self.db.commit()

            print(f"  ❌ Fetch and store failed: {e}")
            return None

    # ========================================================================
    # AI-POWERED SYLLABUS PARSING
    # ========================================================================

    def parse_and_store_topics(self, syllabus_master: SyllabusMaster,
                              syllabus_text: str):
        """
        Use AI to parse syllabus into structured topics
        """
        # Delete old topics if re-parsing
        self.db.query(SyllabusTopics).filter_by(
            syllabus_id=syllabus_master.id
        ).delete()
        self.db.commit()

        # Parse with AI
        structured_data = self._parse_with_ai(
            syllabus_text,
            syllabus_master.class_name,
            syllabus_master.subject
        )

        if not structured_data:
            print("  ⚠️  AI parsing returned no data")
            return

        # Store topics
        sequence = 0
        for unit in structured_data:
            for chapter in unit.get("chapters", []):
                sequence += 1

                topic = SyllabusTopics(
                    syllabus_id=syllabus_master.id,
                    unit_number=unit.get("unit_number"),
                    unit_name=unit.get("unit_name"),
                    chapter_number=chapter.get("chapter_number"),
                    chapter_name=chapter["chapter_name"],
                    topic_name=chapter.get("topic_name"),
                    subtopics=chapter.get("subtopics", []),
                    learning_outcomes=chapter.get("learning_outcomes", []),
                    key_concepts=chapter.get("key_concepts", []),
                    content_details=chapter.get("content_details"),
                    weightage=chapter.get("weightage"),
                    difficulty_level=chapter.get("difficulty_level", "medium"),
                    sequence_order=sequence,
                    is_chapter=True
                )
                self.db.add(topic)

        self.db.commit()
        print(f"  ✅ Stored {sequence} topics")

    def _parse_with_ai(self, syllabus_text: str, class_name: str,
                      subject: str) -> Optional[List[Dict]]:
        """
        Use OpenRouter AI to parse syllabus structure
        """
        # Truncate text if too long (to fit in context window)
        max_chars = 15000
        if len(syllabus_text) > max_chars:
            syllabus_text = syllabus_text[:max_chars] + "\n...[truncated]"

        prompt = f"""
Parse this CBSE Class {class_name} {subject} syllabus into structured JSON format.

Extract:
- Units with unit numbers and names
- Chapters with chapter numbers and names
- Topics and subtopics for each chapter
- Learning outcomes if mentioned
- Marks weightage if mentioned
- Key concepts

Return ONLY valid JSON array (no markdown):
[
  {{
    "unit_number": 1,
    "unit_name": "Number Systems",
    "chapters": [
      {{
        "chapter_number": 1,
        "chapter_name": "Real Numbers",
        "topic_name": "Real Numbers",
        "subtopics": ["Euclid's Division Lemma", "Fundamental Theorem of Arithmetic"],
        "key_concepts": ["HCF", "LCM", "Prime Factorization"],
        "learning_outcomes": ["Understand Euclid's algorithm", "Apply fundamental theorem"],
        "weightage": 6,
        "difficulty_level": "medium"
      }}
    ]
  }}
]

Syllabus text:
{syllabus_text}
"""

        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "openai/gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            data = response.json()

            if "error" in data:
                print(f"  ❌ AI parsing error: {data['error']}")
                return None

            content = data["choices"][0]["message"]["content"]

            # Extract JSON from markdown if present
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()

            # Parse JSON
            parsed = json.loads(json_str)
            return parsed

        except Exception as e:
            print(f"  ❌ AI parsing failed: {e}")
            return None

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def _get_current_academic_year(self) -> str:
        """Get current academic year (April-March cycle)"""
        now = datetime.now()
        if now.month >= 4:
            return f"{now.year}-{str(now.year + 1)[-2:]}"
        else:
            return f"{now.year - 1}-{str(now.year)[-2:]}"

    def get_topics(self, class_name: str, subject: str,
                  academic_year: Optional[str] = None) -> List[SyllabusTopics]:
        """
        Get all topics for a subject
        """
        syllabus = self.get_syllabus(class_name, subject, academic_year)
        if not syllabus:
            return []

        topics = self.db.query(SyllabusTopics).filter_by(
            syllabus_id=syllabus.id,
            is_chapter=True
        ).order_by(SyllabusTopics.sequence_order).all()

        return topics

    def get_topic_content(self, topic_id: int) -> Optional[Dict]:
        """
        Get detailed content for a specific topic
        """
        topic = self.db.query(SyllabusTopics).filter_by(id=topic_id).first()
        if not topic:
            return None

        syllabus = self.db.query(SyllabusMaster).filter_by(id=topic.syllabus_id).first()

        return {
            "id": topic.id,
            "chapter_name": topic.chapter_name,
            "unit_name": topic.unit_name,
            "subtopics": topic.subtopics,
            "learning_outcomes": topic.learning_outcomes,
            "key_concepts": topic.key_concepts,
            "content_details": topic.content_details,
            "full_syllabus_content": syllabus.content_extracted if syllabus else None,
            "weightage": topic.weightage,
            "difficulty_level": topic.difficulty_level
        }


# ========================================================================
# CONVENIENCE FUNCTIONS
# ========================================================================

def get_syllabus_service(db: Session) -> EnhancedSyllabusService:
    """Factory function to create syllabus service"""
    return EnhancedSyllabusService(db)
