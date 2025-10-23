from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Assessment, User, Question
from app.schemas import AssessmentCreate, AssessmentOut
from app.ai_question_gen import generate_questions
from typing import List

router = APIRouter()

@router.post("/create-assessment", response_model=AssessmentOut)
def create_assessment(req: AssessmentCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    teacher = db.query(User).filter(User.id == req.teacher_id, User.role == "teacher").first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    # Convert timezone-aware datetime to naive datetime (strip timezone info)
    # The frontend sends IST times, we store them as-is without timezone
    start_time_naive = req.start_time.replace(tzinfo=None) if req.start_time.tzinfo else req.start_time
    end_time_naive = req.end_time.replace(tzinfo=None) if req.end_time.tzinfo else req.end_time

    new_assessment = Assessment(
        teacher_id=req.teacher_id,
        class_name=req.class_name,
        section=req.section,
        subject=req.subject,
        chapter=req.chapter,
        start_time=start_time_naive,
        end_time=end_time_naive,
        duration_minutes=req.duration_minutes
    )
    db.add(new_assessment)
    db.commit()
    db.refresh(new_assessment)

    # Run AI question generation asynchronously
    background_tasks.add_task(generate_and_store_questions, new_assessment.id, req.class_name, req.subject, req.chapter)

    return new_assessment


def normalize_subject_name(subject: str) -> str:
    """
    Normalize subject names to handle common typos and variations
    """
    subject_lower = subject.lower().strip()

    # Common typo corrections
    typo_map = {
        'mathametics': 'mathematics',
        'mathematic': 'mathematics',
        'maths': 'mathematics',
        'math': 'mathematics',
        'sciense': 'science',
        'sience': 'science',
        'scince': 'science',
        'englsh': 'english',
        'hindy': 'hindi',
        'social science': 'social science',
        'sst': 'social science',
        'evs': 'evs',
        'env': 'evs'
    }

    # Return corrected name or original
    return typo_map.get(subject_lower, subject)


def infer_language_position(subject: str, medium: str) -> str:
    """
    Infer language position (FL, SL, TL) based on subject and medium
    For English Medium (Configuration A - Regional Focus):
    - English → FL (First Language)
    - Telugu → SL (Second Language)
    - Hindi → TL (Third Language)
    """
    subject_lower = subject.lower().strip()

    # Language subjects
    language_subjects = ['english', 'telugu', 'hindi', 'sanskrit', 'urdu']

    # Check if it's a language subject
    if subject_lower not in language_subjects:
        return None  # Not a language subject

    # For English medium
    if medium.lower() == 'english':
        if subject_lower == 'english':
            return 'FL'  # First Language
        elif subject_lower == 'telugu':
            return 'SL'  # Second Language
        elif subject_lower in ['hindi', 'sanskrit']:
            return 'TL'  # Third Language

    # For Telugu medium
    elif medium.lower() == 'telugu':
        if subject_lower == 'telugu':
            return 'FL'  # First Language
        elif subject_lower == 'english':
            return 'SL'  # Second Language
        elif subject_lower in ['hindi', 'sanskrit']:
            return 'TL'  # Third Language

    # For Hindi medium
    elif medium.lower() == 'hindi':
        if subject_lower == 'hindi':
            return 'FL'  # First Language
        elif subject_lower in ['english', 'telugu']:
            return 'SL'  # Second Language
        elif subject_lower == 'sanskrit':
            return 'TL'  # Third Language

    return None  # Default


def generate_and_store_questions(assessment_id, class_name, subject, chapter,
                                board_code=None, medium=None, language_position=None):
    from app.db import SessionLocal
    from app.syllabus_service_v2 import EnhancedSyllabusService
    from app.models import SyllabusMaster, SyllabusTopics

    db = SessionLocal()
    try:
        # Normalize subject name to handle typos
        normalized_subject = normalize_subject_name(subject)
        if normalized_subject != subject:
            print(f"📝 Normalized '{subject}' → '{normalized_subject}'")

        # Default to CBSE if no board specified
        if not board_code:
            board_code = 'CBSE'
        if not medium:
            medium = 'English'

        # Infer language_position for Classes 6-10 if not provided
        if not language_position and int(class_name) >= 6:
            language_position = infer_language_position(normalized_subject, medium)

        # NEW: Try to get REAL syllabus content
        syllabus_content = None
        board_name = board_code if board_code != 'CBSE' else 'CBSE'
        lang_info = f" ({language_position})" if language_position else ""
        print(f"🔍 Fetching {board_name} syllabus for Class {class_name} - {normalized_subject}{lang_info} ({medium} medium)...")

        try:
            service = EnhancedSyllabusService(db)

            # Get or fetch syllabus (using normalized subject name)
            syllabus = service.get_syllabus(class_name, normalized_subject,
                                           board_code=board_code, medium=medium,
                                           language_position=language_position)

            if syllabus and syllabus.content_extracted:
                # Find the specific chapter/topic
                topics = db.query(SyllabusTopics).filter(
                    SyllabusTopics.syllabus_id == syllabus.id,
                    SyllabusTopics.chapter_name.ilike(f"%{chapter}%")
                ).first()

                if topics:
                    print(f"✅ Found syllabus content for: {topics.chapter_name}")
                    # Use a relevant chunk of syllabus
                    full_content = syllabus.content_extracted

                    # Try to find chapter-specific content
                    if chapter.lower() in full_content.lower():
                        start_idx = full_content.lower().find(chapter.lower())
                        syllabus_content = full_content[max(0, start_idx-500):start_idx+2500]
                    else:
                        # Use first 3000 chars as fallback
                        syllabus_content = full_content[:3000]

                    print(f"📄 Using {len(syllabus_content)} chars of REAL CBSE content")
                else:
                    print(f"⚠️ Chapter '{chapter}' not found in parsed topics, using full syllabus")
                    syllabus_content = syllabus.content_extracted[:3000]
            else:
                print(f"⚠️ No syllabus found, will use generic generation")

        except Exception as e:
            print(f"⚠️ Could not fetch syllabus: {e}")
            print(f"   Falling back to generic question generation")

        # Generate questions (with or without syllabus content)
        questions = generate_questions(board_code, class_name, subject, chapter,
                                      num_questions=10,
                                      syllabus_content=syllabus_content)

        if not questions:
            print("⚠️ No questions generated for", chapter)
            return

        for q in questions:
            db.add(Question(
                assessment_id=assessment_id,
                question=q["question"],
                options=q["options"],
                correct_answer=q["correct_answer"],
                difficulty=q.get("difficulty", "medium")
            ))
        db.commit()

        if syllabus_content:
            print(f"✅ {len(questions)} {board_code}-based questions stored for assessment {assessment_id}")
        else:
            print(f"✅ {len(questions)} generic questions stored for assessment {assessment_id}")

    finally:
        db.close()


@router.get("/my-assessments/{teacher_id}", response_model=List[AssessmentOut])
def get_assessments(teacher_id: int, db: Session = Depends(get_db)):
    # Sort by start_time descending (latest/newest first)
    data = db.query(Assessment).filter(Assessment.teacher_id == teacher_id).order_by(Assessment.start_time.desc()).all()
    return data


@router.get("/assessment/{assessment_id}/questions")
def get_assessment_questions(assessment_id: int, db: Session = Depends(get_db)):
    """
    Get all questions for an assessment (for teacher view).
    No time restrictions - teachers can view questions anytime.
    Includes correct answers.
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    questions = db.query(Question).filter(Question.assessment_id == assessment_id).all()

    return [
        {
            "id": q.id,
            "question": q.question,
            "options": q.options,
            "correct_answer": q.correct_answer,
            "difficulty": q.difficulty
        } for q in questions
    ]
