import os
import json
import httpx
import streamlit as st
from datetime import datetime

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

st.set_page_config(page_title="Study Planner Streamlit", layout="wide")

if "auth_token" not in st.session_state:
    st.session_state.auth_token = None

if "user" not in st.session_state:
    st.session_state.user = None

if "loading" not in st.session_state:
    st.session_state.loading = False


def api_headers():
    headers = {"Content-Type": "application/json"}
    if st.session_state.auth_token:
        headers["Authorization"] = f"Bearer {st.session_state.auth_token}"
    return headers


def api_post(path, payload=None, files=None):
    url = f"{API_BASE_URL}{path}"
    if files:
        with httpx.Client(timeout=180.0) as client:
            response = client.post(
                url,
                headers=api_headers(),
                files=files,
            )

    else:
        response = httpx.post(url, headers=api_headers(), json=payload, timeout=180.0)
    response.raise_for_status()
    return response.json()


def api_get(path):
    url = f"{API_BASE_URL}{path}"
    response = httpx.get(url, headers=api_headers(), timeout=180.0)
    response.raise_for_status()
    return response.json()


def login(email: str, password: str):
    payload = {"email": email.strip(), "password": password}
    data = api_post("/auth/login", payload)
    st.session_state.auth_token = data["access_token"]
    st.session_state.user = data.get("user")


def signup(name: str, email: str, password: str):
    payload = {"name": name, "email": email, "password": password}
    api_post("/auth/signup", payload)
    login(email, password)


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


def generate_plan(exam_id: int):
    return api_post(f"/ai/generate-plan/{exam_id}")


def chat_tutor(topic_title: str, question: str, chat_history: list):
    payload = {"topic_title": topic_title, "question": question, "chat_history": chat_history}
    return api_post("/ai/chat-tutor", payload)


st.title("Study Planner Streamlit UI")
st.markdown(
    "This Streamlit interface connects to the FastAPI backend and runs the AI planner through Ollama and PostgreSQL."
)

with st.sidebar:
    st.header("Session")
    if st.session_state.auth_token:
        st.success(f"Signed in as {st.session_state.user.get('email', 'student')}")
        if st.button("Logout"):
            st.session_state.auth_token = None
            st.session_state.user = None
            st.experimental_rerun()
    else:
        auth_tab = st.radio("Authenticate", ["Login", "Signup"])
        if auth_tab == "Login":
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login"):
                if not email.strip() or not password:
                    st.error("Enter both your email address and password.")
                else:
                    try:
                        login(email, password)
                        st.rerun()
                    except httpx.HTTPStatusError as exc:
                        try:
                            message = exc.response.json().get("detail", exc.response.text)
                        except (ValueError, AttributeError):
                            message = exc.response.text
                        st.error(f"Login failed: {message}")
                    except httpx.RequestError:
                        st.error("Cannot reach the API. Start the FastAPI backend on port 8000.")
        else:
            name = st.text_input("Name", key="signup_name")
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            if st.button("Signup"):
                try:
                    signup(name, email, password)
                    st.rerun()
                except httpx.HTTPStatusError as exc:
                    try:
                        error_data = exc.response.json()
                        message = error_data.get("detail", exc.response.text)
                    except Exception:
                        message = exc.response.text
                    st.error(f"Signup failed: {message}")
                except Exception as exc:
                    st.error(f"Signup failed: {exc}")

    st.divider()
    st.write("API Base URL")
    st.code(API_BASE_URL)

if not st.session_state.auth_token:
    st.stop()


tabs = st.tabs(["Dashboard", "Create Exam", "Generate Plan", "Chat Tutor"])

with tabs[0]:
    st.subheader("Dashboard")
    try:
        exams = api_get("/exams")
        st.write(f"You have {len(exams)} exam(s) in your account.")
        for exam in exams:
            st.write(f"**{exam['name']}** — {exam['exam_date']} — priority: {exam['priority']} — difficulty: {exam['difficulty']}")
    except Exception as exc:
        st.error(f"Unable to load exams: {exc}")

with tabs[1]:
    st.subheader("Create New Exam")
    with st.form(key="create_exam_form"):
        exam_name = st.text_input("Exam Name")
        exam_date = st.date_input("Exam Date", value=datetime.today())
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=1)
        difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"], index=1)
        subject_input = st.text_area(
            "Subjects (one per line, format: name,difficulty)",
            value="Math,medium\nPhysics,hard",
            height=120,
        )
        topic_input = st.text_area(
            "Topics (one per line, format: subject_name,title,status,confidence)",
            value="Math,Limits and Continuity,pending,medium\nPhysics,Kinematics,pending,low",
            height=160,
        )
        create_button = st.form_submit_button("Create Exam")
        if create_button:
            try:
                subjects = []
                topics = []
                for line in subject_input.splitlines():
                    if not line.strip():
                        continue
                    name, difficulty_value = [item.strip() for item in line.split(",", 1)]
                    subjects.append({"name": name, "difficulty": difficulty_value})
                for line in topic_input.splitlines():
                    if not line.strip():
                        continue
                    parts = [item.strip() for item in line.split(",")]
                    if len(parts) != 4:
                        st.warning("Topic rows must use format: subject_name,title,status,confidence")
                        continue
                    topics.append(
                        {
                            "subject_name": parts[0],
                            "title": parts[1],
                            "status": parts[2],
                            "confidence": parts[3],
                        }
                    )
                exam = create_exam(
                    exam_name,
                    exam_date.strftime("%Y-%m-%d"),
                    priority,
                    difficulty,
                    subjects,
                    topics,
                )
                st.success(f"Created exam: {exam['name']}")
            except Exception as exc:
                st.error(f"Failed to create exam: {exc}")

with tabs[2]:
    st.subheader("Generate Study Plan")
    try:
        exams = api_get("/exams")
        exam_options = {f"{exam['name']} ({exam['exam_date']})": exam['id'] for exam in exams}
        selected_label = st.selectbox("Choose Exam", list(exam_options.keys()))
        selected_exam_id = exam_options.get(selected_label)
        if st.button("Generate Study Plan"):
            with st.spinner("Generating plan via AI pipeline..."):
                result = generate_plan(selected_exam_id)
                st.success("Study plan generated successfully")
                st.json(result)
    except Exception as exc:
        st.error(f"Could not generate plan: {exc}")

with tabs[3]:
    st.subheader("Chat Tutor")
    topic_title = st.text_input("Topic Title")
    question = st.text_area("Your question")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if st.button("Ask Tutor"):
        try:
            response = chat_tutor(topic_title, question, st.session_state.chat_history)
            st.session_state.chat_history.append({"role": "user", "content": question})
            st.session_state.chat_history.append({"role": "assistant", "content": response["answer"]})
            st.success("Tutor answered")
        except Exception as exc:
            st.error(f"Chat tutor failed: {exc}")
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.info(f"You: {msg['content']}")
        else:
            st.write(f"**Tutor:** {msg['content']}")
