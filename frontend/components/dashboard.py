"""Dashboard component matching React dark theme."""

import datetime
import streamlit as st
from components.utils import fetch_dashboard, fetch_exams, generate_plan, delete_exam, log_study_hours, create_exam
from components.cards import STAT_CARD, GLASS_CARD, SECTION_TITLE, BADGE


def render_dashboard():
    """Render the main dashboard page."""
    dash_data = fetch_dashboard()

    SECTION_TITLE("Study Dashboard", "Welcome back to your study planner dashboard.")

    # ── Top Action Buttons ──
    col_actions1, col_actions2, col_actions3 = st.columns([1, 1, 1])
    exam = dash_data.get("exam") if dash_data else None
    has_schedule = bool(dash_data and dash_data.get("schedule", {}))

    with col_actions1:
        if exam and not has_schedule:
            if st.button("✨ Compile Multi-Agent Plan", type="primary", use_container_width=True):
                with st.spinner("AI Agents generating your study plan..."):
                    try:
                        result = generate_plan(exam.get("id"))
                        st.success("✅ Study plan generated successfully!")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Plan generation failed: {exc}")

    # ── Stat Cards Row ──
    completion_rate = dash_data.get("completion_rate", 0) if dash_data else 0
    active_streak = dash_data.get("active_streak", 0) if dash_data else 0
    avg_quiz_score = dash_data.get("average_quiz_score", 0) if dash_data else 0
    weak_topics = dash_data.get("weak_topics", []) if dash_data else []
    weak_count = len(weak_topics)

    stat_cols = st.columns(4)
    metrics = [
        ("Active Streak", f"{active_streak} Days", "Consistent studies", "🔥", "#f97316"),
        ("Topic Completion", f"{completion_rate:.0f}%", "Syllabus progression", "📖", "#3b70ff"),
        ("Quiz Accuracy", f"{avg_quiz_score:.0f}%", "Performance rating", "🎓", "#a855f7"),
        ("Weak Areas", f"{weak_count} Topics", "Need rebalancing review", "⚠️", "#ef4444"),
    ]
    for i, (col, (title, value, subtitle, icon, color)) in enumerate(zip(stat_cols, metrics)):
        with col:
            STAT_CARD(title, value, subtitle, icon, color)

    st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)

    # ── Main Content ──
    if not exam:
        _render_empty_state()
    else:
        _render_exam_dashboard(dash_data)


