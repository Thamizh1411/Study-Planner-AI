import os
import json
import httpx
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import time
import datetime
from datetime import date, timedelta

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

st.set_page_config(page_title="Study Planner Streamlit", layout="wide")

# ── Session State Initializers ──────────────────────────────────────────────
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "loading" not in st.session_state:
    st.session_state.loading = False

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

# Analytics cache
if "analytics_data" not in st.session_state:
    st.session_state.analytics_data = None
if "progress_logs" not in st.session_state:
    st.session_state.progress_logs = None


# ── Helper Functions ────────────────────────────────────────────────────────

def api_headers():
    headers = {"Content-Type": "application/json"}
    if st.session_state.auth_token:
        headers["Authorization"] = f"Bearer {st.session_state.auth_token}"
    return headers


def api_post(path, payload=None, files=None):
    url = f"{API_BASE_URL}{path}"
    if files:
        with httpx.Client(timeout=180.0) as client:
            response = client.post(url, headers=api_headers(), files=files)
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


def reset_quiz_state():
    """Reset all quiz-related session state."""
    st.session_state.quiz_timer_start = None
    st.session_state.quiz_answers = {}
    st.session_state.quiz_submitted = False
    st.session_state.quiz_result = None
    st.session_state.quiz_questions = []
    st.session_state.quiz_difficulty = "medium"
    st.session_state.rebalanced_schedule = None


def fetch_exam_topics(exam_id: int):
    """Fetch exam details including topics."""
    try:
        data = api_get(f"/exams/{exam_id}/details")
        return data.get("topics", [])
    except Exception:
        return []


def fetch_quiz_questions(topic_id: int):
    """Fetch quiz questions for a topic."""
    try:
        data = api_get(f"/progress/topics/{topic_id}/quiz")
        return data.get("questions", []), data.get("difficulty", "medium")
    except Exception:
        return [], "medium"


def submit_quiz_score(topic_id: int, score: float):
    """Submit quiz score to backend and get rebalanced schedule."""
    try:
        return api_post("/progress/quiz/submit", {"topic_id": topic_id, "score": score})
    except Exception as exc:
        st.error(f"Failed to submit quiz: {exc}")
        return None


def fetch_dashboard():
    """Fetch dashboard data for analytics."""
    try:
        return api_get("/progress/dashboard")
    except Exception:
        return None


def fetch_progress_logs():
    """Fetch progress logs for analytics charts."""
    try:
        return api_get("/progress/progress")
    except Exception:
        return []


# ── Sidebar Auth ────────────────────────────────────────────────────────────

st.title("📚 Study Planner Streamlit UI")
st.markdown(
    "Connect to the FastAPI backend and run the AI planner through Ollama / Gemini."
)

with st.sidebar:
    st.header("🔐 Session")
    if st.session_state.auth_token:
        st.success(f"Signed in as **{st.session_state.user.get('email', 'student')}**")
        if st.button("🚪 Logout"):
            st.session_state.auth_token = None
            st.session_state.user = None
            reset_quiz_state()
            st.rerun()
    else:
        auth_tab = st.radio("Authenticate", ["Login", "Signup"])
        if auth_tab == "Login":
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("🔑 Login"):
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
            if st.button("📝 Signup"):
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
    st.write("**API Base URL**")
    st.code(API_BASE_URL)

if not st.session_state.auth_token:
    st.stop()

# ── Main Tabs ───────────────────────────────────────────────────────────────

