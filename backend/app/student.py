from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.db import SessionLocal
from app.models import Assessment, Question, Result

router = APIRouter()

# >� 1. Fetch all upcoming assessments for a given class
@router.get("/assessments/{class_name}")
def get_assessments(class_name: str):
    db = SessionLocal()
    now = datetime.utcnow()
    data = db.query(Assessment).filter(Assessment.class_name == class_name, Assessment.end_time > now).all()
    return data


# >� 2. Fetch questions for a specific assessment (if within time window)
@router.get("/assessment/{assessment_id}/questions")
def get_questions(assessment_id: int):
    db = SessionLocal()
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    now = datetime.utcnow()
    if now < assessment.start_time or now > assessment.end_time:
        raise HTTPException(status_code=403, detail="Exam not active at this time")

    questions = db.query(Question).filter(Question.assessment_id == assessment_id).all()
    return [
        {
            "id": q.id,
            "question": q.question,
            "options": q.options
        } for q in questions
    ]


# =R 3. Submit answers for evaluation
@router.post("/submit-exam")
def submit_exam(req: dict):
    db = SessionLocal()

    student_id = req["student_id"]
    assessment_id = req["assessment_id"]
    answers = req["answers"]

    # Fetch all questions for this assessment
    questions = db.query(Question).filter(Question.assessment_id == assessment_id).all()
    if not questions:
        raise HTTPException(status_code=404, detail="Questions not found")

    score = 0
    total = len(questions)

    # Evaluate
    for q in questions:
        selected = answers.get(str(q.id)) or answers.get(q.id)
        if selected and selected == q.correct_answer:
            score += 1

    # Save result
    result = Result(
        student_id=student_id,
        assessment_id=assessment_id,
        answers=answers,
        score=score
    )
    db.add(result)
    db.commit()

    return {"message": "Exam submitted successfully", "score": score, "total": total}


# 🧾 Get student's past exam results
@router.get("/my-results/{student_id}")
def get_student_results(student_id: int):
    db = SessionLocal()
    results = db.query(Result).filter(Result.student_id == student_id).all()
    output = []

    for r in results:
        a = db.query(Assessment).filter(Assessment.id == r.assessment_id).first()
        if not a:
            continue
        total_questions = db.query(Question).filter(Question.assessment_id == a.id).count()
        output.append({
            "assessment_id": a.id,
            "subject": a.subject,
            "chapter": a.chapter,
            "score": r.score,
            "total": total_questions,
            "submitted_at": r.submitted_at
        })
    return output