def _render_empty_state():
    """Render empty state when no exam is configured."""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(30,30,40,0.7), rgba(20,20,30,0.5));
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 20px;
        padding: 60px 40px;
        text-align: center;
        max-width: 500px;
        margin: 32px auto;
    ">
        <div style="font-size: 48px; margin-bottom: 16px; display:inline-block; animation: bounce 2s infinite;">📅</div>
        <h3 style="font-size: 22px; font-weight: 800; color: #ffffff; margin-bottom: 8px;">No Active Exam Plans</h3>
        <p style="font-size: 13px; color: #6b6b7d; max-width: 350px; margin: 0 auto 24px;">
            Create your exam schedule, add subjects and syllabus topics, and let the AI agents plan your daily hours.
        </p>
    </div>
    <style>
    @keyframes bounce {
        0%,100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }
    </style>
    """, unsafe_allow_html=True)


def _render_exam_dashboard(dash_data):
    """Render the dashboard with an active exam."""
    exam = dash_data.get("exam", {})
    today_plan = dash_data.get("today_plan", [])
    analysis = dash_data.get("analysis", {})
    motivation = dash_data.get("motivation", {})
    weak_topics = dash_data.get("weak_topics", [])

    # Calculate exam countdown
    try:
        exam_date_str = exam.get("exam_date", "")
        if isinstance(exam_date_str, str):
            exam_date = datetime.datetime.strptime(exam_date_str, "%Y-%m-%d").date()
        else:
            exam_date = exam_date_str
        days_left = (exam_date - datetime.date.today()).days
    except Exception:
        days_left = 0

    left_col, right_col = st.columns([2, 1])

    with left_col:
        _render_today_schedule(today_plan, exam, days_left, bool(dash_data.get("schedule", {})))
        _render_study_logging()
    with right_col:
        _render_motivation(motivation)
        _render_performance(analysis, weak_topics)


def _render_today_schedule(today_plan, exam, days_left, has_schedule):
    """Render today's study schedule card."""
    today_str = datetime.date.today().strftime("%A, %b %d")

    countdown_html = ""
    if days_left > 0:
        countdown_html = f'<span style="font-size:11px;font-weight:600;color:#60a5fa;background:rgba(59,112,255,0.1);padding:5px 12px;border-radius:10px;border:1px solid rgba(59,112,255,0.2);display:inline-flex;align-items:center;gap:5px;">📅 {days_left} Days to Exam</span>'
    else:
        countdown_html = '<span style="font-size:11px;font-weight:600;color:#ef4444;background:rgba(239,68,68,0.1);padding:5px 12px;border-radius:10px;border:1px solid rgba(239,68,68,0.2);">Exam Date Reached!</span>'

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(30,30,40,0.7), rgba(20,20,30,0.5));
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
    ">
        <div style="position:absolute;top:0;right:0;width:200px;height:200px;background:rgba(59,112,255,0.04);border-radius:50%;filter:blur(50px);pointer-events:none;"></div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
            <div>
                <h3 style="font-size:18px;font-weight:700;color:#ffffff;margin:0;">Today's Schedule</h3>
                <p style="font-size:12px;color:#6b6b7d;margin:4px 0 0;">{today_str}</p>
            </div>
            {countdown_html}
        </div>
    """, unsafe_allow_html=True)

    if not today_plan or len(today_plan) == 0:
        if not has_schedule:
            st.markdown("""
            <div style="padding:32px 0;text-align:center;">
                <p style="font-size:13px;color:#6b6b7d;margin-bottom:16px;">Your calendar is clear. Trigger AI planner compilation to build your study roadmap.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("✨ Compile Multi-Agent Plan", type="primary"):
                with st.spinner("Generating plan via AI pipeline..."):
                    try:
                        result = generate_plan(exam.get("id"))
                        st.success("✅ Study plan generated!")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Failed: {exc}")
        else:
            st.markdown('<p style="font-size:13px;color:#6b6b7d;padding:24px 0;text-align:center;">No tasks scheduled for today. Enjoy your break!</p>', unsafe_allow_html=True)
    else:
        for item in today_plan:
            is_completed = item.get("completed", False)
            topic_title = item.get("topic_title", "Study Session")
            subject_name = item.get("subject_name", "")
            item_type = item.get("type", "study")
            hours = item.get("hours", 1)

            status_icon = "✅" if is_completed else "📝"
            status_text = "Done" if is_completed else "Pending"
            status_color = "#34d399" if is_completed else "#6b6b7d"
            border_color = "rgba(52,211,153,0.2)" if is_completed else "rgba(255,255,255,0.06)"

            st.markdown(f"""
            <div style="
                padding:14px 16px;
                border: 1px solid {border_color};
                border-radius: 12px;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                background: {'rgba(52,211,153,0.03)' if is_completed else 'rgba(255,255,255,0.02)'};
            ">
                <div style="display:flex;align-items:center;gap:12px;">
                    <div style="font-size:18px;">{status_icon}</div>
                    <div>
                        <div style="font-size:14px;font-weight:600;color:#e4e4ec;">{topic_title}</div>
                        <div style="font-size:11px;color:#6b6b7d;">{subject_name} • <span style="text-transform:capitalize;">{item_type.replace('_',' ')}</span></div>
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap:12px;">
                    <span style="font-size:11px;font-weight:600;color:#9e9ea7;background:rgba(0,0,0,0.3);padding:4px 10px;border-radius:8px;border:1px solid rgba(255,255,255,0.06);">{hours} hrs</span>
                    <span style="font-size:11px;font-weight:600;color:{status_color};">{status_text}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        if has_schedule:
            st.markdown("""
            <div style="padding-top:12px;border-top:1px solid rgba(255,255,255,0.06);display:flex;justify-content:flex-end;">
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def _render_study_logging():
    """Render study hours logging card."""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(30,30,40,0.7), rgba(20,20,30,0.5));
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
    ">
        <h3 style="font-size:18px;font-weight:700;color:#ffffff;margin:0 0 4px;">Track Daily Progress</h3>
        <p style="font-size:12px;color:#6b6b7d;margin:0 0 16px;">Input study time to build consistency streaks and recalculate learning rates.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        hours_val = st.number_input("Study Hours", min_value=0.0, max_value=24.0, step=0.5, value=2.0, key="log_hours_input", label_visibility="collapsed", placeholder="E.g., 2.5 hours")
    with col2:
        if st.button("Log Study Time", type="primary", use_container_width=True):
            if hours_val > 0:
                with st.spinner("Logging..."):
                    result = log_study_hours(hours_val)
                    if result:
                        st.success(f"✅ Logged {hours_val} hours!")
                        st.rerun()
            else:
                st.error("Enter a positive number of hours.")
    st.markdown('</div>', unsafe_allow_html=True)


