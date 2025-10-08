from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.db import SessionLocal
from app.models import Assessment, User, Question
from app.schemas import AssessmentCreate, AssessmentOut
from app.ai_question_gen import generate_questions
from typing import List

router = APIRouter()

@router.post("/create-assessment", response_model=AssessmentOut)
def create_assessment(req: AssessmentCreate, background_tasks: BackgroundTasks):
    db = SessionLocal()
    teacher = db.query(User).filter(User.id == req.teacher_id, User.role == "teacher").first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    new_assessment = Assessment(
        teacher_id=req.teacher_id,
        class_name=req.class_name,
        subject=req.subject,
        chapter=req.chapter,
        start_time=req.start_time,
        end_time=req.end_time,
        duration_minutes=req.duration_minutes
    )
    db.add(new_assessment)
    db.commit()
    db.refresh(new_assessment)

    # Run AI question generation asynchronously
    background_tasks.add_task(generate_and_store_questions, new_assessment.id, req.class_name, req.subject, req.chapter)

    return new_assessment


def generate_and_store_questions(assessment_id, class_name, subject, chapter):
    db = SessionLocal()
    questions = generate_questions("CBSE", class_name, subject, chapter)
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
    print(f"✅ {len(questions)} questions stored for assessment {assessment_id}")


@router.get("/my-assessments/{teacher_id}", response_model=List[AssessmentOut])
def get_assessments(teacher_id: int):
    db = SessionLocal()
    data = db.query(Assessment).filter(Assessment.teacher_id == teacher_id).all()
    return data
