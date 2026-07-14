import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from backend.database.connection import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=True) # password can be null for OAuth logins
    provider = Column(String, default="email") # email, google, github
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    subjects = relationship("Subject", back_populates="user", cascade="all, delete-orphan")
    exams = relationship("Exam", back_populates="user", cascade="all, delete-orphan")
    progress = relationship("Progress", back_populates="user", cascade="all, delete-orphan")

class Subject(Base):
    __tablename__ = "subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    difficulty = Column(String, default="medium") # easy, medium, hard
    
    user = relationship("User", back_populates="subjects")
    topics = relationship("Topic", back_populates="subject", cascade="all, delete-orphan")

class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    status = Column(String, default="pending") # pending, studying, completed
    confidence = Column(String, default="medium") # low, medium, high
    
    subject = relationship("Subject", back_populates="topics")
    notes = relationship("Note", back_populates="topic", cascade="all, delete-orphan")
    flashcards = relationship("Flashcard", back_populates="topic", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="topic", cascade="all, delete-orphan")

class Exam(Base):
    __tablename__ = "exams"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    exam_date = Column(Date, nullable=False)
    priority = Column(String, default="medium") # low, medium, high
    difficulty = Column(String, default="medium")
    
    user = relationship("User", back_populates="exams")
    study_plans = relationship("StudyPlan", back_populates="exam", cascade="all, delete-orphan")

class StudyPlan(Base):
    __tablename__ = "study_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False)
    plan_json = Column(Text, nullable=False) # JSON representation of the timetable
    generated_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    exam = relationship("Exam", back_populates="study_plans")

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False) # Markdown content
    embedding = Column(Text, nullable=True) # JSON representation of vector embeddings (optional)
    
    topic = relationship("Topic", back_populates="notes")

class Flashcard(Base):
    __tablename__ = "flashcards"
    
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    
    # SM-2 Spaced Repetition Fields
    review_date = Column(Date, default=datetime.date.today)
    interval = Column(Integer, default=0) # days
    ease_factor = Column(Float, default=2.5)
    repetitions = Column(Integer, default=0)
    
    topic = relationship("Topic", back_populates="flashcards")

class Quiz(Base):
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    questions = Column(Text, nullable=False) # JSON string of all quiz questions
    answers = Column(Text, nullable=True) # JSON string of user submissions or correct answers
    score = Column(Float, default=0.0) # Percentage score
    difficulty = Column(String, default="medium")
    generated_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    topic = relationship("Topic", back_populates="quizzes")

class Progress(Base):
    __tablename__ = "progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, default=datetime.date.today)
    study_hours = Column(Float, default=0.0)
    quiz_score = Column(Float, default=0.0)
    completion = Column(Float, default=0.0) # Overall topics completion %
    active_streak = Column(Integer, default=0)
    
    user = relationship("User", back_populates="progress")

class PDFChunk(Base):
    __tablename__ = "pdf_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    doc_name = Column(String, nullable=False)
    chunk_text = Column(Text, nullable=False)

