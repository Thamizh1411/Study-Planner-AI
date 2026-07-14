import datetime
import json
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database.connection import get_db
from backend.database.models import User, Exam, Subject, Topic, StudyPlan, Quiz, Progress, Note, Flashcard
from backend.api.auth import get_current_user

router = APIRouter(tags=["progress"])
logger = logging.getLogger("study_planner_agents")

class QuizSubmit(BaseModel):
    topic_id: int
    score: float  # Percentage score (0 - 100)

class StudyLog(BaseModel):
    hours: float

# Import scheduler directly to trigger dynamic rebalancing
from backend.agents.scheduler import SchedulerAgent
from backend.agents.analyzer import PerformanceAnalyzerAgent
from backend.agents.motivator import MotivationAgent

def trigger_schedule_rebalance(user_id: int, db: Session):
    logger.info(f"Triggering automated schedule rebalance for user_id: {user_id}")
    
    # 1. Fetch exam
    exam = db.query(Exam).filter(Exam.user_id == user_id).order_by(Exam.id.desc()).first()
    if not exam:
        return None
        
    # 2. Get subjects & topics
    subjects = db.query(Subject).filter(Subject.user_id == user_id).all()
    sub_ids = [s.id for s in subjects]
    
    topics = []
    if sub_ids:
        topics = db.query(Topic).filter(Topic.subject_id.in_(sub_ids)).all()
        
    if not topics:
        return None
        
    # 3. Get quiz scores
    topic_ids = [t.id for t in topics]
    quizzes = db.query(Quiz).filter(Quiz.topic_id.in_(topic_ids)).all()
    
    quiz_scores = []
    for q in quizzes:
        t = next((topic for topic in topics if topic.id == q.topic_id), None)
        if t:
            quiz_scores.append({
                "topic_title": t.title,
                "score": q.score,
                "date": q.generated_at.strftime("%Y-%m-%d")
            })
            
    # 4. Construct current graph state subset
    state_input = {
        "student_profile": {},
        "subjects": [{"name": s.name, "difficulty": s.difficulty} for s in subjects],
        "topics": [{
            "subject_name": next((s.name for s in subjects if s.id == t.subject_id), "Unknown"),
            "title": t.title,
            "status": t.status,
            "confidence": t.confidence
        } for t in topics],
        "exam_date": exam.exam_date.strftime("%Y-%m-%d"),
        "daily_hours": 3.0,
        "quiz_scores": quiz_scores,
        "schedule": {},
        "analysis": {},
        "motivation": {}
    }
    
    # 5. Execute Scheduler, Analyzer and Motivator sequentially
    state = SchedulerAgent.execute(state_input)
    state = PerformanceAnalyzerAgent.execute(state)
    state = MotivationAgent.execute(state)
    
    # 6. Save rebalanced study plan
    study_plan_json = json.dumps(state.get("schedule"))
    db.query(StudyPlan).filter(StudyPlan.exam_id == exam.id).delete()
    
    db_plan = StudyPlan(
        exam_id=exam.id,
        plan_json=study_plan_json
    )
    db.add(db_plan)
    db.commit()
    
    return state

