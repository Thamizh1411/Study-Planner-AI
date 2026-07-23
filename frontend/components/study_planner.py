"""Study Planner component - Create Exam and Generate Plan pages."""

import datetime
from datetime import date
import streamlit as st
from components.utils import fetch_exams, create_exam, generate_plan, fetch_exam_topics, fetch_exams as fetch_all_exams
from components.cards import SECTION_TITLE


def render_create_exam():
    """Render the Create Exam form."""
    SECTION_TITLE("📝 Configure Study Plan", "Input exam variables, syllabus subjects, and individual topics to schedule study logs.")

    with st.form(key="create_exam_form"):
        col1, col2 = st.columns(2)
        with col1:
            exam_name = st.text_input("Exam Subject / Title", placeholder="E.g., Final Term Exams")
        with col2:
            exam_date = st.date_input("Exam Target Date", value=date.today())

        col3, col4 = st.columns(2)
        with col3:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=1)
        with col4:
            difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"], index=1)

        st.markdown("### 📚 Subjects")
        subject_input = st.text_area(
            "Subjects (one per line, format: name,difficulty)",
            value="Math,medium\nPhysics,hard",
            height=100,
            help="Enter one subject per line: name,difficulty",
        )

        st.markdown("### 📋 Topics / Syllabus Chapters")
        topic_input = st.text_area(
            "Topics (one per line, format: subject_name,title,status,confidence)",
            value="Math,Limits and Continuity,pending,medium\nPhysics,Kinematics,pending,low",
            height=120,
            help="Format: subject_name,title,status,confidence",
        )

        submitted = st.form_submit_button("🚀 Save and Initialize Plan", type="primary", use_container_width=True)
        if submitted:
            try:
                subjects = []
                topics = []
                for line in subject_input.splitlines():
                    if not line.strip():
                        continue
                    parts = [item.strip() for item in line.split(",", 1)]
                    if len(parts) == 2:
                        subjects.append({"name": parts[0], "difficulty": parts[1]})

                for line in topic_input.splitlines():
                    if not line.strip():
                        continue
                    parts = [item.strip() for item in line.split(",")]
                    if len(parts) != 4:
                        st.warning(f"Skipping invalid topic line: {line}")
                        continue
                    topics.append({
                        "subject_name": parts[0],
                        "title": parts[1],
                        "status": parts[2],
                        "confidence": parts[3],
                    })

                if not exam_name.strip():
                    st.error("Please enter an exam name.")
                    return

                exam = create_exam(
                    exam_name,
                    exam_date.strftime("%Y-%m-%d"),
                    priority,
                    difficulty,
                    subjects,
                    topics,
                )
                st.success(f"✅ Created exam: {exam['name']}")
                st.balloons()
            except Exception as exc:
                st.error(f"Failed to create exam: {exc}")


def render_generate_plan():
    """Render the Generate Study Plan page."""
    SECTION_TITLE("🧠 Generate Study Plan", "Let the multi-agent system evaluate your subjects and build the calendar.")

    exams = fetch_all_exams()

    if not exams:
        st.info("No exams found. Create an exam first on the Dashboard.")
        return

    exam_options = {f"{ex['name']} ({ex.get('exam_date', 'N/A')})": ex['id'] for ex in exams}
    selected_label = st.selectbox("Choose Exam", list(exam_options.keys()), key="gen_plan_exam_select")
    selected_exam_id = exam_options.get(selected_label)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("✨ Generate Study Plan", type="primary", use_container_width=True):
            with st.spinner("AI Agents are generating your personalized study plan..."):
                try:
                    result = generate_plan(selected_exam_id)
                    st.success("✅ Study plan generated successfully!")
                    if result.get("schedule"):
                        st.markdown("### 📅 Schedule Generated")
                        dates = list(result["schedule"].keys())
                        st.info(f"Plan spans {len(dates)} days from {dates[0]} to {dates[-1]}")
                    if result.get("analysis"):
                        st.markdown("### 📊 Analysis")
                        st.json(result["analysis"])
                except Exception as exc:
                    st.error(f"Plan generation failed: {exc}")

    with col2:
        if st.button("🔄 Refresh Exams", use_container_width=True):
            st.rerun()

