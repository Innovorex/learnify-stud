"""
Syllabus Management API Routes
===============================
Endpoints for syllabus catalog discovery, topic browsing, and management
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.db import get_db
from app.models import SyllabusMaster, SyllabusTopics, CurriculumCatalog
from app.syllabus_service_v2 import EnhancedSyllabusService, get_syllabus_service
from app.syllabus_scraper import CBSESyllabusDiscovery, discover_syllabus_catalog


# ============================================================================
# SCHEMAS
# ============================================================================

class SubjectInfo(BaseModel):
    subject_name: str
    subject_code: Optional[str]
    stage: str

class TopicOut(BaseModel):
    id: int
    unit_number: Optional[int]
    unit_name: Optional[str]
    chapter_number: Optional[int]
    chapter_name: str
    subtopics: Optional[List[str]]
    learning_outcomes: Optional[List[str]]
    weightage: Optional[int]
    difficulty_level: Optional[str]

    class Config:
        from_attributes = True

class CatalogOut(BaseModel):
    id: int
    academic_year: str
    stage: str
    subject_display_name: str
    subject_code: Optional[str]
    pdf_url: str
    last_verified: Optional[str]

    class Config:
        from_attributes = True


# ============================================================================
# ROUTER
# ============================================================================

router = APIRouter(prefix="/syllabus", tags=["Syllabus"])


# ============================================================================
# CATALOG MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/discover-catalog/{academic_year}")
def discover_catalog(
    academic_year: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Trigger catalog discovery for an academic year
    Runs in background
    """
    background_tasks.add_task(discover_syllabus_catalog, db, academic_year)

    return {
        "message": f"Catalog discovery started for {academic_year}",
        "status": "in_progress"
    }


