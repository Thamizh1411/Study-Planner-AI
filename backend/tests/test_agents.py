import pytest
from backend.core.security import get_password_hash, verify_password
from backend.agents.scheduler import SchedulerAgent
from backend.agents.analyzer import PerformanceAnalyzerAgent
from backend.agents.state import PlannerState
from backend.agents.providers import LLMProvider

def test_password_hashing():
    password = "study_hard_test"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False

def test_scheduler_algorithm():
    # Verify that scheduler creates schedule, respects exam date and prioritizes subjects
    initial_state = {
        "student_profile": {"name": "Test student"},
        "subjects": [
            {"name": "Advanced Networks", "difficulty": "hard"},
            {"name": "Calculus", "difficulty": "easy"}
        ],
        "topics": [
            {"subject_name": "Advanced Networks", "title": "BGP Routing Protocol", "status": "pending", "confidence": "low"},
            {"subject_name": "Calculus", "title": "Limits and Continuity", "status": "completed", "confidence": "high"}
        ],
        "exam_date": "2026-08-20", # in the future
        "daily_hours": 3.0,
        "quiz_scores": [{"topic_title": "BGP Routing Protocol", "score": 45.0}], # low score makes it weak
        "schedule": {}
    }
    
    state = SchedulerAgent.execute(initial_state)
    schedule = state["schedule"]
    
    assert len(schedule) > 0
    # Let's check that BGP Routing Protocol is allocated hours because it's a weak topic from a hard subject
    found_bgp = False
    for day, items in schedule.items():
        for item in items:
            if item["topic_title"] == "BGP Routing Protocol":
                found_bgp = True
                assert item["hours"] > 0
                
    assert found_bgp is True

def test_analyzer_calculations():
    # Verify performance calculations
    state_with_data = {
        "topics": [
            {"title": "Topic A", "status": "completed"},
            {"title": "Topic B", "status": "pending"}
        ],
        "quiz_scores": [
            {"topic_title": "Topic A", "score": 90.0},
            {"topic_title": "Topic B", "score": 50.0}
        ],
        "schedule": {
            "2026-07-15": [
                {"topic_title": "Topic A", "hours": 2.0, "completed": True},
                {"topic_title": "Topic B", "hours": 2.0, "completed": False}
            ]
        }
    }
    
    state = PerformanceAnalyzerAgent.execute(state_with_data)
    analysis = state["analysis"]
    
    assert analysis["completion_rate"] == 50.0
    assert analysis["total_hours_scheduled"] == 4.0
    assert analysis["total_hours_completed"] == 2.0
    assert analysis["average_quiz_score"] == 70.0
    assert analysis["productivity_score"] == 50.0 # 2/4 hours completed
    assert len(analysis["weak_topics"]) == 1
    assert analysis["weak_topics"][0]["topic_title"] == "Topic B"


def test_provider_fallback_returns_local_response():
    response = LLMProvider.generate(
        prompt="Create a short summary for a study plan",
        system_prompt="You are a study assistant",
        json_mode=True,
        provider="gemini"
    )

    assert "mock" in response.lower() or "summary" in response.lower()
