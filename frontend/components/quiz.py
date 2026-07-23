"""Complete Practice Quiz page with timer, progress, and evaluation."""

import time
import streamlit as st
from components.utils import (
    fetch_exams, fetch_exam_topics, fetch_quiz_questions,
    submit_quiz_score, reset_quiz_state
)
from components.cards import SECTION_TITLE, BADGE


def render_quiz():
    """Render the full Practice Quiz page."""
    SECTION_TITLE("❓ Practice Arena", "Interactive adaptive testing. Scheduler rebalances after every attempt.")

    try:
        exams = fetch_exams()
    except Exception as e:
        st.error(f"⚠️ Cannot connect to backend: {e}")
        st.info("Make sure the FastAPI backend is running on port 8000.")
        return

    if not exams:
        st.warning("⚠️ No exams found. Create an exam on the Dashboard first, then generate a Study Plan to populate quiz questions.")
        return

    # ── Exam Selector ──
    exam_options = {f"{ex['name']} ({ex.get('exam_date', 'N/A')})": ex['id'] for ex in exams}
    selected_label = st.selectbox("Choose Exam", list(exam_options.keys()), key="quiz_exam_select")
    selected_exam_id = exam_options[selected_label]

    # ── Fetch Topics ──
    topics_key = f"quiz_topics_{selected_exam_id}"

    # Auto-fetch topics if not cached OR if exam changed
    if topics_key not in st.session_state or st.session_state.get("quiz_last_exam_id") != selected_exam_id:
        with st.spinner("Loading topics..."):
            try:
                st.session_state[topics_key] = fetch_exam_topics(selected_exam_id)
                st.session_state.quiz_last_exam_id = selected_exam_id
            except Exception as e:
                st.error(f"Failed to load topics: {e}")
                st.session_state[topics_key] = []
        st.rerun()

    if st.button("🔄 Refresh Topics", key="refresh_quiz_topics"):
        with st.spinner("Refreshing topics..."):
            try:
                st.session_state[topics_key] = fetch_exam_topics(selected_exam_id)
                reset_quiz_state()
            except Exception as e:
                st.error(f"Failed to refresh: {e}")
        st.rerun()

    topics = st.session_state[topics_key]

    if not topics:
        st.info("📭 No topics available. Go to **Study Planner → Generate Study Plan** to populate topics with quiz questions.")
        return

    # ── Auto-select first topic if none selected ──
    if st.session_state.get("selected_quiz_topic") not in [t.get("id") for t in topics]:
        st.session_state.selected_quiz_topic = topics[0]["id"]
        st.session_state.selected_quiz_topic_idx = 0
        reset_quiz_state()
        st.rerun()

    # ── Layout: Sidebar topics + Main quiz area ──
    col1, col2 = st.columns([1, 3])

    with col1:
        _render_topic_sidebar(topics)

    with col2:
        _render_quiz_area(topics)


