#!/usr/bin/env python3
"""
Load NCERT-based syllabus structure for Classes 1-8 into database
"""
from app.db import SessionLocal
from app.models import SyllabusMaster, SyllabusTopics
from datetime import datetime
import hashlib
from ncert_class_1_8_structure import NCERT_SYLLABUS_STRUCTURE

def load_ncert_syllabi():
    db = SessionLocal()

    print("=" * 70)
    print("📚 LOADING NCERT SYLLABI FOR CLASSES 1-8")
    print("=" * 70)

    total_subjects = 0
    total_chapters = 0

    for class_num in range(1, 9):
        class_str = str(class_num)
        syllabus_data = NCERT_SYLLABUS_STRUCTURE.get(class_str, {})

        print(f"\n{'='*70}")
        print(f"📘 CLASS {class_num}")
        print(f"{'='*70}")

        for subject, subject_data in syllabus_data.items():
            print(f"\n📖 {subject}...")

            chapters = subject_data.get('chapters', [])
            subject_code = subject_data.get('subject_code', 'N/A')

            # Create synthetic syllabus content
            content = f"NCERT {subject} Syllabus for Class {class_num}\\n\\n"
            content += f"Subject Code: {subject_code}\\n\\n"
            content += "This syllabus is based on NCERT curriculum framework.\\n\\n"

            for i, chapter in enumerate(chapters, 1):
                content += f"{i}. {chapter}\\n"

            # Compute content hash
            content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

            # Check if already exists
            existing = db.query(SyllabusMaster).filter(
                SyllabusMaster.class_name == class_str,
                SyllabusMaster.subject.ilike(subject),
                SyllabusMaster.is_active == True
            ).first()

            if existing:
                print(f"   ⏭️  Already exists, skipping")
                continue

            # Determine stage
            if class_num <= 5:
                stage = 'primary'
            elif class_num <= 8:
                stage = 'middle'
            else:
                stage = 'secondary'

            # Create syllabus master entry
            syllabus = SyllabusMaster(
                board='CBSE',
                class_name=class_str,
                subject=subject,
                subject_code=subject_code,
                stage=stage,
                academic_year='2024-25',
                content_extracted=content,
                content_sha256=content_hash,
                last_updated=datetime.now(),
                is_active=True
            )

            db.add(syllabus)
            db.flush()  # Get the ID

            # Add chapters
            for i, chapter_name in enumerate(chapters, 1):
                topic = SyllabusTopics(
                    syllabus_id=syllabus.id,
                    chapter_number=i,
                    chapter_name=chapter_name,
                    sequence_order=i,
                    is_chapter=True,
                    content_details=f"Chapter {i}: {chapter_name}\\n\\nThis chapter is part of the NCERT {subject} curriculum for Class {class_num}."
                )
                db.add(topic)

            db.commit()

            print(f"   ✅ Loaded: {len(chapters)} chapters")
            total_subjects += 1
            total_chapters += len(chapters)

    print("\n" + "=" * 70)
    print("📊 FINAL SUMMARY")
    print("=" * 70)
    print(f"✅ Total subjects loaded: {total_subjects}")
    print(f"📚 Total chapters loaded: {total_chapters}")
    print("=" * 70)

    # Show complete status
    print("\n📋 COMPLETE STATUS BY CLASS:\n")
    for class_num in range(1, 9):
        syllabi = db.query(SyllabusMaster).filter(
            SyllabusMaster.class_name == str(class_num),
            SyllabusMaster.is_active == True
        ).all()

        chapter_count = sum([
            db.query(SyllabusTopics).filter_by(syllabus_id=s.id).count()
            for s in syllabi
        ])

        print(f"   Class {class_num}: {len(syllabi)} subjects, {chapter_count} chapters")

    print("\n" + "=" * 70)
    print("✅ NCERT CLASSES 1-8 LOADED SUCCESSFULLY!")
    print("=" * 70)

    db.close()

if __name__ == "__main__":
    load_ncert_syllabi()
