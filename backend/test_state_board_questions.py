#!/usr/bin/env python3
"""
Test State Board Question Generation
Generate questions for Telangana Class 5 Environmental Studies
"""

from app.db import SessionLocal
from app.teacher import generate_and_store_questions
from app.models import Assessment, User, Question, ist_now
from datetime import datetime, timedelta

def test_state_board_question_generation():
    """
    Test generating questions for Telangana State Board Class 5
    """
    db = SessionLocal()

    try:
        print("=" * 80)
        print("TESTING STATE BOARD QUESTION GENERATION")
        print("Telangana Class 5 - Environmental Studies")
        print("=" * 80)

        # Get or create a test teacher
        teacher = db.query(User).filter_by(role='teacher').first()
        if not teacher:
            print("\n⚠️ No teacher found in database. Creating test teacher...")
            teacher = User(
                name="Test Teacher",
                email="teacher@test.com",
                password="hashed_password",
                role="teacher"
            )
            db.add(teacher)
            db.commit()
            db.refresh(teacher)
            print(f"✅ Created teacher: {teacher.name} (ID: {teacher.id})")
        else:
            print(f"\n✅ Using existing teacher: {teacher.name} (ID: {teacher.id})")

        # Create a test assessment
        print(f"\n{'=' * 80}")
        print("Creating Test Assessment")
        print(f"{'=' * 80}")

        start_time = datetime.now()
        end_time = start_time + timedelta(hours=2)

        test_assessment = Assessment(
            teacher_id=teacher.id,
            class_name='5',
            section='A',
            subject='Environmental Studies',
            chapter='Super Senses',  # First chapter from Class 5 EVS
            start_time=start_time,
            end_time=end_time,
            duration_minutes=60
        )

        db.add(test_assessment)
        db.commit()
        db.refresh(test_assessment)

        print(f"✅ Assessment created (ID: {test_assessment.id})")
        print(f"   Class: {test_assessment.class_name}")
        print(f"   Subject: {test_assessment.subject}")
        print(f"   Chapter: {test_assessment.chapter}")

        # Generate questions for Telangana state board
        print(f"\n{'=' * 80}")
        print("Generating Questions - TELANGANA STATE BOARD")
        print(f"{'=' * 80}")

        generate_and_store_questions(
            assessment_id=test_assessment.id,
            class_name='5',
            subject='Environmental Studies',
            chapter='Super Senses',
            board_code='TSBSE',
            medium='English'
        )

        # Verify questions were created
        print(f"\n{'=' * 80}")
        print("VERIFICATION")
        print(f"{'=' * 80}")

        questions = db.query(Question).filter_by(assessment_id=test_assessment.id).all()

        if questions:
            print(f"\n✅ {len(questions)} questions generated successfully!")
            print(f"\nSample Questions:")
            print(f"{'=' * 80}")

            for i, q in enumerate(questions[:3], 1):  # Show first 3 questions
                print(f"\nQuestion {i}:")
                print(f"Q: {q.question}")
                print(f"Options:")
                for key, value in q.options.items():
                    marker = "✓" if key == q.correct_answer else " "
                    print(f"  [{marker}] {key}: {value}")
                print(f"Difficulty: {q.difficulty}")

            if len(questions) > 3:
                print(f"\n... and {len(questions) - 3} more questions")

            print(f"\n{'=' * 80}")
            print("✅ STATE BOARD QUESTION GENERATION TEST PASSED!")
            print(f"{'=' * 80}")

        else:
            print(f"\n❌ No questions were generated!")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    test_state_board_question_generation()