@router.get("/dashboard")
def get_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Get active exam
    exam = db.query(Exam).filter(Exam.user_id == current_user.id).order_by(Exam.id.desc()).first()
    
    subjects = db.query(Subject).filter(Subject.user_id == current_user.id).all()
    sub_ids = [s.id for s in subjects]
    
    topics = []
    if sub_ids:
        topics = db.query(Topic).filter(Topic.subject_id.in_(sub_ids)).all()
        
    study_plan = None
    if exam:
        study_plan = db.query(StudyPlan).filter(StudyPlan.exam_id == exam.id).order_by(StudyPlan.id.desc()).first()
        
    # Build schedule calendar dict
    schedule_data = json.loads(study_plan.plan_json) if study_plan else {}
    
    # Find today's tasks
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    today_plan = schedule_data.get(today_str, [])
    
    # Calculate general metrics
    total_topics = len(topics)
    completed_topics = len([t for t in topics if t.status == "completed"])
    completion_rate = (completed_topics / total_topics * 100.0) if total_topics > 0 else 0.0
    
    # Calculate streak from progress database
    latest_progress = db.query(Progress).filter(Progress.user_id == current_user.id).order_by(Progress.date.desc()).first()
    active_streak = latest_progress.active_streak if latest_progress else 0
    
    # Fetch quiz score averages
    quizzes = db.query(Quiz).join(Topic).join(Subject).filter(Subject.user_id == current_user.id).all()
    avg_score = sum(q.score for q in quizzes) / len(quizzes) if quizzes else 0.0
    
    weak_topics = [t.title for t in topics if any(q.topic_id == t.id and q.score < 60.0 for q in quizzes)]
    
    # Stub default analyzer/motivation messages if plan hasn't been generated
    analysis_report = {
        "completion_rate": round(completion_rate, 1),
        "average_quiz_score": round(avg_score, 1),
        "productivity_score": 85,
        "learning_score": 75,
        "weekly_summary": "Looking good! Make sure to take regular Pomodoro breaks to keep study sessions focused.",
        "suggestions": ["Spend more time reviewing hard subjects.", "Use active recall definitions."],
        "productivity_badge": "Focus Explorer"
    }
    
    motivation_report = {
        "daily_motivation": "Mistakes are proof that you are trying. Keep learning!",
        "study_tips": ["Start with your hardest topic first.", "Limit digital distractions during review blocks."],
        "pomodoro_suggestion": "Study 25m, break 5m.",
        "break_reminder": "Get up and stretch for 5 minutes.",
        "stress_management": "Breathe deeply. Your efforts are building understanding."
    }
    
    return {
        "exam": exam,
        "topics_count": total_topics,
        "completion_rate": round(completion_rate, 1),
        "active_streak": active_streak,
        "average_quiz_score": round(avg_score, 1),
        "weak_topics": weak_topics,
        "today_plan": today_plan,
        "schedule": schedule_data,
        "analysis": analysis_report,
        "motivation": motivation_report
    }

@router.get("/progress")
def get_progress_logs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logs = db.query(Progress).filter(Progress.user_id == current_user.id).order_by(Progress.date.asc()).all()
    return logs

