#!/usr/bin/env python3
"""
Load Telangana & Andhra Pradesh State Board Syllabi
Classes 6-10 | English Medium | Configuration A (Regional Focus)

Configuration A:
1️⃣ English (FL) - First Language
2️⃣ Telugu (SL) - Second Language
3️⃣ Hindi (TL) - Third Language
+ Mathematics, Science, Social Studies
"""

from app.db import SessionLocal
from app.models import StateBoard, SyllabusMaster, SyllabusTopics
from state_board_structure_6_10_telangana_ap import (
    TELANGANA_6_10_STRUCTURE,
    ANDHRA_PRADESH_6_10_STRUCTURE,
    PUBLISHERS
)

def extract_subject_and_position(subject_key):
    """
    Extract subject name and language position from key
    E.g., 'English_FL' → ('English', 'FL')
          'Mathematics' → ('Mathematics', None)
    """
    if '_' in subject_key:
        parts = subject_key.rsplit('_', 1)
        return parts[0], parts[1]
    return subject_key, None


def load_classes_6_10_syllabi():
    """
    Load Telangana and AP state board syllabi for Classes 6-10
    """
    db = SessionLocal()

    try:
        print("=" * 80)
        print("LOADING STATE BOARD SYLLABI - CLASSES 6-10")
        print("Telangana & Andhra Pradesh | English Medium | Configuration A")
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
                'structure': TELANGANA_6_10_STRUCTURE,
                'name': 'Telangana'
            },
            {
                'board': bseap,
                'structure': ANDHRA_PRADESH_6_10_STRUCTURE,
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

                for subject_key, subject_data in subjects.items():
                    subject, language_position = extract_subject_and_position(subject_key)
                    textbook_name = subject_data['textbook_name']
                    chapters = subject_data['chapters']
                    lang_pos = subject_data.get('language_position')

                    # Check if syllabus already exists
                    existing = db.query(SyllabusMaster).filter_by(
                        board=board.board_code,
                        board_type='STATE',
                        state_board_id=board.id,
                        class_name=class_str,
                        subject=subject,
                        medium='English',
                        language_position=lang_pos
                    ).first()

                    if existing:
                        lang_info = f" ({lang_pos})" if lang_pos else ""
                        print(f"  ⏭️ Class {class_str} {subject}{lang_info} already exists (ID: {existing.id})")
                        continue

                    # Create synthetic content
                    content = f"{board.board_name}\nClass {class_str} - {subject}\n"
                    if lang_pos:
                        position_name = {
                            'FL': 'First Language',
                            'SL': 'Second Language',
                            'TL': 'Third Language'
                        }.get(lang_pos, lang_pos)
                        content += f"Language Position: {position_name}\n"
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
                        stage='middle' if int(class_str) <= 8 else 'secondary',
                        academic_year='2024-25',
                        medium='English',
                        language_position=lang_pos,
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

                    lang_info = f" ({lang_pos})" if lang_pos else ""
                    print(f"  ✅ Class {class_str} {subject}{lang_info}: {len(chapters)} chapters")

        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"✅ Total syllabi loaded: {total_syllabi}")
        print(f"✅ Total chapters: {total_chapters}")
        print(f"✅ Boards: Telangana (TSBSE) + Andhra Pradesh (BSEAP)")
        print(f"✅ Classes: 6-10")
        print(f"✅ Medium: English only")
        print(f"✅ Configuration: A (Regional Focus)")
        print(f"   1️⃣ English (FL) - First Language")
        print(f"   2️⃣ Telugu (SL) - Second Language")
        print(f"   3️⃣ Hindi (TL) - Third Language")
        print(f"   + Mathematics, Science, Social Studies")

        # Verification query
        print("\n" + "=" * 80)
        print("VERIFICATION")
        print("=" * 80)

        for board_code in ['TSBSE', 'BSEAP']:
            count = db.query(SyllabusMaster).filter_by(
                board=board_code,
                board_type='STATE'
            ).count()

            # Count by language position
            fl_count = db.query(SyllabusMaster).filter_by(
                board=board_code,
                language_position='FL'
            ).count()
            sl_count = db.query(SyllabusMaster).filter_by(
                board=board_code,
                language_position='SL'
            ).count()
            tl_count = db.query(SyllabusMaster).filter_by(
                board=board_code,
                language_position='TL'
            ).count()
            core_count = db.query(SyllabusMaster).filter_by(
                board=board_code,
                board_type='STATE',
                language_position=None
            ).count()

            print(f"  {board_code}: {count} syllabi")
            print(f"    - First Language (FL): {fl_count}")
            print(f"    - Second Language (SL): {sl_count}")
            print(f"    - Third Language (TL): {tl_count}")
            print(f"    - Core Subjects: {core_count}")

        print("\n✅ CLASSES 6-10 STATE BOARD DATA LOADING COMPLETED!")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    load_classes_6_10_syllabi()
