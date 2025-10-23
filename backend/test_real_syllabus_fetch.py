#!/usr/bin/env python3
"""
Test: Fetch and parse REAL Class 10 Mathematics CBSE syllabus
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.db import SessionLocal
from app.syllabus_service_v2 import EnhancedSyllabusService

print("="*70)
print("📚 CBSE Class 10 Mathematics - Real Syllabus Fetch Test")
print("="*70)

db = SessionLocal()

try:
    service = EnhancedSyllabusService(db)

    print("\n⏳ Fetching Class 10 Mathematics syllabus...")
    print("   (This will download PDF, extract text, and parse with AI)")
    print("   Expected time: 30-60 seconds\n")

    # Fetch syllabus (will auto-discover if needed)
    syllabus = service.get_syllabus('10', 'Mathematics')

    if syllabus:
        print(f"\n✅ Syllabus fetched successfully!")
        print(f"   Class: {syllabus.class_name}")
        print(f"   Subject: {syllabus.subject} ({syllabus.subject_code})")
        print(f"   Academic Year: {syllabus.academic_year}")
        print(f"   SHA256: {syllabus.content_sha256[:16]}...")
        print(f"   PDF URL: {syllabus.pdf_url[:60]}...")

        # Show content sample
        if syllabus.content_extracted:
            content_preview = syllabus.content_extracted[:500]
            print(f"\n📄 Content Sample (first 500 chars):")
            print(f"   {content_preview}")

        # Get topics
        print("\n📚 Fetching chapters/topics...")
        topics = service.get_topics('10', 'Mathematics')

        print(f"\n✅ Found {len(topics)} chapters:")
        for i, topic in enumerate(topics[:10], 1):  # Show first 10
            weightage = f" ({topic.weightage} marks)" if topic.weightage else ""
            print(f"   {i}. Ch {topic.chapter_number}: {topic.chapter_name}{weightage}")
            if topic.subtopics:
                print(f"      Subtopics: {', '.join(topic.subtopics[:3])}")

        # Test specific topic content
        if topics:
            print(f"\n🔍 Detailed view of first chapter:")
            topic_detail = service.get_topic_content(topics[0].id)
            print(f"   Chapter: {topic_detail['chapter_name']}")
            print(f"   Unit: {topic_detail['unit_name']}")
            if topic_detail['subtopics']:
                print(f"   Subtopics: {', '.join(topic_detail['subtopics'])}")
            if topic_detail['learning_outcomes']:
                print(f"   Learning Outcomes:")
                for outcome in topic_detail['learning_outcomes'][:3]:
                    print(f"     - {outcome}")

        print(f"\n{'='*70}")
        print("✅ SUCCESS! Real CBSE syllabus is being extracted and parsed!")
        print("="*70)

    else:
        print(f"\n❌ Failed to fetch syllabus")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    db.close()