def _render_topic_sidebar(topics):
    """Render the topic selection sidebar."""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(30,30,40,0.7), rgba(20,20,30,0.5));
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 16px;
    ">
        <h4 style="font-size:11px;font-weight:700;color:#9e9ea7;text-transform:uppercase;letter-spacing:0.08em;margin:0 0 12px;">📋 Topics</h4>
    """, unsafe_allow_html=True)

    selected_topic_id = st.session_state.get("selected_quiz_topic")

    for i, t in enumerate(topics):
        topic_id = t.get("id")
        is_selected = topic_id == selected_topic_id

        if st.button(
            f"{'●' if is_selected else '○'} {t['title']}",
            key=f"topic_btn_{topic_id}",
            use_container_width=True,
        ):
            if selected_topic_id != topic_id:
                reset_quiz_state()
                st.session_state.selected_quiz_topic = topic_id
                st.session_state.selected_quiz_topic_idx = i
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def _render_quiz_area(topics):
    """Render the main quiz workspace."""
    selected_topic_id = st.session_state.get("selected_quiz_topic")
    selected_idx = next((i for i, t in enumerate(topics) if t.get("id") == selected_topic_id), 0)
    selected_topic = topics[selected_idx]

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(30,30,40,0.7), rgba(20,20,30,0.5));
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 24px;
        position: relative;
        overflow: hidden;
        min-height: 300px;
    ">
        <div style="position:absolute;top:0;right:0;width:150px;height:150px;background:rgba(168,85,247,0.04);border-radius:50%;filter:blur(50px);pointer-events:none;"></div>
    """, unsafe_allow_html=True)

    # Load questions if not loaded
    if not st.session_state.quiz_questions:
        with st.spinner(f"Loading questions for {selected_topic['title']}..."):
            try:
                qs, diff = fetch_quiz_questions(selected_topic["id"])
                st.session_state.quiz_questions = qs
                st.session_state.quiz_difficulty = diff
                if qs:
                    st.session_state.quiz_timer_start = time.time()
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_result = None
                    st.session_state.rebalanced_schedule = None
                else:
                    st.warning(f"No questions found for '{selected_topic['title']}'. Generate a Study Plan first.")
            except Exception as e:
                st.error(f"Failed to load quiz questions: {e}")
        st.rerun()

    if st.session_state.quiz_questions:
        questions = st.session_state.quiz_questions
        diff = st.session_state.quiz_difficulty
        total_q = len(questions)

        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;padding-bottom:16px;border-bottom:1px solid rgba(255,255,255,0.06);margin-bottom:16px;">
            <div>
                <h3 style="font-size:18px;font-weight:700;color:#ffffff;margin:0;">{selected_topic['title']}</h3>
                <span style="font-size:11px;color:#6b6b7d;">Adaptive Level: <strong style="color:#a855f7;text-transform:capitalize;">{diff}</strong> | Questions: <strong>{total_q}</strong></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Timer ──
        if st.session_state.quiz_timer_start and not st.session_state.quiz_submitted:
            elapsed = time.time() - st.session_state.quiz_timer_start
            remaining = max(0, 300 - int(elapsed))
            mins, secs = divmod(remaining, 60)
            timer_color = "🟢" if remaining > 60 else "🟡" if remaining > 30 else "🔴"

            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
                <span style="font-size:13px;">{timer_color} Time remaining: <strong>{mins:02d}:{secs:02d}</strong></span>
                <span style="font-size:12px;color:#6b6b7d;">Question <strong>{st.session_state.get('quiz_current_index', 0)+1}</strong> of {total_q}</span>
            </div>
            """, unsafe_allow_html=True)

            progress_val = (st.session_state.get("quiz_current_index", 0) + 1) / total_q
            st.progress(progress_val)

            if remaining <= 0:
                st.warning("⏰ Time's up! Auto-submitting...")
                time.sleep(0.5)
                st.session_state.quiz_submitted = True
                st.rerun()

        st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)

        # ── Current Question ──
        current_idx = st.session_state.get("quiz_current_index", 0)
        if current_idx >= total_q:
            current_idx = total_q - 1
            st.session_state.quiz_current_index = current_idx

        q = questions[current_idx]
        q_id = q.get("id", current_idx)
        q_key = f"q_{q_id}"
        q_type = q.get("type", "mcq")

        st.markdown(f"""
        <div style="margin-bottom:16px;">
            <div style="display:flex;gap:10px;">
                <span style="width:28px;height:28px;background:rgba(99,102,241,0.15);border:1px solid rgba(99,102,241,0.25);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:#818cf8;flex-shrink:0;">{current_idx + 1}</span>
                <div>
                    <p style="font-size:15px;font-weight:600;color:#e4e4ec;margin:0;">{q['question_text']}</p>
                    {BADGE(q_type.replace('_', ' ').title(), '#a855f7')}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Render by Type ──
        disabled = st.session_state.quiz_submitted

        if q_type == "mcq":
            options = q.get("options", [])
            current_val = st.session_state.quiz_answers.get(q_key)
            idx = options.index(current_val) if current_val in options else 0
            selected_opt = st.radio("Choose an answer", options, index=idx, key=f"mcq_{q_id}",
                                   disabled=disabled, label_visibility="collapsed", horizontal=True)
            if not disabled:
                st.session_state.quiz_answers[q_key] = selected_opt

        elif q_type == "true_false":
            tf_options = ["True", "False"]
            current_val = st.session_state.quiz_answers.get(q_key)
            idx = tf_options.index(current_val) if current_val in tf_options else 0
            selected_tf = st.radio("True or False", tf_options, index=idx, key=f"tf_{q_id}",
                                  disabled=disabled, label_visibility="collapsed", horizontal=True)
            if not disabled:
                st.session_state.quiz_answers[q_key] = selected_tf

        elif q_type == "fill_blank":
            current_val = st.session_state.quiz_answers.get(q_key, "")
            answer = st.text_input("Your answer", value=current_val, key=f"fb_{q_id}",
                                  disabled=disabled, placeholder="Type the correct keyword...", label_visibility="collapsed")
            if not disabled:
                st.session_state.quiz_answers[q_key] = answer

        elif q_type in ("short_answer", "coding"):
            current_val = st.session_state.quiz_answers.get(q_key, "")
            height = 80 if q_type == "short_answer" else 100
            placeholder = "Write a concise explanation..." if q_type == "short_answer" else "# Write your code..."
            key_prefix = 'sa' if q_type == 'short_answer' else 'code'
            answer = st.text_area("Your answer", value=current_val, key=f"{key_prefix}_{q_id}",
                                 disabled=disabled, placeholder=placeholder, height=height, label_visibility="collapsed")
            if not disabled:
                st.session_state.quiz_answers[q_key] = answer

        # ── Navigation ──
        if not st.session_state.quiz_submitted:
            nav_cols = st.columns([1, 1, 1])
            with nav_cols[0]:
                if current_idx > 0 and st.button("◀ Previous", use_container_width=True):
                    st.session_state.quiz_current_index = current_idx - 1
                    st.rerun()
            with nav_cols[1]:
                if current_idx < total_q - 1 and st.button("Next ▶", type="primary", use_container_width=True):
                    st.session_state.quiz_current_index = current_idx + 1
                    st.rerun()
            with nav_cols[2]:
                if st.button("✅ Submit All", type="primary", use_container_width=True):
                    st.session_state.quiz_submitted = True
                    st.rerun()

        # ── Results ──
        if st.session_state.quiz_submitted:
            _render_quiz_results(selected_topic)

    else:
        st.markdown("""
        <div style="padding:48px 0;text-align:center;">
            <div style="font-size:48px;margin-bottom:12px;">📭</div>
            <p style="font-size:14px;color:#c4c4d0;font-weight:600;margin:0 0 8px;">No Quiz Questions Available</p>
            <p style="font-size:12px;color:#6b6b7d;max-width:400px;margin:0 auto 16px;">
                This topic has no quiz questions yet. Go to <strong>Study Planner → Generate Study Plan</strong> 
                to let the AI agents generate questions for all topics.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔄 Retry Load Quiz", use_container_width=True):
            reset_quiz_state()
            st.session_state.selected_quiz_topic = selected_topic["id"]
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def _render_quiz_results(selected_topic):
    """Render quiz evaluation results."""
    if st.session_state.quiz_result is None:
        with st.spinner("Evaluating your answers..."):
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
            try:
                result = submit_quiz_score(selected_topic["id"], score_pct)
                if result:
                    st.session_state.rebalanced_schedule = result.get("rebalanced_schedule")
            except Exception as e:
                st.warning(f"Could not submit score to backend: {e}")

            st.session_state.quiz_result = {
                "score": score_pct,
                "correct": correct_count,
                "total": total,
                "evaluation": evaluation,
            }
        st.rerun()

    result = st.session_state.quiz_result
    score = result["score"]

    if score >= 70:
        bg = "linear-gradient(135deg, rgba(5,150,105,0.15), rgba(4,120,87,0.1))"
        border = "rgba(5,150,105,0.3)"
        text_color = "#34d399"
    elif score >= 40:
        bg = "linear-gradient(135deg, rgba(217,119,6,0.15), rgba(180,83,9,0.1))"
        border = "rgba(217,119,6,0.3)"
        text_color = "#fbbf24"
    else:
        bg = "linear-gradient(135deg, rgba(220,38,38,0.15), rgba(185,28,28,0.1))"
        border = "rgba(220,38,38,0.3)"
        text_color = "#f87171"

    st.markdown(f"""
    <div style="background:{bg};border:1px solid {border};border-radius:16px;padding:24px;text-align:center;margin:20px 0;">
        <h2 style="margin:0;font-size:42px;color:{text_color};">{score:.1f}%</h2>
        <p style="color:#9e9ea7;margin:4px 0 0;">{result['correct']} / {result['total']} correct</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.rebalanced_schedule:
        st.success("🔄 **AI Scheduler Rebalance:** Study calendar updated dynamically!")

    with st.expander("📋 Detailed Evaluation", expanded=True):
        for ev in result["evaluation"]:
            if ev["is_correct"]:
                st.success(f"✅ **Q:** {ev['question_text']}")
            else:
                st.error(f"❌ **Q:** {ev['question_text']}")
                st.info(f"   **Expected:** `{ev['correct_answer']}` | **Your answer:** `{ev['student_answer']}`")

    if st.button("🔄 Retake Quiz", type="primary", use_container_width=True):
        reset_quiz_state()
        st.session_state.selected_quiz_topic = selected_topic["id"]
        st.rerun()

