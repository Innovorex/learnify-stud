#!/usr/bin/env python3
"""
Test script to verify CBSE syllabus system is working
"""

import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from app.db import SessionLocal
from app.syllabus_scraper import CBSESyllabusDiscovery
from app.syllabus_service_v2 import EnhancedSyllabusService
from app.models import CurriculumCatalog, SyllabusMaster, SyllabusTopics

print("="*70)
print("🧪 CBSE Syllabus System - Comprehensive Test")
print("="*70)

db = SessionLocal()

# Test 1: Check database tables
print("\n1️⃣ Testing Database Tables...")
try:
    catalog_count = db.query(CurriculumCatalog).count()
    syllabus_count = db.query(SyllabusMaster).count()
    topics_count = db.query(SyllabusTopics).count()
    print(f"   ✅ curriculum_catalog: {catalog_count} entries")
    print(f"   ✅ syllabus_master: {syllabus_count} entries")
    print(f"   ✅ syllabus_topics: {topics_count} entries")
except Exception as e:
    print(f"   ❌ Database error: {e}")
    db.close()
    sys.exit(1)

# Test 2: Catalog Discovery (limited test - just check if it runs)
print("\n2️⃣ Testing Catalog Discovery...")
try:
    scraper = CBSESyllabusDiscovery(db)
    current_year = scraper.get_current_academic_year()
    print(f"   ✅ Current academic year: {current_year}")
    print(f"   ℹ️  Skipping full discovery (too slow for test)")
except Exception as e:
    print(f"   ❌ Scraper error: {e}")

# Test 3: Enhanced Syllabus Service
print("\n3️⃣ Testing Enhanced Syllabus Service...")
try:
    service = EnhancedSyllabusService(db)
    print(f"   ✅ Service initialized")
    print(f"   ✅ PyMuPDF available: {service._extract_with_pymupdf is not None}")
except Exception as e:
    print(f"   ❌ Service error: {e}")

# Test 4: Get subjects for Class 10
print("\n4️⃣ Testing Subject Retrieval for Class 10...")
try:
    from app.syllabus_scraper import get_catalog_entry

    # Check if we have catalog entries
    stage = 'secondary'
    catalogs = db.query(CurriculumCatalog).filter_by(
        stage=stage,
        is_active=True
    ).limit(5).all()

    if catalogs:
        print(f"   ✅ Found {len(catalogs)} subjects in catalog:")
        for cat in catalogs:
            code = f"({cat.subject_code})" if cat.subject_code else ""
            print(f"      - {cat.subject_display_name} {code}")
    else:
        print(f"   ⚠️  No catalog entries yet (need to run discovery)")
        print(f"   📝 Running quick discovery test...")

        # Try discovering just the current year
        scraper = CBSESyllabusDiscovery(db)
        print(f"   ⏳ Discovering catalog for {current_year}...")
        count = scraper.discover_and_store(current_year)
        print(f"   ✅ Discovered {count} syllabus PDFs")

except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Try to get topics (will fetch if needed)
print("\n5️⃣ Testing Topic Retrieval (may take time if fetching)...")
try:
    service = EnhancedSyllabusService(db)

    # Check if we have any syllabus already
    existing = db.query(SyllabusMaster).first()

    if existing:
        print(f"   ✅ Found existing syllabus: Class {existing.class_name} - {existing.subject}")
        topics = service.get_topics(existing.class_name, existing.subject)
        print(f"   ✅ Topics loaded: {len(topics)} chapters")
        if topics:
            print(f"   📚 Sample topics:")
            for topic in topics[:3]:
                print(f"      - Ch {topic.chapter_number}: {topic.chapter_name}")
    else:
        print(f"   ℹ️  No syllabus in database yet")
        print(f"   ℹ️  Run: service.get_syllabus('10', 'Mathematics') to fetch")

except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "="*70)
print("📊 Test Summary")
print("="*70)

catalog_count = db.query(CurriculumCatalog).count()
syllabus_count = db.query(SyllabusMaster).count()
topics_count = db.query(SyllabusTopics).count()

print(f"Catalog Entries: {catalog_count}")
print(f"Syllabi Cached: {syllabus_count}")
print(f"Total Topics: {topics_count}")

if catalog_count > 0:
    print("\n✅ System is ready!")
    print("   Next: Fetch syllabus for a subject")
    print("   Example: service.get_syllabus('10', 'Mathematics')")
else:
    print("\n⚠️  System needs catalog discovery")
    print("   Run: scraper.discover_and_store('2024-25')")

print("="*70)

db.close()
