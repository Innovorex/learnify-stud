#!/usr/bin/env python3
"""
Test State Board Syllabus Retrieval
Verify Telangana and AP state boards are working
"""

from app.db import SessionLocal
from app.syllabus_service_v2 import EnhancedSyllabusService

def test_state_board_retrieval():
    """
    Test retrieving state board syllabi
    """
    db = SessionLocal()
    service = EnhancedSyllabusService(db)

    print("=" * 80)
    print("TESTING STATE BOARD SYLLABUS RETRIEVAL")
    print("=" * 80)

    test_cases = [
        # Telangana State Board
        {
            'board_code': 'TSBSE',
            'class_name': '1',
            'subject': 'Mathematics',
            'medium': 'English',
            'description': 'Telangana Class 1 Mathematics (English)'
        },
        {
            'board_code': 'TSBSE',
            'class_name': '5',
            'subject': 'Environmental Studies',
            'medium': 'English',
            'description': 'Telangana Class 5 EVS (English)'
        },
        # Andhra Pradesh State Board
        {
            'board_code': 'BSEAP',
            'class_name': '3',
            'subject': 'English',
            'medium': 'English',
            'description': 'AP Class 3 English'
        },
        {
            'board_code': 'BSEAP',
            'class_name': '4',
            'subject': 'Mathematics',
            'medium': 'English',
            'description': 'AP Class 4 Mathematics (English)'
        },
        # CBSE for comparison
        {
            'board_code': 'CBSE',
            'class_name': '10',
            'subject': 'Mathematics',
            'medium': None,
            'description': 'CBSE Class 10 Mathematics'
        }
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST {i}: {test['description']}")
        print(f"{'=' * 80}")

        syllabus = service.get_syllabus(
            class_name=test['class_name'],
            subject=test['subject'],
            board_code=test['board_code'],
            medium=test['medium']
        )

        if syllabus:
            print(f"✅ SUCCESS")
            print(f"   Board: {syllabus.board} ({syllabus.board_type})")
            print(f"   Class: {syllabus.class_name}")
            print(f"   Subject: {syllabus.subject}")
            print(f"   Medium: {syllabus.medium}")
            print(f"   Textbook: {syllabus.textbook_name}")
            print(f"   Publisher: {syllabus.publisher}")

            # Count chapters
            from app.models import SyllabusTopics
            chapters = db.query(SyllabusTopics).filter_by(
                syllabus_id=syllabus.id
            ).count()
            print(f"   Chapters: {chapters}")
        else:
            print(f"❌ FAILED - Syllabus not found")

    print("\n" + "=" * 80)
    print("TESTING COMPLETE")
    print("=" * 80)

    db.close()


if __name__ == "__main__":
    test_state_board_retrieval()