@router.get("/catalog", response_model=List[CatalogOut])
def get_all_catalog_entries(
    academic_year: Optional[str] = None,
    stage: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all curriculum catalog entries
    Optional filters: academic_year, stage
    """
    query = db.query(CurriculumCatalog).filter_by(is_active=True)

    if academic_year:
        query = query.filter_by(academic_year=academic_year)
    if stage:
        query = query.filter_by(stage=stage)

    catalogs = query.all()
    return catalogs


@router.get("/catalog/{class_name}", response_model=List[CatalogOut])
def get_catalog_by_class(class_name: str, db: Session = Depends(get_db)):
    """
    Get catalog entries for a specific class
    Automatically determines stage (secondary/sr_secondary)
    """
    stage = 'secondary' if class_name in ['9', '10'] else 'sr_secondary'

    catalogs = db.query(CurriculumCatalog).filter_by(
        stage=stage,
        is_active=True
    ).all()

    if not catalogs:
        # Try to discover
        scraper = CBSESyllabusDiscovery(db)
        scraper.discover_and_store()
        catalogs = db.query(CurriculumCatalog).filter_by(
            stage=stage,
            is_active=True
        ).all()

    return catalogs


# ============================================================================
# SUBJECT & TOPIC BROWSING ENDPOINTS
# ============================================================================

@router.get("/subjects/{class_name}")
def get_available_subjects(class_name: str, db: Session = Depends(get_db)):
    """
    Get all available subjects for a class with subject codes
    """
    stage = 'secondary' if class_name in ['9', '10'] else 'sr_secondary'

    # Get from catalog
    catalogs = db.query(CurriculumCatalog).filter_by(
        stage=stage,
        is_active=True
    ).distinct(CurriculumCatalog.subject_display_name).all()

    if not catalogs:
        # Trigger discovery
        scraper = CBSESyllabusDiscovery(db)
        scraper.discover_and_store()
        catalogs = db.query(CurriculumCatalog).filter_by(
            stage=stage,
            is_active=True
        ).distinct(CurriculumCatalog.subject_display_name).all()

    subjects = [
        {
            "subject_name": c.subject_display_name,
            "subject_code": c.subject_code,
            "stage": c.stage
        }
        for c in catalogs
    ]

    return {
        "class": class_name,
        "stage": stage,
        "subjects": subjects
    }


@router.get("/topics/{class_name}/{subject}", response_model=List[TopicOut])
def get_topics_for_subject(
    class_name: str,
    subject: str,
    academic_year: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all chapters/topics for a subject
    Auto-fetches syllabus if not cached
    """
    service = get_syllabus_service(db)

    # This will auto-fetch if not in cache
    topics = service.get_topics(class_name, subject, academic_year)

    if not topics:
        raise HTTPException(
            status_code=404,
            detail=f"No topics found for Class {class_name} - {subject}"
        )

    return topics


@router.get("/topic/{topic_id}")
def get_topic_details(topic_id: int, db: Session = Depends(get_db)):
    """
    Get detailed content for a specific topic/chapter
    Includes syllabus content for AI question generation
    """
    service = get_syllabus_service(db)
    content = service.get_topic_content(topic_id)

    if not content:
        raise HTTPException(status_code=404, detail="Topic not found")

    return content


# ============================================================================
# SYLLABUS MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/fetch/{class_name}/{subject}")
def force_fetch_syllabus(
    class_name: str,
    subject: str,
    academic_year: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Manually force-fetch and update syllabus for a subject
    Useful for refreshing content or fixing issues
    """
    service = get_syllabus_service(db)

    syllabus = service.get_syllabus(
        class_name, subject, academic_year, force_refresh=True
    )

    if not syllabus:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch syllabus for Class {class_name} - {subject}"
        )

    return {
        "message": "Syllabus fetched successfully",
        "id": syllabus.id,
        "class": syllabus.class_name,
        "subject": syllabus.subject,
        "academic_year": syllabus.academic_year,
        "sha256": syllabus.content_sha256[:16] + "...",
        "topics_count": db.query(SyllabusTopics).filter_by(
            syllabus_id=syllabus.id
        ).count()
    }


@router.get("/status/{class_name}/{subject}")
def get_syllabus_status(
    class_name: str,
    subject: str,
    academic_year: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Check status of syllabus in database
    Returns cache info, last update, version hash, etc.
    """
    if not academic_year:
        from app.syllabus_service_v2 import EnhancedSyllabusService
        service = EnhancedSyllabusService(db)
        academic_year = service._get_current_academic_year()

    syllabus = db.query(SyllabusMaster).filter_by(
        class_name=class_name,
        subject=subject,
        academic_year=academic_year,
        is_active=True
    ).first()

    if not syllabus:
        return {
            "status": "not_cached",
            "message": "Syllabus not in database"
        }

    from datetime import datetime
    cache_age_days = (datetime.now() - syllabus.last_updated.replace(tzinfo=None)).days

    topics_count = db.query(SyllabusTopics).filter_by(
        syllabus_id=syllabus.id
    ).count()

    return {
        "status": "cached",
        "id": syllabus.id,
        "class": syllabus.class_name,
        "subject": syllabus.subject,
        "subject_code": syllabus.subject_code,
        "academic_year": syllabus.academic_year,
        "last_updated": syllabus.last_updated.isoformat(),
        "cache_age_days": cache_age_days,
        "sha256": syllabus.content_sha256[:16] + "..." if syllabus.content_sha256 else None,
        "topics_count": topics_count,
        "pdf_url": syllabus.pdf_url
    }


@router.get("/hierarchy/{class_name}/{subject}")
def get_syllabus_hierarchy(
    class_name: str,
    subject: str,
    academic_year: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get complete syllabus hierarchy with units → chapters → subtopics
    """
    service = get_syllabus_service(db)
    syllabus = service.get_syllabus(class_name, subject, academic_year)

    if not syllabus:
        raise HTTPException(status_code=404, detail="Syllabus not found")

    topics = db.query(SyllabusTopics).filter_by(
        syllabus_id=syllabus.id
    ).order_by(SyllabusTopics.sequence_order).all()

    # Group by units
    units = {}
    for topic in topics:
        unit_key = f"{topic.unit_number}_{topic.unit_name}"
        if unit_key not in units:
            units[unit_key] = {
                "unit_number": topic.unit_number,
                "unit_name": topic.unit_name,
                "chapters": []
            }

        units[unit_key]["chapters"].append({
            "id": topic.id,
            "chapter_number": topic.chapter_number,
            "chapter_name": topic.chapter_name,
            "subtopics": topic.subtopics,
            "learning_outcomes": topic.learning_outcomes,
            "weightage": topic.weightage
        })

    return {
        "class": class_name,
        "subject": subject,
        "academic_year": syllabus.academic_year,
        "units": list(units.values())
    }


# ============================================================================
# ADMIN/MAINTENANCE ENDPOINTS
# ============================================================================

@router.post("/refresh-all")
def refresh_all_syllabi(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Refresh all syllabi in catalog (admin function)
    Runs in background
    """
    scraper = CBSESyllabusDiscovery(db)

    def refresh_task():
        scraper.refresh_all_catalogs()

    background_tasks.add_task(refresh_task)

    return {
        "message": "Full syllabus refresh started",
        "status": "in_progress"
    }


@router.get("/health")
def syllabus_system_health(db: Session = Depends(get_db)):
    """
    Check health of syllabus system
    """
    catalog_count = db.query(CurriculumCatalog).filter_by(is_active=True).count()
    syllabus_count = db.query(SyllabusMaster).filter_by(is_active=True).count()
    topics_count = db.query(SyllabusTopics).count()

    return {
        "status": "healthy",
        "catalog_entries": catalog_count,
        "syllabi_cached": syllabus_count,
        "total_topics": topics_count,
        "pymupdf_available": True  # Will be dynamically checked
    }
