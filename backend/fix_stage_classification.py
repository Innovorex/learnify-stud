#!/usr/bin/env python3
"""
Fix stage classification for CBSE syllabi
- Detect SrSec (Classes 11-12) vs Sec (Classes 9-10) from PDF URLs
- Update catalog and syllabus_master tables
"""
from app.db import SessionLocal
from app.models import CurriculumCatalog, SyllabusMaster

def fix_stage_classification():
    db = SessionLocal()

    print("=" * 70)
    print("🔧 FIXING STAGE CLASSIFICATION")
    print("=" * 70)

    # Step 1: Fix curriculum_catalog
    print("\n📋 Step 1: Fixing curriculum_catalog...")
    catalog_entries = db.query(CurriculumCatalog).filter(
        CurriculumCatalog.is_active == True
    ).all()

    catalog_fixed = 0
    for entry in catalog_entries:
        # Detect actual stage from PDF URL
        if 'SrSec' in entry.pdf_url:
            correct_stage = 'sr_secondary'
        elif 'Sec' in entry.pdf_url:
            correct_stage = 'secondary'
        else:
            continue

        if entry.stage != correct_stage:
            print(f"   Fixing: {entry.subject_display_name}")
            print(f"      {entry.stage} → {correct_stage}")
            entry.stage = correct_stage
            catalog_fixed += 1

    db.commit()
    print(f"\n   ✅ Fixed {catalog_fixed} catalog entries")

    # Step 2: Fix syllabus_master
    print("\n📚 Step 2: Fixing syllabus_master...")

    # Map subjects to their correct stage and classes
    subject_mapping = {
        # Classes 9-10 (Secondary)
        'English': {'stage': 'secondary', 'classes': ['9', '10']},
        'Hindi': {'stage': 'secondary', 'classes': ['9', '10']},
        'Mathematics': {'stage': 'secondary', 'classes': ['9', '10']},
        'Science': {'stage': 'secondary', 'classes': ['9', '10']},

        # Classes 11-12 (Sr. Secondary)
        'Physics': {'stage': 'sr_secondary', 'classes': ['11', '12']},
        'Chemistry': {'stage': 'sr_secondary', 'classes': ['11', '12']},
        'Biology': {'stage': 'sr_secondary', 'classes': ['11', '12']},
        'History': {'stage': 'sr_secondary', 'classes': ['11', '12']},
        'Geography': {'stage': 'sr_secondary', 'classes': ['11', '12']},
        'Economics': {'stage': 'sr_secondary', 'classes': ['11', '12']},
        'Business Studies': {'stage': 'sr_secondary', 'classes': ['11', '12']},
        'Accountancy': {'stage': 'sr_secondary', 'classes': ['11', '12']},
        'Psychology': {'stage': 'sr_secondary', 'classes': ['11', '12']},
        'Sociology': {'stage': 'sr_secondary', 'classes': ['11', '12']},
    }

    syllabi_fixed = 0
    syllabi_removed = 0

    for subject, info in subject_mapping.items():
        syllabi = db.query(SyllabusMaster).filter(
            SyllabusMaster.subject.ilike(subject),
            SyllabusMaster.is_active == True
        ).all()

        for syllabus in syllabi:
            correct_stage = info['stage']

            # If class_name is 9 or 10 but subject is sr_secondary
            if syllabus.class_name in ['9', '10'] and correct_stage == 'sr_secondary':
                print(f"   Removing: Class {syllabus.class_name} {subject} (actually for Classes 11-12)")
                syllabus.is_active = False
                syllabi_removed += 1

            # If class_name is 11 or 12 but subject is secondary
            elif syllabus.class_name in ['11', '12'] and correct_stage == 'secondary':
                print(f"   Removing: Class {syllabus.class_name} {subject} (actually for Classes 9-10)")
                syllabus.is_active = False
                syllabi_removed += 1

            # Fix stage field
            elif syllabus.stage != correct_stage:
                print(f"   Fixing stage: {subject} - {syllabus.stage} → {correct_stage}")
                syllabus.stage = correct_stage
                syllabi_fixed += 1

    db.commit()
    print(f"\n   ✅ Fixed {syllabi_fixed} syllabus stages")
    print(f"   ✅ Removed {syllabi_removed} incorrectly classified syllabi")

    # Step 3: Show final state
    print("\n" + "=" * 70)
    print("📊 FINAL STATE AFTER FIXING")
    print("=" * 70)

    for stage, class_range in [('secondary', '9-10'), ('sr_secondary', '11-12')]:
        syllabi = db.query(SyllabusMaster).filter(
            SyllabusMaster.stage == stage,
            SyllabusMaster.is_active == True
        ).order_by(SyllabusMaster.class_name, SyllabusMaster.subject).all()

        if syllabi:
            # Group by class
            by_class = {}
            for s in syllabi:
                if s.class_name not in by_class:
                    by_class[s.class_name] = []
                by_class[s.class_name].append(s)

            print(f"\n📘 {stage.upper().replace('_', ' ')} (Classes {class_range}):")
            for class_name in sorted(by_class.keys()):
                print(f"\n   Class {class_name}: {len(by_class[class_name])} subjects")
                for s in sorted(by_class[class_name], key=lambda x: x.subject):
                    print(f"      - {s.subject} (Code: {s.subject_code or 'N/A'})")

    print("\n" + "=" * 70)
    print("✅ STAGE CLASSIFICATION FIXED!")
    print("=" * 70)

    db.close()

if __name__ == "__main__":
    fix_stage_classification()
