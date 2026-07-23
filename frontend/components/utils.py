"""Utility functions for API calls and session management."""

import os
import time
import json
import httpx
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")


# ── Session State Initializers ──────────────────────────────────────────────

def init_session_state():
    """Initialize all required session state variables."""
    if "auth_token" not in st.session_state:
        st.session_state.auth_token = None
    if "user" not in st.session_state:
        st.session_state.user = None
    if "loading" not in st.session_state:
        st.session_state.loading = False
    if "page" not in st.session_state:
        st.session_state.page = "Dashboard"
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Quiz session state
    if "quiz_timer_start" not in st.session_state:
        st.session_state.quiz_timer_start = None
    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = {}
    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False
    if "quiz_result" not in st.session_state:
        st.session_state.quiz_result = None
    if "quiz_questions" not in st.session_state:
        st.session_state.quiz_questions = []
    if "quiz_difficulty" not in st.session_state:
        st.session_state.quiz_difficulty = "medium"
    if "rebalanced_schedule" not in st.session_state:
        st.session_state.rebalanced_schedule = None
    if "selected_quiz_topic" not in st.session_state:
        st.session_state.selected_quiz_topic = None
    if "quiz_exam_topics" not in st.session_state:
        st.session_state.quiz_exam_topics = []
    if "quiz_current_index" not in st.session_state:
        st.session_state.quiz_current_index = 0

    # Dashboard cache
    if "dashboard_data" not in st.session_state:
        st.session_state.dashboard_data = None
    if "progress_logs" not in st.session_state:
        st.session_state.progress_logs = None

    # Learning desk state
    if "notes_content" not in st.session_state:
        st.session_state.notes_content = ""
    if "flashcards" not in st.session_state:
        st.session_state.flashcards = []
    if "flipped_card_id" not in st.session_state:
        st.session_state.flipped_card_id = None
    if "ocr_result" not in st.session_state:
        st.session_state.ocr_result = None
    if "rag_answer" not in st.session_state:
        st.session_state.rag_answer = ""
    if "rag_sources" not in st.session_state:
        st.session_state.rag_sources = []


# ── API Helpers ─────────────────────────────────────────────────────────────

def api_headers():
    headers = {"Content-Type": "application/json"}
    if st.session_state.auth_token:
        headers["Authorization"] = f"Bearer {st.session_state.auth_token}"
    return headers


def api_post(path, payload=None, files=None):
    url = f"{API_BASE_URL}{path}"
    if files:
        with httpx.Client(timeout=300.0) as client:
            response = client.post(url, headers=api_headers(), files=files)
    else:
        response = httpx.post(url, headers=api_headers(), json=payload, timeout=300.0)
    response.raise_for_status()
    return response.json()


def api_get(path):
    url = f"{API_BASE_URL}{path}"
    response = httpx.get(url, headers=api_headers(), timeout=300.0)
    response.raise_for_status()
    return response.json()


# ── Auth Functions ──────────────────────────────────────────────────────────

def login(email: str, password: str):
    payload = {"email": email.strip(), "password": password}
    data = api_post("/auth/login", payload)
    st.session_state.auth_token = data["access_token"]
    st.session_state.user = data.get("user")
    st.session_state.page = "Dashboard"


def signup(name: str, email: str, password: str):
    payload = {"name": name, "email": email, "password": password}
    api_post("/auth/signup", payload)
    login(email, password)


def logout():
    st.session_state.auth_token = None
    st.session_state.user = None
    st.session_state.page = "Dashboard"
    reset_quiz_state()
    st.session_state.chat_history = []


# ── Exam Functions ──────────────────────────────────────────────────────────

def create_exam(exam_name: str, exam_date: str, priority: str, difficulty: str, subjects: list, topics: list):
    payload = {
        "name": exam_name,
        "exam_date": exam_date,
        "priority": priority,
        "difficulty": difficulty,
        "subjects": subjects,
        "topics": topics,
    }
    return api_post("/exams", payload)


def fetch_exams():
    try:
        return api_get("/exams")
    except Exception:
        return []


