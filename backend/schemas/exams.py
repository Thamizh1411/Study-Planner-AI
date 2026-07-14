import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class SubjectBase(BaseModel):
    name: str
    difficulty: str  # easy, medium, hard

class SubjectCreate(SubjectBase):
    pass

class SubjectOut(SubjectBase):
    id: int
    user_id: int
    
    model_config = ConfigDict(from_attributes=True)

class TopicBase(BaseModel):
    title: str
    status: str = "pending"  # pending, studying, completed
    confidence: str = "medium"  # low, medium, high

class TopicCreate(TopicBase):
    subject_name: str

class TopicOut(TopicBase):
    id: int
    subject_id: int
    
    model_config = ConfigDict(from_attributes=True)

class ExamBase(BaseModel):
    name: str
    exam_date: datetime.date
    priority: str = "medium"  # low, medium, high
    difficulty: str = "medium"

class ExamCreate(ExamBase):
    subjects: List[SubjectCreate]
    topics: List[TopicCreate]

class ExamOut(ExamBase):
    id: int
    user_id: int
    
    model_config = ConfigDict(from_attributes=True)
