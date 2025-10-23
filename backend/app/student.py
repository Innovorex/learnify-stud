from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from app.db import get_db
from app.models import Assessment, Question, Result

# IST timezone (UTC + 5:30)
IST = timezone(timedelta(hours=5, minutes=30))

router = APIRouter()

def get_ist_now():
    """Get current time in IST as naive datetime"""
    return datetime.now(IST).replace(tzinfo=None)

# >� 1. Fetch all upcoming assessments for a given class and section
@router.get("/assessments/{class_name}/{section}")
def get_assessments(class_name: str, section: str, db: Session = Depends(get_db)):
    # Get current time in IST (naive datetime)
    now = get_ist_now()

    print(f"🔍 Fetching assessments for Class: '{class_name}', Section: '{section}'")

    # Get all assessments for debugging
    all_assessments = db.query(Assessment).all()
    print(f"📚 Total assessments in DB: {len(all_assessments)}")
    for a in all_assessments:
        print(f"  - ID {a.id}: Class='{a.class_name}', Section='{a.section}', Subject={a.subject}")

    data = db.query(Assessment).filter(
        Assessment.class_name == class_name,
        Assessment.section == section,
        Assessment.end_time > now
    ).all()

    print(f"✅ Found {len(data)} matching assessments for '{class_name}'-'{section}'")

    return data


# >� 2. Fetch questions for a specific assessment (if within time window)
@router.get("/assessment/{assessment_id}/questions")
def get_questions(assessment_id: int, db: Session = Depends(get_db)):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    # Get current time in IST (naive datetime)
    now = get_ist_now()

    # Ensure assessment times are naive datetimes (they should be stored as naive)
    start_time = assessment.start_time.replace(tzinfo=None) if assessment.start_time.tzinfo else assessment.start_time
    end_time = assessment.end_time.replace(tzinfo=None) if assessment.end_time.tzinfo else assessment.end_time

    print(f"🕐 Current IST time: {now}")
    print(f"📝 Assessment ID {assessment_id}: {start_time} to {end_time} IST")
    print(f"✅ Time check: start < now < end? {start_time} < {now} < {end_time}")

    if now < start_time or now > end_time:
        raise HTTPException(status_code=403, detail=f"Exam not active. Available from {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')} IST")

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
def submit_exam(req: dict, db: Session = Depends(get_db)):
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


# 📊 Get all assessments with completion status for a student
@router.get("/assessments-with-status/{student_id}/{class_name}/{section}")
def get_assessments_with_status(student_id: int, class_name: str, section: str, db: Session = Depends(get_db)):
    # Get current time in IST (naive datetime)
    now = get_ist_now()

    print(f"🔍 Fetching assessments with status for Student ID: {student_id}, Class: '{class_name}', Section: '{section}'")

    # Get all assessments for this class and section, sorted by start_time descending (latest first)
    assessments = db.query(Assessment).filter(
        Assessment.class_name == class_name,
        Assessment.section == section
    ).order_by(Assessment.start_time.desc()).all()

    print(f"📚 Found {len(assessments)} total assessments for '{class_name}'-'{section}'")

    output = []
    for a in assessments:
        # Check if student has submitted this assessment
        result = db.query(Result).filter(
            Result.student_id == student_id,
            Result.assessment_id == a.id
        ).first()

        # Make times timezone-aware for comparison if needed
        start_time = a.start_time.replace(tzinfo=None) if a.start_time.tzinfo else a.start_time
        end_time = a.end_time.replace(tzinfo=None) if a.end_time.tzinfo else a.end_time

        # Determine status
        if result:
            status = "completed"
            score = result.score
            total_questions = db.query(Question).filter(Question.assessment_id == a.id).count()
            submitted_at = result.submitted_at
        elif now < start_time:
            status = "scheduled"
            score = None
            total_questions = None
            submitted_at = None
        elif now >= start_time and now <= end_time:
            status = "available"
            score = None
            total_questions = None
            submitted_at = None
        else:  # now > end_time
            status = "missed"
            score = None
            total_questions = None
            submitted_at = None

        output.append({
            "id": a.id,
            "subject": a.subject,
            "chapter": a.chapter,
            "start_time": a.start_time,
            "end_time": a.end_time,
            "duration_minutes": a.duration_minutes,
            "status": status,
            "score": score,
            "total_questions": total_questions,
            "submitted_at": submitted_at
        })

    print(f"✅ Returning {len(output)} assessments with status")
    return output


# 🧾 Get student's past exam results
@router.get("/my-results/{student_id}")
def get_student_results(student_id: int, db: Session = Depends(get_db)):
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