def fetch_exam_topics(exam_id: int):
    try:
        data = api_get(f"/exams/{exam_id}/details")
        return data.get("topics", [])
    except Exception:
        return []


def delete_exam(exam_id: int):
    try:
        api_post(f"/exams/delete/{exam_id}")
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 405:
            # Try DELETE method
            import httpx as hp
            url = f"{API_BASE_URL}/exams/{exam_id}"
            response = hp.delete(url, headers=api_headers(), timeout=30.0)
            response.raise_for_status()
        else:
            raise


# ── Plan Functions ──────────────────────────────────────────────────────────

def generate_plan(exam_id: int):
    return api_post(f"/ai/generate-plan/{exam_id}")


# ── Quiz Functions ──────────────────────────────────────────────────────────

def reset_quiz_state():
    st.session_state.quiz_timer_start = None
    st.session_state.quiz_answers = {}
    st.session_state.quiz_submitted = False
    st.session_state.quiz_result = None
    st.session_state.quiz_questions = []
    st.session_state.quiz_difficulty = "medium"
    st.session_state.rebalanced_schedule = None
    st.session_state.quiz_current_index = 0


def fetch_quiz_questions(topic_id: int):
    try:
        data = api_get(f"/progress/topics/{topic_id}/quiz")
        return data.get("questions", []), data.get("difficulty", "medium")
    except Exception:
        return [], "medium"


def submit_quiz_score(topic_id: int, score: float):
    try:
        return api_post("/progress/quiz/submit", {"topic_id": topic_id, "score": score})
    except Exception as exc:
        st.error(f"Failed to submit quiz: {exc}")
        return None


# ── Dashboard Functions ─────────────────────────────────────────────────────

def fetch_dashboard():
    try:
        data = api_get("/progress/dashboard")
        st.session_state.dashboard_data = data
        return data
    except Exception:
        return st.session_state.dashboard_data or {}


def fetch_progress_logs():
    try:
        logs = api_get("/progress/progress")
        st.session_state.progress_logs = logs
        return logs
    except Exception:
        return st.session_state.progress_logs or []


# ── Tutor Functions ─────────────────────────────────────────────────────────

def chat_tutor(topic_title: str, question: str, chat_history: list):
    payload = {"topic_title": topic_title, "question": question, "chat_history": chat_history}
    return api_post("/ai/chat-tutor", payload)


# ── Learning Desk Functions ─────────────────────────────────────────────────

def fetch_topic_notes(topic_id: int):
    try:
        data = api_get(f"/progress/topics/{topic_id}/notes")
        return data.get("content", "")
    except Exception:
        return ""


def fetch_topic_flashcards(topic_id: int):
    try:
        return api_get(f"/progress/topics/{topic_id}/flashcards")
    except Exception:
        return []


def review_flashcard(flashcard_id: int, quality: int):
    try:
        return api_post("/progress/flashcards/review", {
            "flashcard_id": flashcard_id,
            "quality": quality
        })
    except Exception:
        return None


def ocr_upload(file, topic_id: int):
    try:
        files = {"file": (file.name, file.getvalue(), "image/jpeg")}
        return api_post(f"/ai/ocr-upload?topic_id={topic_id}", files=files)
    except Exception as exc:
        st.error(f"OCR failed: {exc}")
        return None


def pdf_upload(file):
    try:
        files = {"file": (file.name, file.getvalue(), "application/pdf")}
        return api_post("/ai/pdf-upload", files=files)
    except Exception as exc:
        st.error(f"PDF upload failed: {exc}")
        return None


def pdf_query(query: str):
    try:
        return api_post("/ai/pdf-query", {"query": query})
    except Exception as exc:
        return {"answer": f"Query failed: {exc}", "sources": []}


# ── Study Logging ───────────────────────────────────────────────────────────

def log_study_hours(hours: float):
    try:
        return api_post("/progress/progress/log-study", {"hours": hours})
    except Exception as exc:
        st.error(f"Failed to log hours: {exc}")
        return None

