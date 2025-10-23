#!/usr/bin/env python3
"""
Load Telangana & Andhra Pradesh State Board Syllabi
Classes 1-5 | English Medium Only
"""

from app.db import SessionLocal
from app.models import StateBoard, SyllabusMaster, SyllabusTopics
from state_board_structure_telangana_ap import (
    TELANGANA_STRUCTURE,
    ANDHRA_PRADESH_STRUCTURE,
    PUBLISHERS
)
from datetime import datetime

def load_state_board_syllabi():
    """
    Load Telangana and AP state board syllabi into database
    """
    db = SessionLocal()

    try:
        print("=" * 80)
        print("LOADING STATE BOARD SYLLABI")
        print("Telangana & Andhra Pradesh | Classes 1-5 | English Medium")
        print("=" * 80)

        # Get state board IDs
        tsbse = db.query(StateBoard).filter_by(board_code='TSBSE').first()
        bseap = db.query(StateBoard).filter_by(board_code='BSEAP').first()

        if not tsbse or not bseap:
            print("\n❌ State boards not found in database!")
            print("   Run apply_state_board_migration.py first")
            return

        print(f"\n✅ Found state boards:")
        print(f"   • TSBSE (ID: {tsbse.id})")
        print(f"   • BSEAP (ID: {bseap.id})")

        boards_to_load = [
            {
                'board': tsbse,
                'structure': TELANGANA_STRUCTURE,
                'name': 'Telangana'
            },
            {
                'board': bseap,
                'structure': ANDHRA_PRADESH_STRUCTURE,
                'name': 'Andhra Pradesh'
            }
        ]

        total_syllabi = 0
        total_chapters = 0

        for board_data in boards_to_load:
            board = board_data['board']
            structure = board_data['structure']
            board_name = board_data['name']

            print(f"\n{'=' * 80}")
            print(f"LOADING: {board_name} State Board ({board.board_code})")
            print(f"{'=' * 80}")

            for class_num, subjects in structure.items():
                class_str = str(class_num)

                for subject, subject_data in subjects.items():
                    textbook_name = subject_data['textbook_name']
                    chapters = subject_data['chapters']

                    # Check if syllabus already exists
                    existing = db.query(SyllabusMaster).filter_by(
                        board=board.board_code,
                        board_type='STATE',
                        state_board_id=board.id,
                        class_name=class_str,
                        subject=subject,
                        medium='English'
                    ).first()

                    if existing:
                        print(f"  ⏭️ Class {class_str} {subject} already exists (ID: {existing.id})")
                        continue

                    # Create synthetic content (chapter names as content)
                    content = f"{board.board_name}\nClass {class_str} - {subject}\n"
                    content += f"Textbook: {textbook_name}\n\n"
                    content += "Chapters:\n"
                    for i, chapter in enumerate(chapters, 1):
                        content += f"{i}. {chapter}\n"

                    # Create SyllabusMaster entry
                    syllabus = SyllabusMaster(
                        board=board.board_code,
                        board_type='STATE',
                        state_board_id=board.id,
                        class_name=class_str,
                        subject=subject,
                        stage='primary',  # Classes 1-5 are primary
                        academic_year='2024-25',
                        medium='English',
                        textbook_name=textbook_name,
                        publisher=PUBLISHERS[board.board_code],
                        content_extracted=content,
                        is_active=True
                    )

                    db.add(syllabus)
                    db.flush()  # Get the ID

                    # Add chapters as topics
                    for i, chapter_name in enumerate(chapters, 1):
                        topic = SyllabusTopics(
                            syllabus_id=syllabus.id,
                            is_chapter=True,
                            chapter_number=i,
                            chapter_name=chapter_name,
                            sequence_order=i
                        )
                        db.add(topic)

                    db.commit()

                    total_syllabi += 1
                    total_chapters += len(chapters)

                    print(f"  ✅ Class {class_str} {subject}: {len(chapters)} chapters")

        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"✅ Total syllabi loaded: {total_syllabi}")
        print(f"✅ Total chapters: {total_chapters}")
        print(f"✅ Boards: Telangana (TSBSE) + Andhra Pradesh (BSEAP)")
        print(f"✅ Classes: 1-5")
        print(f"✅ Medium: English only")
        print(f"✅ Subjects per class: English, Mathematics, Environmental Studies")

        # Verification query
        print("\n" + "=" * 80)
        print("VERIFICATION")
        print("=" * 80)

        for board_code in ['TSBSE', 'BSEAP']:
            count = db.query(SyllabusMaster).filter_by(
                board=board_code,
                board_type='STATE'
            ).count()
            print(f"  {board_code}: {count} syllabi in database")

        print("\n✅ STATE BOARD DATA LOADING COMPLETED!")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    load_state_board_syllabi()