def _render_motivation(motivation):
    """Render daily motivation card."""
    daily_msg = motivation.get("daily_motivation", "Consistency is the engine of academic success.")
    study_tips = motivation.get("study_tips", [])

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(99,102,241,0.05), rgba(139,92,246,0.05));
        backdrop-filter: blur(12px);
        border: 1px solid rgba(99,102,241,0.1);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
    ">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
            <span style="font-size:18px;">🧠</span>
            <h4 style="font-size:12px;font-weight:700;color:#818cf8;text-transform:uppercase;letter-spacing:0.08em;margin:0;">AI Motivation Desk</h4>
        </div>
        <p style="font-size:13px;color:#c4c4d0;font-style:italic;line-height:1.6;margin-bottom:16px;">"{daily_msg}"</p>
    """, unsafe_allow_html=True)

    if study_tips:
        st.markdown('<p style="font-size:10px;font-weight:700;color:#818cf8;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">Study Tips</p>', unsafe_allow_html=True)
        for tip in study_tips:
            st.markdown(f'<p style="font-size:12px;color:#6b6b7d;margin:0 0 4px;">• {tip}</p>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def _render_performance(analysis, weak_topics):
    """Render performance analytics card."""
    prod_score = analysis.get("productivity_score", 80)
    learn_score = analysis.get("learning_score", 70)
    weekly_summary = analysis.get("weekly_summary", "Your personalized dashboard is processing metrics.")
    suggestions = analysis.get("suggestions", [])
    badge = analysis.get("productivity_badge", "")

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(30,30,40,0.7), rgba(20,20,30,0.5));
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
    ">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
            <h4 style="font-size:12px;font-weight:700;color:#e4e4ec;text-transform:uppercase;letter-spacing:0.08em;margin:0;">Performance Analytics</h4>
            {f'<span style="font-size:9px;font-weight:700;color:#fbbf24;background:rgba(251,191,36,0.1);border:1px solid rgba(251,191,36,0.2);padding:3px 8px;border-radius:6px;">{badge}</span>' if badge else ''}
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px;">
            <div style="padding:12px;background:rgba(0,0,0,0.3);border:1px solid rgba(255,255,255,0.06);border-radius:12px;">
                <div style="font-size:9px;color:#6b6b7d;text-transform:uppercase;letter-spacing:0.08em;font-weight:600;">Productivity</div>
                <div style="font-size:22px;font-weight:800;color:#60a5fa;margin-top:4px;">{prod_score}/100</div>
            </div>
            <div style="padding:12px;background:rgba(0,0,0,0.3);border:1px solid rgba(255,255,255,0.06);border-radius:12px;">
                <div style="font-size:9px;color:#6b6b7d;text-transform:uppercase;letter-spacing:0.08em;font-weight:600;">Learning</div>
                <div style="font-size:22px;font-weight:800;color:#a855f7;margin-top:4px;">{learn_score}/100</div>
            </div>
        </div>
        <p style="font-size:12px;color:#6b6b7d;line-height:1.5;">{weekly_summary}</p>
    """, unsafe_allow_html=True)

    if suggestions:
        st.markdown('<p style="font-size:10px;font-weight:700;color:#6b6b7d;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">Actions Required</p>', unsafe_allow_html=True)
        for sug in suggestions:
            st.markdown(f'<p style="font-size:12px;color:#6b6b7d;margin:0 0 4px;">• {sug}</p>', unsafe_allow_html=True)

    if weak_topics:
        st.markdown('<div style="margin-top:16px;padding-top:16px;border-top:1px solid rgba(255,255,255,0.06);">', unsafe_allow_html=True)
        st.markdown('<p style="font-size:10px;font-weight:700;color:#ef4444;margin-bottom:8px;">⚠️ Weak Topics</p>', unsafe_allow_html=True)
        for wt in weak_topics:
            st.markdown(f'<p style="font-size:11px;color:#fca5a5;margin:0 0 4px;">• {wt}</p>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

