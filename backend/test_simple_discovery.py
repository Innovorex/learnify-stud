#!/usr/bin/env python3
"""
Simple test: Discover CBSE catalog
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.db import SessionLocal
from app.syllabus_scraper import CBSESyllabusDiscovery

print("="*70)
print("🔍 CBSE Catalog Discovery Test")
print("="*70)

db = SessionLocal()

try:
    scraper = CBSESyllabusDiscovery(db)

    print("\n📅 Current academic year:", scraper.get_current_academic_year())

    print("\n⏳ Discovering CBSE syllabus PDFs for 2024-25...")
    print("   (This may take 30-60 seconds)\n")

    count = scraper.discover_and_store('2024-25', force_refresh=False)

    print(f"\n✅ Discovery completed!")
    print(f"   Found: {count} syllabus PDFs")

    # Show what was discovered
    from app.models import CurriculumCatalog
    catalogs = db.query(CurriculumCatalog).limit(10).all()

    if catalogs:
        print(f"\n📚 Sample discovered subjects:")
        for cat in catalogs:
            code = f"({cat.subject_code})" if cat.subject_code else ""
            print(f"   - {cat.subject_display_name} {code} [{cat.stage}]")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    db.close()

print("\n" + "="*70)
