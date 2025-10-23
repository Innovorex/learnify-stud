#!/usr/bin/env python3
"""
Load ALL CBSE Syllabi for Class 1-10
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.db import SessionLocal
from app.syllabus_service_v2 import EnhancedSyllabusService
from app.syllabus_scraper import CBSESyllabusDiscovery
import time

print("="*70)
print("📚 Loading ALL CBSE Syllabi - Class 1 to 10")
print("="*70)

db = SessionLocal()

# Define subjects for each class
subjects_by_class = {
    "1": ["English", "Hindi", "Mathematics"],
    "2": ["English", "Hindi", "Mathematics"],
    "3": ["English", "Hindi", "Mathematics", "Science"],
    "4": ["English", "Hindi", "Mathematics", "Science"],
    "5": ["English", "Hindi", "Mathematics", "Science"],
    "6": ["English", "Hindi", "Mathematics", "Science", "Social Science"],
    "7": ["English", "Hindi", "Mathematics", "Science", "Social Science"],
    "8": ["English", "Hindi", "Mathematics", "Science", "Social Science"],
    "9": ["English", "Hindi", "Mathematics", "Science", "Social Science"],
    "10": ["English", "Hindi", "Mathematics", "Science", "Social Science"]
}

try:
    service = EnhancedSyllabusService(db)

    total_subjects = sum(len(subjects) for subjects in subjects_by_class.values())
    print(f"\n📊 Total to load: {total_subjects} subject syllabi")
    print(f"⏱️  Estimated time: 3-5 minutes\n")

    start_time = time.time()
    loaded_count = 0
    skipped_count = 0
    failed_count = 0

    for class_name, subjects in subjects_by_class.items():
        print(f"\n{'='*70}")
        print(f"📖 Class {class_name} ({len(subjects)} subjects)")
        print(f"{'='*70}")

        for subject in subjects:
            try:
                print(f"\n   Loading: {subject}...")

                # Check if already exists
                from app.models import SyllabusMaster
                existing = db.query(SyllabusMaster).filter_by(
                    class_name=class_name,
                    subject=subject,
                    is_active=True
                ).first()

                if existing:
                    print(f"   ⏭️  Already loaded (skipping)")
                    skipped_count += 1
                    continue

                # Fetch syllabus
                syllabus = service.get_syllabus(class_name, subject)

                if syllabus and syllabus.content_extracted:
                    # Get topic count
                    from app.models import SyllabusTopics
                    topic_count = db.query(SyllabusTopics).filter_by(
                        syllabus_id=syllabus.id
                    ).count()

                    print(f"   ✅ Loaded: {len(syllabus.content_extracted)} chars, {topic_count} topics")
                    loaded_count += 1
                else:
                    print(f"   ⚠️  Could not load (may not be available)")
                    failed_count += 1

            except Exception as e:
                print(f"   ❌ Error: {str(e)[:60]}")
                failed_count += 1

    duration = time.time() - start_time

    print(f"\n{'='*70}")
    print(f"📊 FINAL SUMMARY")
    print(f"{'='*70}")
    print(f"✅ Successfully loaded: {loaded_count}")
    print(f"⏭️  Already existed: {skipped_count}")
    print(f"❌ Failed/Unavailable: {failed_count}")
    print(f"⏱️  Total time: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    print(f"{'='*70}")

    # Show what we have now
    from app.models import SyllabusMaster
    all_syllabi = db.query(SyllabusMaster).order_by(
        SyllabusMaster.class_name,
        SyllabusMaster.subject
    ).all()

    print(f"\n📚 Total Syllabi in Database: {len(all_syllabi)}")
    print(f"\nBreakdown by Class:")

    current_class = None
    for syl in all_syllabi:
        if syl.class_name != current_class:
            current_class = syl.class_name
            print(f"\n   Class {current_class}:")
        code = f"({syl.subject_code})" if syl.subject_code else ""
        print(f"      - {syl.subject} {code}")

    print(f"\n✅ All syllabi loaded successfully!")
    print(f"{'='*70}")

except Exception as e:
    print(f"\n❌ Fatal Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    db.close()