@router.post("/progress/log-study")
def log_study_hours(study_log: StudyLog, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    today = datetime.date.today()
    
    # 1. Update or create progress entry for today
    progress = db.query(Progress).filter(Progress.user_id == current_user.id, Progress.date == today).first()
    
    subjects = db.query(Subject).filter(Subject.user_id == current_user.id).all()
    sub_ids = [s.id for s in subjects]
    topics = db.query(Topic).filter(Topic.subject_id.in_(sub_ids)).all() if sub_ids else []
    total_topics = len(topics)
    completed_topics = len([t for t in topics if t.status == "completed"])
    completion_rate = (completed_topics / total_topics * 100.0) if total_topics > 0 else 0.0
    
    # Calculate streak: check if yesterday had study hours logged
    yesterday = today - datetime.timedelta(days=1)
    yesterday_progress = db.query(Progress).filter(Progress.user_id == current_user.id, Progress.date == yesterday).first()
    
    new_streak = 1
    if yesterday_progress and yesterday_progress.study_hours > 0:
        new_streak = yesterday_progress.active_streak + 1
    elif progress:
        new_streak = progress.active_streak
        
    if progress:
        progress.study_hours += study_log.hours
        progress.completion = completion_rate
        progress.active_streak = max(progress.active_streak, new_streak)
    else:
        progress = Progress(
            user_id=current_user.id,
            date=today,
            study_hours=study_log.hours,
            completion=completion_rate,
            active_streak=new_streak
        )
        db.add(progress)
        
    db.commit()
    db.refresh(progress)
    return progress

@router.post("/quiz/submit")
def submit_quiz(submission: QuizSubmit, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Verify topic ownership
    topic = db.query(Topic).join(Subject).filter(Topic.id == submission.topic_id, Subject.user_id == current_user.id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
        
    # 1. Update Quiz score
    quiz = db.query(Quiz).filter(Quiz.topic_id == topic.id).first()
    if not quiz:
        quiz = Quiz(
            topic_id=topic.id,
            questions=json.dumps([]),
            score=submission.score
        )
        db.add(quiz)
    else:
        quiz.score = submission.score
        
    # 2. Automatically update Topic status/confidence based on score
    if submission.score >= 80.0:
        topic.confidence = "high"
        topic.status = "completed"
    elif submission.score >= 50.0:
        topic.confidence = "medium"
        topic.status = "studying"
    else:
        topic.confidence = "low"
        topic.status = "studying"  # requires review
        
    # 3. Log average quiz score in Progress log for today
    today = datetime.date.today()
    progress = db.query(Progress).filter(Progress.user_id == current_user.id, Progress.date == today).first()
    
    if progress:
        progress.quiz_score = submission.score
    else:
        progress = Progress(
            user_id=current_user.id,
            date=today,
            quiz_score=submission.score
        )
        db.add(progress)
        
    db.commit()
    
    # 4. FEEDBACK LOOP: Trigger automatic schedule rebalancing
    # The scheduler runs to give weak topics more time
    updated_state = trigger_schedule_rebalance(current_user.id, db)
    
    return {
        "message": "Quiz submitted successfully. Study schedule has been rebalanced.",
        "score": submission.score,
        "rebalanced_schedule": updated_state.get("schedule") if updated_state else None,
        "analysis": updated_state.get("analysis") if updated_state else None
    }

# Expose flashcards retrieval per topic
@router.get("/topics/{topic_id}/flashcards")
def get_topic_flashcards(topic_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    topic = db.query(Topic).join(Subject).filter(Topic.id == topic_id, Subject.user_id == current_user.id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
        
    return db.query(Flashcard).filter(Flashcard.topic_id == topic_id).all()

# Expose notes retrieval per topic
@router.get("/topics/{topic_id}/notes")
def get_topic_notes(topic_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    topic = db.query(Topic).join(Subject).filter(Topic.id == topic_id, Subject.user_id == current_user.id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
        
    note = db.query(Note).filter(Note.topic_id == topic_id).first()
    if not note:
        # Generate default notes on the fly
        note = Note(
            topic_id=topic_id,
            content=f"# {topic.title}\n\nNotes are pending generation. Trigger 'Generate Study Plan' to build AI Notes."
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        
    return note

# Expose quizzes retrieval per topic
@router.get("/topics/{topic_id}/quiz")
def get_topic_quiz(topic_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    topic = db.query(Topic).join(Subject).filter(Topic.id == topic_id, Subject.user_id == current_user.id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
        
    quiz = db.query(Quiz).filter(Quiz.topic_id == topic_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found for this topic. Please run 'Generate Study Plan' first.")
        
    return {
        "id": quiz.id,
        "topic_id": quiz.topic_id,
        "questions": json.loads(quiz.questions),
        "score": quiz.score,
        "difficulty": quiz.difficulty
    }

# Review Flashcard Spaced Repetition (SM-2 Algorithm)
# Request schema
class FlashcardReview(BaseModel):
    flashcard_id: int
    quality: int # Quality score 0-5 from SM-2 algorithm

@router.post("/flashcards/review")
def review_flashcard(review: FlashcardReview, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    card = db.query(Flashcard).join(Topic).join(Subject).filter(Flashcard.id == review.flashcard_id, Subject.user_id == current_user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")
        
    q = review.quality
    if q < 0 or q > 5:
        raise HTTPException(status_code=400, detail="Quality score must be between 0 and 5.")
        
    # SM-2 Algorithm Implementation
    if q >= 3:
        if card.repetitions == 0:
            card.interval = 1
        elif card.repetitions == 1:
            card.interval = 6
        else:
            card.interval = int(card.interval * card.ease_factor)
        card.repetitions += 1
    else:
        card.repetitions = 0
        card.interval = 1
        
    # Adjust ease factor
    card.ease_factor = card.ease_factor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    if card.ease_factor < 1.3:
        card.ease_factor = 1.3
        
    card.review_date = datetime.date.today() + datetime.timedelta(days=card.interval)
    db.commit()
    db.refresh(card)
    return card
