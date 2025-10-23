#!/usr/bin/env python3
"""
Re-parse Class 9-10 syllabi to extract ALL chapters with detailed content
"""
from app.db import SessionLocal
from app.models import SyllabusMaster, SyllabusTopics
from app.syllabus_service_v2 import EnhancedSyllabusService

def reparse_all_chapters():
    db = SessionLocal()
    service = EnhancedSyllabusService(db)

    print("=" * 70)
    print("🔄 RE-PARSING CLASS 9-10 SYLLABI FOR COMPLETE CHAPTERS")
    print("=" * 70)

    classes = ['9', '10']
    subjects = ['English', 'Hindi', 'Mathematics', 'Science']

    total_parsed = 0
    total_chapters = 0

    for class_name in classes:
        print(f"\n{'='*70}")
        print(f"📚 CLASS {class_name}")
        print(f"{'='*70}")

        for subject in subjects:
            print(f"\n📖 {subject}...")

            # Get syllabus
            syllabus = db.query(SyllabusMaster).filter(
                SyllabusMaster.class_name == class_name,
                SyllabusMaster.subject.ilike(subject),
                SyllabusMaster.is_active == True
            ).first()

            if not syllabus:
                print(f"   ⚠️  Syllabus not found")
                continue

            print(f"   Content: {len(syllabus.content_extracted):,} chars")

            # Delete existing topics
            existing_count = db.query(SyllabusTopics).filter(
                SyllabusTopics.syllabus_id == syllabus.id
            ).count()

            if existing_count > 0:
                print(f"   🗑️  Deleting {existing_count} old chapters...")
                db.query(SyllabusTopics).filter(
                    SyllabusTopics.syllabus_id == syllabus.id
                ).delete()
                db.commit()

            # Re-parse with AI using the service's method
            print(f"   🤖 Re-parsing with AI...")

            try:
                # Use the built-in parse_and_store_topics method
                service.parse_and_store_topics(syllabus, syllabus.content_extracted)

                # Count topics added
                new_count = db.query(SyllabusTopics).filter(
                    SyllabusTopics.syllabus_id == syllabus.id
                ).count()

                if new_count > 0:
                    print(f"   ✅ Parsed {new_count} chapters")
                    total_chapters += new_count
                    total_parsed += 1

                    # Show chapter names
                    topics = db.query(SyllabusTopics).filter(
                        SyllabusTopics.syllabus_id == syllabus.id
                    ).limit(5).all()

                    for i, t in enumerate(topics, 1):
                        print(f"      {i}. {t.chapter_name}")
                    if new_count > 5:
                        print(f"      ... and {new_count - 5} more")
                else:
                    print(f"   ⚠️  No chapters extracted")

            except Exception as e:
                print(f"   ❌ Error: {str(e)[:100]}")
                db.rollback()

    print("\n" + "=" * 70)
    print("📊 FINAL SUMMARY")
    print("=" * 70)
    print(f"✅ Successfully re-parsed: {total_parsed} syllabi")
    print(f"📚 Total chapters extracted: {total_chapters}")
    print("=" * 70)

    # Show final status
    print("\n📋 FINAL CHAPTER STATUS:")
    for class_num in ['9', '10']:
        print(f"\n   Class {class_num}:")
        syllabi = db.query(SyllabusMaster).filter(
            SyllabusMaster.class_name == class_num,
            SyllabusMaster.is_active == True
        ).order_by(SyllabusMaster.subject).all()

        for s in syllabi:
            topic_count = db.query(SyllabusTopics).filter_by(syllabus_id=s.id).count()
            print(f"      {s.subject}: {topic_count} chapters")

    print("\n" + "=" * 70)
    print("✅ RE-PARSING COMPLETED!")
    print("=" * 70)

    db.close()

if __name__ == "__main__":
    reparse_all_chapters()
