"""
CBSE Syllabus Catalog Discovery - Dynamic Year-Aware Scraper
============================================================
Automatically discovers syllabus PDFs from CBSE website for any academic year.
Handles URL changes, validates links, and populates curriculum_catalog table.
"""

import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
import time
from urllib.parse import urljoin
from sqlalchemy.orm import Session
from app.models import CurriculumCatalog, SyllabusFetchLog


class CBSESyllabusDiscovery:
    """
    Discovers and catalogs CBSE syllabus URLs dynamically
    """

    BASE_URL = "https://cbseacademic.nic.in"
    TIMEOUT = 30

    # Subject name normalization mapping
    SUBJECT_NORMALIZATION = {
        "mathematics": "Mathematics",
        "science": "Science",
        "social science": "Social Science",
        "english": "English",
        "hindi": "Hindi",
        "physics": "Physics",
        "chemistry": "Chemistry",
        "biology": "Biology",
        "accountancy": "Accountancy",
        "business studies": "Business Studies",
        "economics": "Economics",
        "computer science": "Computer Science",
        "information technology": "Information Technology",
        "political science": "Political Science",
        "history": "History",
        "geography": "Geography",
        "sociology": "Sociology",
        "psychology": "Psychology"
    }

    # CBSE subject code patterns
    SUBJECT_CODES = {
        "Mathematics": "041",
        "Science": "086",
        "Social Science": "087",
        "English": "184",
        "Physics": "042",
        "Chemistry": "043",
        "Biology": "044",
        "Accountancy": "055",
        "Business Studies": "054",
        "Economics": "030",
        "Computer Science": "083"
    }

    def __init__(self, db: Session):
        self.db = db
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_current_academic_year(self) -> str:
        """
        Determine current academic year (e.g., '2024-25')
        Academic year starts in April
        """
        now = datetime.now()
        if now.month >= 4:  # April onwards
            return f"{now.year}-{str(now.year + 1)[-2:]}"
        else:
            return f"{now.year - 1}-{str(now.year)[-2:]}"

    def discover_curriculum_page(self, academic_year: Optional[str] = None) -> str:
        """
        Find the curriculum page URL for a given academic year
        Example: curriculum_2025.html or curriculum.html
        """
        if not academic_year:
            academic_year = self.get_current_academic_year()

        year_short = academic_year.split('-')[0][-2:]  # '24' from '2024-25'

        # Try multiple URL patterns
        patterns = [
            f"/curriculum_{year_short}.html",
            f"/curriculum_20{year_short}.html",
            "/curriculum.html",
            "/web_material/Curriculum.aspx"
        ]

        for pattern in patterns:
            url = self.BASE_URL + pattern
            try:
                response = self.session.get(url, timeout=self.TIMEOUT)
                if response.status_code == 200:
                    print(f"✅ Found curriculum page: {url}")
                    return url
            except:
                continue

        # Fallback: scrape from main academic page
        return self.BASE_URL + "/curriculum.html"

    def extract_pdf_links(self, html_content: str, base_url: str) -> List[Dict]:
        """
        Extract all PDF links from curriculum page
        Returns: [{"url": "...", "text": "Mathematics IX-X", "stage": "secondary"}]
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        pdf_links = []

        # Find all PDF links
        for link in soup.find_all('a', href=re.compile(r'\.pdf$', re.I)):
            href = link.get('href')
            text = link.get_text(strip=True)

            if not href or not text:
                continue

            # Make absolute URL
            full_url = urljoin(base_url, href)

            # Determine stage from URL or text
            stage = self._determine_stage(full_url, text)

            # Extract subject name
            subject_name = self._extract_subject_name(text, href)

            if subject_name:
                pdf_links.append({
                    'url': full_url,
                    'text': text,
                    'subject': subject_name,
                    'stage': stage,
                    'filename': href.split('/')[-1]
                })

        return pdf_links

    def _determine_stage(self, url: str, text: str) -> str:
        """
        Determine if this is secondary (IX-X) or senior secondary (XI-XII)
        """
        combined = (url + " " + text).lower()

        if any(x in combined for x in ['ix-x', '9-10', 'secondary', 'class_ix']):
            return 'secondary'
        elif any(x in combined for x in ['xi-xii', '11-12', 'sr_secondary', 'senior']):
            return 'sr_secondary'

        # Default based on common patterns
        if 'srsecondary' in url.lower() or 'senior' in url.lower():
            return 'sr_secondary'
        return 'secondary'

    def _extract_subject_name(self, link_text: str, filename: str) -> Optional[str]:
        """
        Extract normalized subject name from link text or filename
        """
        combined = (link_text + " " + filename).lower()

        for key, normalized in self.SUBJECT_NORMALIZATION.items():
            if key in combined:
                return normalized

        return None

    def discover_and_store(self, academic_year: Optional[str] = None,
                          force_refresh: bool = False) -> int:
        """
        Main method: Discover all syllabus PDFs and store in curriculum_catalog
        Returns: Number of entries added/updated
        """
        if not academic_year:
            academic_year = self.get_current_academic_year()

        start_time = time.time()

        print(f"\n{'='*60}")
        print(f"🔍 Discovering CBSE Syllabus Catalog for {academic_year}")
        print(f"{'='*60}\n")

        # Create log entry
        log = SyllabusFetchLog(
            board='CBSE',
            academic_year=academic_year,
            fetch_status='pending',
            source='syllabus_scraper'
        )
        self.db.add(log)
        self.db.commit()

        try:
            # 1. Find curriculum page
            curriculum_url = self.discover_curriculum_page(academic_year)

            # 2. Fetch page content
            response = self.session.get(curriculum_url, timeout=self.TIMEOUT)
            response.raise_for_status()

            log.http_status = response.status_code

            # 3. Extract PDF links
            pdf_links = self.extract_pdf_links(response.text, curriculum_url)

            print(f"📚 Found {len(pdf_links)} syllabus PDFs\n")

            # 4. Store in database
            added_count = 0
            for pdf_info in pdf_links:
                try:
                    # Check if already exists
                    existing = self.db.query(CurriculumCatalog).filter_by(
                        academic_year=academic_year,
                        stage=pdf_info['stage'],
                        subject_display_name=pdf_info['subject']
                    ).first()

                    if existing and not force_refresh:
                        print(f"  ⏭️  Skipping {pdf_info['subject']} ({pdf_info['stage']}) - already exists")
                        continue

                    # Verify PDF is accessible
                    if not self._verify_pdf_url(pdf_info['url']):
                        print(f"  ❌ Failed to verify: {pdf_info['subject']}")
                        continue

                    subject_code = self.SUBJECT_CODES.get(pdf_info['subject'])

                    if existing:
                        # Update existing
                        existing.pdf_url = pdf_info['url']
                        existing.pdf_filename = pdf_info['filename']
                        existing.last_verified = datetime.now()
                        print(f"  🔄 Updated: {pdf_info['subject']} ({pdf_info['stage']})")
                    else:
                        # Create new
                        catalog_entry = CurriculumCatalog(
                            academic_year=academic_year,
                            stage=pdf_info['stage'],
                            subject_display_name=pdf_info['subject'],
                            subject_code=subject_code,
                            pdf_url=pdf_info['url'],
                            pdf_filename=pdf_info['filename'],
                            last_verified=datetime.now()
                        )
                        self.db.add(catalog_entry)
                        print(f"  ✅ Added: {pdf_info['subject']} ({pdf_info['stage']}) - Code: {subject_code or 'N/A'}")

                    # Commit each entry individually to handle duplicates gracefully
                    self.db.commit()
                    added_count += 1

                except Exception as e:
                    # Rollback on error and continue with next entry
                    self.db.rollback()
                    print(f"  ⚠️  Skipped {pdf_info['subject']} - {str(e)[:50]}")

            # Update log
            duration_ms = int((time.time() - start_time) * 1000)
            log.fetch_status = 'success'
            log.duration_ms = duration_ms
            log.completed_at = datetime.now()
            self.db.commit()

            print(f"\n{'='*60}")
            print(f"✅ Catalog discovery completed!")
            print(f"   Added/Updated: {added_count} entries")
            print(f"   Duration: {duration_ms}ms")
            print(f"{'='*60}\n")

            return added_count

        except Exception as e:
            log.fetch_status = 'failed'
            log.error_message = str(e)
            log.error_type = type(e).__name__
            self.db.commit()

            print(f"❌ Discovery failed: {e}")
            return 0

    def _verify_pdf_url(self, url: str) -> bool:
        """
        Quick HEAD request to verify PDF is accessible
        """
        try:
            response = self.session.head(url, timeout=10, allow_redirects=True)
            return response.status_code == 200
        except:
            return False

    def get_catalog_for_subject(self, subject: str, class_name: str,
                               academic_year: Optional[str] = None) -> Optional[CurriculumCatalog]:
        """
        Retrieve catalog entry for a specific subject
        If not found, trigger discovery
        """
        if not academic_year:
            academic_year = self.get_current_academic_year()

        stage = 'secondary' if class_name in ['9', '10'] else 'sr_secondary'

        # Try to find in catalog (case-insensitive)
        catalog = self.db.query(CurriculumCatalog).filter(
            CurriculumCatalog.academic_year == academic_year,
            CurriculumCatalog.stage == stage,
            CurriculumCatalog.subject_display_name.ilike(subject),
            CurriculumCatalog.is_active == True
        ).first()

        if catalog:
            return catalog

        # Not found - trigger discovery
        print(f"⚠️  Catalog entry not found for {subject}, triggering discovery...")
        self.discover_and_store(academic_year)

        # Try again (case-insensitive)
        return self.db.query(CurriculumCatalog).filter(
            CurriculumCatalog.academic_year == academic_year,
            CurriculumCatalog.stage == stage,
            CurriculumCatalog.subject_display_name.ilike(subject),
            CurriculumCatalog.is_active == True
        ).first()

    def refresh_all_catalogs(self) -> Dict[str, int]:
        """
        Refresh catalogs for current and next academic year
        """
        current_year = self.get_current_academic_year()
        years = [current_year]

        # Calculate next year
        year_start = int(current_year.split('-')[0])
        next_year = f"{year_start + 1}-{str(year_start + 2)[-2:]}"
        years.append(next_year)

        results = {}
        for year in years:
            count = self.discover_and_store(year, force_refresh=True)
            results[year] = count

        return results


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def discover_syllabus_catalog(db: Session, academic_year: Optional[str] = None) -> int:
    """
    Convenience function to discover and store syllabus catalog
    Usage: discover_syllabus_catalog(db)
    """
    scraper = CBSESyllabusDiscovery(db)
    return scraper.discover_and_store(academic_year)


def get_catalog_entry(db: Session, subject: str, class_name: str,
                     academic_year: Optional[str] = None) -> Optional[CurriculumCatalog]:
    """
    Get catalog entry for a subject, auto-discover if needed
    """
    scraper = CBSESyllabusDiscovery(db)
    return scraper.get_catalog_for_subject(subject, class_name, academic_year)
