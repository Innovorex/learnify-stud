#!/usr/bin/env python3
"""
Load all missing CBSE syllabi for Classes 9-10
"""
import sys
from app.db import SessionLocal
from app.syllabus_service_v2 import EnhancedSyllabusService
from app.models import CurriculumCatalog, SyllabusMaster

def load_missing_syllabi():
    db = SessionLocal()
    service = EnhancedSyllabusService(db)

    print("=" * 70)
    print("🔄 LOADING MISSING CLASS 9-10 SYLLABI")
    print("=" * 70)

    # All subjects available in catalog for secondary stage
    all_subjects = [
        "English", "Hindi", "Mathematics", "Science",
        "Physics", "Chemistry", "Biology",
        "History", "Geography", "Economics",
        "Accountancy", "Business Studies",
        "Psychology", "Sociology"
    ]

    classes = ['9', '10']

    success_count = 0
    skip_count = 0
    fail_count = 0

    for class_name in classes:
        print(f"\n{'='*70}")
        print(f"📚 CLASS {class_name}")
        print(f"{'='*70}")

        for subject in all_subjects:
            print(f"\n   Loading: {subject}...")

            # Check if already exists
            existing = db.query(SyllabusMaster).filter(
                SyllabusMaster.class_name == class_name,
                SyllabusMaster.subject.ilike(subject),
                SyllabusMaster.is_active == True
            ).first()

            if existing:
                print(f"   ⏭️  Already loaded (skipping)")
                skip_count += 1
                continue

            try:
                # Determine academic year and stage
                academic_year = service._get_current_academic_year()
                stage = 'secondary' if class_name in ['9', '10'] else 'sr_secondary'

                # Fetch and store
                result = service.fetch_and_store_syllabus(
                    class_name=class_name,
                    subject=subject,
                    academic_year=academic_year,
                    stage=stage
                )

                if result:
                    # Get the stored syllabus to check
                    syllabus = service.get_syllabus(class_name, subject)
                    if syllabus:
                        content_len = len(syllabus.content_extracted) if syllabus.content_extracted else 0
                        from app.models import SyllabusTopics
                        topic_count = db.query(SyllabusTopics).filter_by(syllabus_id=syllabus.id).count()
                        print(f"   ✅ Loaded: {content_len:,} chars, {topic_count} topics")
                        success_count += 1
                    else:
                        print(f"   ⚠️  Stored but cannot retrieve")
                        fail_count += 1
                else:
                    print(f"   ⚠️  Could not load (may not be available)")
                    fail_count += 1

            except Exception as e:
                print(f"   ❌ Error: {str(e)[:100]}")
                fail_count += 1

    print("\n" + "=" * 70)
    print("📊 FINAL SUMMARY")
    print("=" * 70)
    print(f"✅ Successfully loaded: {success_count}")
    print(f"⏭️  Already existed: {skip_count}")
    print(f"❌ Failed/Unavailable: {fail_count}")
    print("=" * 70)

    # Show current database status
    print("\n📚 Total Syllabi in Database:")
    all_syllabi = db.query(SyllabusMaster).filter(SyllabusMaster.is_active == True).all()

    by_class = {}
    for s in all_syllabi:
        if s.class_name not in by_class:
            by_class[s.class_name] = []
        by_class[s.class_name].append(s)

    print("\nBreakdown by Class:\n")
    for class_name in sorted(by_class.keys()):
        print(f"   Class {class_name}:")
        for s in sorted(by_class[class_name], key=lambda x: x.subject):
            print(f"      - {s.subject} ({s.subject_code or 'N/A'})")

    print("\n" + "=" * 70)
    print("✅ All available syllabi loaded!")
    print("=" * 70)

    db.close()

if __name__ == "__main__":
    load_missing_syllabi()
