from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.database.models import Exam, Subject, Topic
from backend.api.auth import get_current_user
from backend.schemas.exams import ExamCreate, ExamOut, ExamBase, SubjectOut, TopicOut
from backend.database.models import User

router = APIRouter(prefix="/exams", tags=["exams"])

@router.post("", response_model=ExamOut)
def create_exam(exam_in: ExamCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 1. Create Exam
    db_exam = Exam(
        user_id=current_user.id,
        name=exam_in.name,
        exam_date=exam_in.exam_date,
        priority=exam_in.priority,
        difficulty=exam_in.difficulty
    )
    db.add(db_exam)
    db.commit()
    db.refresh(db_exam)
    
    # 2. Add Subjects and Topics
    # We will map subject name -> db subject object to link topics properly
    subject_db_map = {}
    for sub in exam_in.subjects:
        db_sub = Subject(
            user_id=current_user.id,
            name=sub.name,
            difficulty=sub.difficulty
        )
        db.add(db_sub)
        db.commit()
        db.refresh(db_sub)
        subject_db_map[sub.name] = db_sub
        
    for top in exam_in.topics:
        sub_obj = subject_db_map.get(top.subject_name)
        if not sub_obj:
            # Create subject on the fly if not specified in subjects list
            sub_obj = Subject(
                user_id=current_user.id,
                name=top.subject_name,
                difficulty="medium"
            )
            db.add(sub_obj)
            db.commit()
            db.refresh(sub_obj)
            subject_db_map[top.subject_name] = sub_obj
            
        db_topic = Topic(
            subject_id=sub_obj.id,
            title=top.title,
            status=top.status,
            confidence=top.confidence
        )
        db.add(db_topic)
        
    db.commit()
    return db_exam

@router.get("", response_model=List[ExamOut])
def get_exams(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Exam).filter(Exam.user_id == current_user.id).all()

@router.get("/{exam_id}/details")
def get_exam_details(exam_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id, Exam.user_id == current_user.id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
        
    # Get subjects and topics
    subjects = db.query(Subject).filter(Subject.user_id == current_user.id).all()
    sub_ids = [s.id for s in subjects]
    
    topics = []
    if sub_ids:
        topics = db.query(Topic).filter(Topic.subject_id.in_(sub_ids)).all()
        
    return {
        "exam": exam,
        "subjects": subjects,
        "topics": [{
            "id": t.id,
            "subject_id": t.subject_id,
            "subject_name": next((s.name for s in subjects if s.id == t.subject_id), "Unknown"),
            "title": t.title,
            "status": t.status,
            "confidence": t.confidence
        } for t in topics]
    }

@router.put("/{exam_id}", response_model=ExamOut)
def update_exam(exam_id: int, exam_in: ExamBase, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id, Exam.user_id == current_user.id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
        
    for key, value in exam_in.model_dump().items():
        setattr(exam, key, value)
        
    db.commit()
    db.refresh(exam)
    return exam

@router.delete("/{exam_id}")
def delete_exam(exam_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id, Exam.user_id == current_user.id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
        
    db.delete(exam)
    db.commit()
    return {"message": "Exam deleted successfully"}

# Extra helper route to update a topic directly
@router.put("/topics/{topic_id}")
def update_topic_status(topic_id: int, status: str, confidence: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Verify topic ownership via subject
    topic = db.query(Topic).join(Subject).filter(Topic.id == topic_id, Subject.user_id == current_user.id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
        
    topic.status = status
    topic.confidence = confidence
    db.commit()
    db.refresh(topic)
    return topic
