from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Result, Assessment, User

router = APIRouter()

# =� Get results for a specific assessment
@router.get("/results/{assessment_id}")
def get_assessment_results(assessment_id: int, db: Session = Depends(get_db)):
    results = db.query(Result).filter(Result.assessment_id == assessment_id).all()
    if not results:
        raise HTTPException(status_code=404, detail="No results found for this assessment")

    total_students = len(results)
    avg_score = sum(r.score for r in results) / total_students
    top_result = max(results, key=lambda r: r.score)
    top_student = db.query(User).filter(User.id == top_result.student_id).first()

    return {
        "assessment_id": assessment_id,
        "average_score": round(avg_score, 2),
        "total_students": total_students,
        "top_scorer": top_student.name if top_student else None,
        "results": [
            {
                "student_id": r.student_id,
                "score": r.score,
                "submitted_at": r.submitted_at
            } for r in results
        ]
    }


# =� Summary for teacher (all assessments)
@router.get("/summary/{teacher_id}")
def get_teacher_summary(teacher_id: int, db: Session = Depends(get_db)):
    assessments = db.query(Assessment).filter(Assessment.teacher_id == teacher_id).all()
    summary = []

    for a in assessments:
        results = db.query(Result).filter(Result.assessment_id == a.id).all()
        if not results:
            continue
        avg = sum(r.score for r in results) / len(results)
        top = max(r.score for r in results)
        summary.append({
            "assessment_id": a.id,
            "subject": a.subject,
            "chapter": a.chapter,
            "average_score": round(avg, 2),
            "top_score": top
        })
    return summary