tabs = st.tabs([
    "📊 Dashboard",
    "📝 Create Exam",
    "🧠 Generate Plan",
    "❓ Quizzes",
    "📈 Analytics",
    "💬 Chat Tutor",
])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 0 — DASHBOARD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tabs[0]:
    st.subheader("📊 Dashboard")
    try:
        exams = api_get("/exams")
        st.write(f"You have **{len(exams)}** exam(s) in your account.")
        for exam in exams:
            st.write(f"- **{exam['name']}** — {exam['exam_date']} — priority: {exam['priority']} — difficulty: {exam['difficulty']}")
    except Exception as exc:
        st.error(f"Unable to load exams: {exc}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 1 — CREATE EXAM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tabs[1]:
    st.subheader("📝 Create New Exam")
    with st.form(key="create_exam_form"):
        exam_name = st.text_input("Exam Name")
        exam_date = st.date_input("Exam Date", value=date.today())
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

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 2 — GENERATE PLAN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tabs[2]:
    st.subheader("🧠 Generate Study Plan")
    try:
        exams = api_get("/exams")
        exam_options = {f"{exam['name']} ({exam['exam_date']})": exam['id'] for exam in exams}
        selected_label = st.selectbox("Choose Exam", list(exam_options.keys()), key="gen_plan_exam")
        selected_exam_id = exam_options.get(selected_label)
        if st.button("Generate Study Plan"):
            with st.spinner("Generating plan via AI pipeline..."):
                result = generate_plan(selected_exam_id)
                st.success("✅ Study plan generated successfully")
                st.json(result)
    except Exception as exc:
        st.error(f"Could not generate plan: {exc}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 3 — QUIZZES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tabs[3]:
    st.subheader("❓ Practice Arena — Interactive Adaptive Testing")
    st.markdown("Select a topic, answer the questions, and get AI-rebalanced study schedule.")

    # Fetch exams and topics
    try:
        exams_list = api_get("/exams")
    except Exception:
        exams_list = []

    if not exams_list:
        st.warning("No exams found. Create an exam on the **Create Exam** tab first.")
    else:
        exam_options = {f"{ex['name']} ({ex['exam_date']})": ex['id'] for ex in exams_list}
        selected_exam_label = st.selectbox("Choose Exam", list(exam_options.keys()), key="quiz_exam_select")
        selected_exam_id = exam_options[selected_exam_label]

        # Fetch topics when exam changes
        topics_key = f"quiz_topics_{selected_exam_id}"
        if topics_key not in st.session_state:
            st.session_state[topics_key] = fetch_exam_topics(selected_exam_id)

        if st.button("🔄 Refresh Topics", key="refresh_quiz_topics"):
            st.session_state[topics_key] = fetch_exam_topics(selected_exam_id)
            reset_quiz_state()
            st.rerun()

        topics = st.session_state[topics_key]

        if not topics:
            st.info("No topics available. Generate a Study Plan first to populate quizzes.")
        else:
            # Layout: sidebar topics + main quiz area
            col1, col2 = st.columns([1, 3])

            # ── Topic Selector Sidebar ──
            with col1:
                st.markdown("### 📋 Topics")
                topic_titles = [t["title"] for t in topics]
                selected_topic_idx = st.selectbox(
                    "Select a topic",
                    range(len(topic_titles)),
                    format_func=lambda i: f"{topic_titles[i]} ({topics[i].get('subject_name', '')})",
                    key="quiz_topic_selector",
                    label_visibility="collapsed",
                )
                selected_topic = topics[selected_topic_idx]

                # Check if topic changed
                prev_topic_id = st.session_state.get("selected_quiz_topic")
                if prev_topic_id != selected_topic["id"]:
                    reset_quiz_state()
                    st.session_state.selected_quiz_topic = selected_topic["id"]
                    st.rerun()

            # ── Main Quiz Area ──
            with col2:
                # Load quiz questions if not loaded
                if not st.session_state.quiz_questions and selected_topic:
                    qs, diff = fetch_quiz_questions(selected_topic["id"])
                    st.session_state.quiz_questions = qs
                    st.session_state.quiz_difficulty = diff
                    if qs:
                        st.session_state.quiz_timer_start = time.time()
                        st.session_state.quiz_submitted = False
                        st.session_state.quiz_answers = {}
                        st.session_state.quiz_result = None
                        st.session_state.rebalanced_schedule = None

                # Display quiz header
                if st.session_state.quiz_questions:
                    st.markdown(f"### 📖 {selected_topic['title']}")
                    diff = st.session_state.quiz_difficulty
                    st.caption(f"Adaptive Level: **{diff.capitalize()}** | Questions: **{len(st.session_state.quiz_questions)}**")

                    # ── Timer ──
                    if st.session_state.quiz_timer_start and not st.session_state.quiz_submitted:
                        elapsed = time.time() - st.session_state.quiz_timer_start
                        remaining = max(0, 300 - int(elapsed))  # 5 min = 300 sec
                        mins, secs = divmod(remaining, 60)
                        timer_color = "🟢" if remaining > 60 else "🟡" if remaining > 30 else "🔴"
                        st.markdown(f"{timer_color} Time remaining: **{mins:02d}:{secs:02d}**")

                        if remaining <= 0:
                            st.warning("⏰ Time's up! Auto-submitting...")
                            time.sleep(0.5)
                            st.session_state.quiz_submitted = True
                            st.rerun()

                    st.divider()

                    # ── Render Questions ──
                    for q_idx, q in enumerate(st.session_state.quiz_questions):
                        q_id = q.get("id", q_idx)
                        q_key = f"q_{q_id}"
                        st.markdown(f"**Q{q_idx + 1}.** {q['question_text']}  `[{q.get('type', 'mcq')}]`")

                        if q["type"] == "mcq":
                            options = q.get("options", [])
                            current_val = st.session_state.quiz_answers.get(q_key)
                            selected_opt = st.radio(
                                "Choose an answer",
                                options,
                                index=options.index(current_val) if current_val in options else 0,
                                key=f"mcq_{q_id}",
                                disabled=st.session_state.quiz_submitted,
                                label_visibility="collapsed",
                            )
                            if not st.session_state.quiz_submitted:
                                st.session_state.quiz_answers[q_key] = selected_opt

                        elif q["type"] == "true_false":
                            tf_options = ["True", "False"]
                            current_val = st.session_state.quiz_answers.get(q_key)
                            selected_tf = st.radio(
                                "True or False",
                                tf_options,
                                index=tf_options.index(current_val) if current_val in tf_options else 0,
                                key=f"tf_{q_id}",
                                disabled=st.session_state.quiz_submitted,
                                label_visibility="collapsed",
                                horizontal=True,
                            )
                            if not st.session_state.quiz_submitted:
                                st.session_state.quiz_answers[q_key] = selected_tf

                        elif q["type"] == "fill_blank":
                            current_val = st.session_state.quiz_answers.get(q_key, "")
                            answer = st.text_input(
                                "Your answer",
                                value=current_val,
                                key=f"fb_{q_id}",
                                disabled=st.session_state.quiz_submitted,
                                placeholder="Type the correct keyword...",
                                label_visibility="collapsed",
                            )
                            if not st.session_state.quiz_submitted:
                                st.session_state.quiz_answers[q_key] = answer

                        elif q["type"] == "short_answer":
                            current_val = st.session_state.quiz_answers.get(q_key, "")
                            answer = st.text_area(
                                "Your answer",
                                value=current_val,
                                key=f"sa_{q_id}",
                                disabled=st.session_state.quiz_submitted,
                                placeholder="Write a concise explanation...",
                                height=80,
                                label_visibility="collapsed",
                            )
                            if not st.session_state.quiz_submitted:
                                st.session_state.quiz_answers[q_key] = answer

                        elif q["type"] == "coding":
                            current_val = st.session_state.quiz_answers.get(q_key, "")
                            answer = st.text_area(
                                "Your code",
                                value=current_val,
                                key=f"code_{q_id}",
                                disabled=st.session_state.quiz_submitted,
                                placeholder="# Write your code or pseudo-code here...",
                                height=100,
                                label_visibility="collapsed",
                            )
                            if not st.session_state.quiz_submitted:
                                st.session_state.quiz_answers[q_key] = answer

                        st.divider()

                    # ── Submit Button ──
                    if not st.session_state.quiz_submitted:
                        if st.button("✅ Submit Answers", type="primary", use_container_width=True):
                            st.session_state.quiz_submitted = True
                            st.rerun()

                    # ── Evaluation Results ──
                    if st.session_state.quiz_submitted:
                        if st.session_state.quiz_result is None:
                            # Evaluate
                            correct_count = 0
                            total = len(st.session_state.quiz_questions)
                            evaluation = []
                            for q_idx, q in enumerate(st.session_state.quiz_questions):
                                q_id = q.get("id", q_idx)
                                q_key = f"q_{q_id}"
                                student_ans = str(st.session_state.quiz_answers.get(q_key, "")).strip().lower()
                                correct_ans = str(q.get("correct_answer", "")).strip().lower()

                                is_correct = False
                                if q["type"] in ("mcq", "true_false"):
                                    is_correct = student_ans == correct_ans
                                else:
                                    # Keyword overlap check
                                    correct_words = correct_ans.split()
                                    is_correct = any(word in student_ans for word in correct_words) or student_ans == correct_ans

                                if is_correct:
                                    correct_count += 1
                                evaluation.append({
                                    "question_id": q_id,
                                    "question_text": q["question_text"],
                                    "is_correct": is_correct,
                                    "correct_answer": q.get("correct_answer", ""),
                                    "student_answer": st.session_state.quiz_answers.get(q_key, "(No response)"),
                                    "type": q["type"],
                                })

                            score_pct = (correct_count / total * 100.0) if total > 0 else 0.0

                            # Submit to backend
                            result = submit_quiz_score(selected_topic["id"], score_pct)
                            if result:
                                st.session_state.rebalanced_schedule = result.get("rebalanced_schedule")

                            st.session_state.quiz_result = {
                                "score": score_pct,
                                "correct": correct_count,
                                "total": total,
                                "evaluation": evaluation,
                            }
                            st.rerun()

                        # Display Results
                        result = st.session_state.quiz_result
                        score = result["score"]

                        # Score card with conditional coloring
                        if score >= 70:
                            bg = "linear-gradient(135deg, #05966920, #04785720)"
                            border = "#05966960"
                            text_color = "#34d399"
                        elif score >= 40:
                            bg = "linear-gradient(135deg, #d9770620, #b4530920)"
                            border = "#d9770660"
                            text_color = "#fbbf24"
                        else:
                            bg = "linear-gradient(135deg, #dc262620, #b91c1c20)"
                            border = "#dc262660"
                            text_color = "#f87171"

                        st.markdown(
                            f"""
                            <div style="
                                background: {bg};
                                border: 1px solid {border};
                                border-radius: 16px;
                                padding: 24px;
                                text-align: center;
                                margin-bottom: 20px;
                            ">
                                <h2 style="margin:0; font-size: 48px; color: {text_color};">
                                    {score:.1f}%
                                </h2>
                                <p style="color: #ccc; margin:4px 0 0;">
                                    {result['correct']} / {result['total']} correct
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        # Rebalanced schedule notification
                        if st.session_state.rebalanced_schedule:
                            st.success("🔄 **AI Scheduler Rebalance:** Study calendar updated dynamically! Low-confidence topics have been assigned extra hours.")

                        # Per-question evaluation
                        st.markdown("### 📋 Detailed Evaluation")
                        for ev in result["evaluation"]:
                            if ev["is_correct"]:
                                st.success(f"✅ **Q:** {ev['question_text']} — *Correct!*")
                            else:
                                st.error(f"❌ **Q:** {ev['question_text']}")
                                st.info(f"   **Expected:** `{ev['correct_answer']}` | **Your answer:** `{ev['student_answer']}`")

                        # Retake button
                        if st.button("🔄 Retake Quiz", use_container_width=True):
                            reset_quiz_state()
                            st.session_state.selected_quiz_topic = selected_topic["id"]
                            st.rerun()

                elif selected_topic:
                    st.info("📭 No quiz questions found for this topic. Generate a Study Plan first to populate quizzes.")
                    if st.button("🔄 Load Quiz"):
                        qs, diff = fetch_quiz_questions(selected_topic["id"])
                        st.session_state.quiz_questions = qs
                        st.session_state.quiz_difficulty = diff
                        if qs:
                            st.session_state.quiz_timer_start = time.time()
                        st.rerun()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 4 — ANALYTICS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tabs[4]:
    st.subheader("📈 Academic Analytics")
    st.markdown("Deep analysis metrics of your study logs, streak consistency, and quiz outputs.")

    # Fetch data
    dash_data = fetch_dashboard()
    logs_data = fetch_progress_logs()

    if not dash_data or not dash_data.get("exam"):
        st.warning("No active exam data. Create an exam and generate a study plan first.")
    else:
        # Metrics row
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("📚 Completion Rate", f"{dash_data.get('completion_rate', 0):.1f}%")
        with col_m2:
            st.metric("🔥 Active Streak", f"{dash_data.get('active_streak', 0)} days")
        with col_m3:
            st.metric("📊 Avg Quiz Score", f"{dash_data.get('average_quiz_score', 0):.1f}%")
        with col_m4:
            st.metric("📖 Topics", dash_data.get("topics_count", 0))

        st.divider()

        # ── Study Hours Line Chart ──
        st.markdown("### 📊 Study Duration Log")
        if logs_data:
            df_logs = pd.DataFrame(logs_data)
            df_logs["date"] = pd.to_datetime(df_logs["date"])
            df_logs = df_logs.sort_values("date")

            fig_hours = go.Figure()
            fig_hours.add_trace(go.Scatter(
                x=df_logs["date"],
                y=df_logs["study_hours"],
                mode="lines+markers",
                name="Study Hours",
                line=dict(color="#3b70ff", width=2),
                fill="tozeroy",
                fillcolor="rgba(59, 112, 255, 0.08)",
            ))
            fig_hours.update_layout(
                template="plotly_dark",
                xaxis_title="Date",
                yaxis_title="Hours",
                height=300,
                margin=dict(l=20, r=20, t=20, b=20),
                hovermode="x unified",
            )
            st.plotly_chart(fig_hours, use_container_width=True)
        else:
            st.info("No study logs yet. Log study hours to see trends here.")

        st.divider()

        # ── Quiz Scores Bar Chart ──
        st.markdown("### 🎯 Quiz Evaluation Scores")
        if logs_data:
            df_scores = pd.DataFrame(logs_data)
            df_scores["date"] = pd.to_datetime(df_scores["date"])
            df_scores = df_scores.sort_values("date")
            # Filter out entries with no quiz score
            df_scores = df_scores[df_scores["quiz_score"] > 0]

            if not df_scores.empty:
                fig_scores = go.Figure()
                fig_scores.add_trace(go.Bar(
                    x=df_scores["date"],
                    y=df_scores["quiz_score"],
                    name="Quiz Score",
                    marker_color="#a855f7",
                    marker_line_color="#7c3aed",
                    marker_line_width=1,
                    opacity=0.85,
                ))
                fig_scores.add_hline(
                    y=70,
                    line_dash="dash",
                    line_color="#34d399",
                    annotation_text="70% Target",
                    annotation_font_color="#34d399",
                )
                fig_scores.update_layout(
                    template="plotly_dark",
                    xaxis_title="Date",
                    yaxis_title="Score (%)",
                    yaxis=dict(range=[0, 100]),
                    height=300,
                    margin=dict(l=20, r=20, t=20, b=20),
                    hovermode="x unified",
                )
                st.plotly_chart(fig_scores, use_container_width=True)
            else:
                st.info("No quiz scores recorded yet. Complete quizzes to see scores here.")
        else:
            st.info("No quiz scores recorded yet.")

        st.divider()

        # ── Study Consistency Heatmap ──
        st.markdown("### 🔥 Study Consistency Heatmap")
        st.caption("Visualize daily study hours for the last 4 weeks. Darker cells = more hours studied.")

        # Build heatmap data from logs
        today_dt = date.today()
        heatmap_data = {}
        if logs_data:
            for log in logs_data:
                log_date_str = log["date"]
                if isinstance(log_date_str, str):
                    log_date = datetime.datetime.strptime(log_date_str, "%Y-%m-%d").date()
                else:
                    log_date = log_date_str
                heatmap_data[log_date.isoformat()] = log.get("study_hours", 0)

        # Generate 4 weeks of data (28 days)
        dates_list = [(today_dt - timedelta(days=i)) for i in range(27, -1, -1)]
        weekdays_labels = ["Mon", "", "Wed", "", "Fri", "", "Sun"]

        # Prepare matrix: 7 rows (days of week) x 4 cols (weeks)
        matrix = [[0] * 4 for _ in range(7)]
        for i, d in enumerate(dates_list):
            col_idx = i // 7
            row_idx = d.weekday()  # Monday=0, Sunday=6
            iso = d.isoformat()
            val = heatmap_data.get(iso, 0)
            matrix[row_idx][col_idx] = val

        # Define color scale
        def heat_color(val):
            if val == 0:
                return "#1a1a2e"
            if val < 1.5:
                return "#1e3a5f"
            if val < 3.0:
                return "#2563eb"
            return "#60a5fa"

        # Build custom HTML heatmap
        heat_html = '<table style="border-collapse: collapse;">'
        # Header
        heat_html += '<tr><td style="width:30px;height:20px;"></td>'
        for w in range(4):
            heat_html += f'<td style="width:20px;height:20px;text-align:center;font-size:10px;color:#666;">W{w+1}</td>'
        heat_html += '</tr>'

        for row_idx in range(7):
            heat_html += '<tr>'
            heat_html += f'<td style="width:30px;height:20px;font-size:10px;color:#666;text-align:right;padding-right:4px;">{weekdays_labels[row_idx]}</td>'
            for col_idx in range(4):
                val = matrix[row_idx][col_idx]
                color = heat_color(val)
                tooltip = f"{val:.1f}h" if val > 0 else "No study"
                heat_html += f'<td style="width:20px;height:20px;padding:1px;"><div title="{tooltip}" style="width:18px;height:18px;border-radius:3px;background:{color};border:1px solid rgba(255,255,255,0.05);"></div></td>'
            heat_html += '</tr>'

        heat_html += '</table>'

        # Legend
        legend_html = """
        <div style="display:flex;gap:12px;align-items:center;font-size:11px;color:#999;margin-top:8px;">
            <span>Less</span>
            <div style="width:14px;height:14px;border-radius:3px;background:#1a1a2e;border:1px solid rgba(255,255,255,0.1);"></div>
            <div style="width:14px;height:14px;border-radius:3px;background:#1e3a5f;border:1px solid rgba(255,255,255,0.1);"></div>
            <div style="width:14px;height:14px;border-radius:3px;background:#2563eb;border:1px solid rgba(255,255,255,0.1);"></div>
            <div style="width:14px;height:14px;border-radius:3px;background:#60a5fa;border:1px solid rgba(255,255,255,0.1);"></div>
            <span>More</span>
        </div>
        """

        st.markdown(f'{heat_html}{legend_html}', unsafe_allow_html=True)

        st.divider()

        # ── Analysis & Weak Topics ──
        analysis = dash_data.get("analysis", {})
        weak_topics = dash_data.get("weak_topics", [])

        col_a1, col_a2 = st.columns(2)
        with col_a1:
            st.markdown("### 📊 Performance Analysis")
            st.markdown(f"- **Productivity Score:** {analysis.get('productivity_score', 'N/A')}/100")
            st.markdown(f"- **Learning Score:** {analysis.get('learning_score', 'N/A')}/100")
            st.markdown(f"- **Weekly Summary:** _{analysis.get('weekly_summary', 'N/A')}_")

            if analysis.get("suggestions"):
                st.markdown("**AI Suggestions:**")
                for s in analysis["suggestions"]:
                    st.markdown(f"- 💡 {s}")

        with col_a2:
            if weak_topics:
                st.markdown("### ⚠️ Weak Topics Requiring Review")
                for t in weak_topics:
                    st.markdown(f"- 🔴 **{t}** — Needs attention")
                st.markdown("**Recommended Actions:**")
                st.markdown("- Review AI-generated Notes for these topics")
                st.markdown("- Use SM-2 Spaced Flashcards")
                st.markdown("- Ask the AI Chat Tutor for explanations")
            else:
                st.markdown("### ✅ No Weak Topics")
                st.markdown("Great job! Your quiz scores indicate strong understanding across all topics.")

        # Motivation
        motivation = dash_data.get("motivation", {})
        if motivation:
            st.divider()
            st.markdown("### 💪 Daily Motivation")
            st.info(f"_{motivation.get('daily_motivation', 'Keep learning!')}_")
            if motivation.get("study_tips"):
                st.markdown("**Study Tips:**")
                for tip in motivation["study_tips"]:
                    st.markdown(f"- 📌 {tip}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 5 — CHAT TUTOR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tabs[5]:
    st.subheader("💬 Chat Tutor")
    topic_title = st.text_input("Topic Title", key="tutor_topic")
    question = st.text_area("Your question", key="tutor_question")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if st.button("Ask Tutor", key="tutor_ask"):
        if not topic_title.strip() or not question.strip():
            st.error("Enter both a topic title and a question.")
        else:
            try:
                with st.spinner("Tutor is thinking..."):
                    response = chat_tutor(topic_title, question, st.session_state.chat_history)
                st.session_state.chat_history.append({"role": "user", "content": question})
                st.session_state.chat_history.append({"role": "assistant", "content": response["answer"]})
                st.success("Tutor answered")
            except Exception as exc:
                st.error(f"Chat tutor failed: {exc}")
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.info(f"🧑‍🎓 You: {msg['content']}")
        else:
            st.markdown(f"**🤖 Tutor:** {msg['content']}")
