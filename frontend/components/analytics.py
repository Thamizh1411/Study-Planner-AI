"""Analytics page with Plotly charts and study insights."""

import streamlit as st
from components.utils import fetch_dashboard, fetch_progress_logs
from components.cards import SECTION_TITLE, STAT_CARD
from components.charts import study_hours_chart, quiz_scores_chart, render_heatmap


def render_analytics():
    """Render the full Analytics page."""
    SECTION_TITLE("📈 Academic Analytics", "Deep analysis metrics of your study logs, streak consistency, and quiz outputs.")

    dash_data = fetch_dashboard()
    logs_data = fetch_progress_logs()

    if not dash_data or not dash_data.get("exam"):
        st.warning("No active exam data. Create an exam and generate a study plan first.")
        return

    # ── Metrics Row ──
    st.markdown('<div style="margin-bottom:24px;">', unsafe_allow_html=True)
    completion_rate = dash_data.get("completion_rate", 0)
    active_streak = dash_data.get("active_streak", 0)
    avg_score = dash_data.get("average_quiz_score", 0)
    topics_count = dash_data.get("topics_count", 0)

    stat_cols = st.columns(4)
    with stat_cols[0]:
        STAT_CARD("Completion Rate", f"{completion_rate:.1f}%", "Syllabus progress", "📚", "#3b70ff")
    with stat_cols[1]:
        STAT_CARD("Active Streak", f"{active_streak} days", "Consistency", "🔥", "#f97316")
    with stat_cols[2]:
        STAT_CARD("Avg Quiz Score", f"{avg_score:.1f}%", "Performance", "🎯", "#a855f7")
    with stat_cols[3]:
        STAT_CARD("Topics", f"{topics_count}", "Total syllabus items", "📖", "#06b6d4")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Charts Row ──
    chart_cols = st.columns(2)
    with chart_cols[0]:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(30,30,40,0.7), rgba(20,20,30,0.5));
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
        ">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;">
                <span style="font-size:18px;">📊</span>
                <h4 style="font-size:12px;font-weight:700;color:#e4e4ec;text-transform:uppercase;letter-spacing:0.08em;margin:0;">Study Duration Log</h4>
            </div>
        </div>
        """, unsafe_allow_html=True)
        study_hours_chart(logs_data)

    with chart_cols[1]:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(30,30,40,0.7), rgba(20,20,30,0.5));
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
        ">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;">
                <span style="font-size:18px;">🎯</span>
                <h4 style="font-size:12px;font-weight:700;color:#e4e4ec;text-transform:uppercase;letter-spacing:0.08em;margin:0;">Quiz Evaluation Scores</h4>
            </div>
        </div>
        """, unsafe_allow_html=True)
        quiz_scores_chart(logs_data)

    # ── Heatmap ──
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(30,30,40,0.7), rgba(20,20,30,0.5));
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
    ">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;">
            <span style="font-size:18px;">📅</span>
            <h4 style="font-size:12px;font-weight:700;color:#e4e4ec;text-transform:uppercase;letter-spacing:0.08em;margin:0;">Study Consistency Heatmap</h4>
        </div>
    """, unsafe_allow_html=True)
    render_heatmap(logs_data)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Analysis & Weak Topics ──
    analysis = dash_data.get("analysis", {})
    weak_topics = dash_data.get("weak_topics", [])

    analysis_cols = st.columns(2)
    with analysis_cols[0]:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(30,30,40,0.7), rgba(20,20,30,0.5));
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 16px;
            padding: 20px;
        ">
            <h4 style="font-size:12px;font-weight:700;color:#e4e4ec;text-transform:uppercase;letter-spacing:0.08em;margin:0 0 16px;">📊 Performance Analysis</h4>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px;">
                <div style="padding:12px;background:rgba(0,0,0,0.3);border-radius:12px;border:1px solid rgba(255,255,255,0.06);">
                    <p style="font-size:9px;color:#6b6b7d;text-transform:uppercase;font-weight:600;margin:0;">Productivity Score</p>
                    <p style="font-size:20px;font-weight:800;color:#60a5fa;margin:4px 0 0;">{analysis.get('productivity_score', 'N/A')}/100</p>
                </div>
                <div style="padding:12px;background:rgba(0,0,0,0.3);border-radius:12px;border:1px solid rgba(255,255,255,0.06);">
                    <p style="font-size:9px;color:#6b6b7d;text-transform:uppercase;font-weight:600;margin:0;">Learning Score</p>
                    <p style="font-size:20px;font-weight:800;color:#a855f7;margin:4px 0 0;">{analysis.get('learning_score', 'N/A')}/100</p>
                </div>
            </div>
            <p style="font-size:12px;color:#6b6b7d;line-height:1.5;font-style:italic;">{analysis.get('weekly_summary', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)

        suggestions = analysis.get("suggestions", [])
        if suggestions:
            st.markdown('<p style="font-size:10px;font-weight:700;color:#6b6b7d;text-transform:uppercase;margin:8px 0;">AI Suggestions</p>', unsafe_allow_html=True)
            for s in suggestions:
                st.markdown(f'<p style="font-size:12px;color:#6b6b7d;margin:0 0 4px;">💡 {s}</p>', unsafe_allow_html=True)

    with analysis_cols[1]:
        if weak_topics:
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, rgba(239,68,68,0.05), rgba(220,38,38,0.03));
                border: 1px solid rgba(239,68,68,0.15);
                border-radius: 16px;
                padding: 20px;
            ">
                <h4 style="font-size:12px;font-weight:700;color:#ef4444;text-transform:uppercase;letter-spacing:0.08em;margin:0 0 12px;">⚠️ Weak Topics</h4>
            """, unsafe_allow_html=True)
            for t in weak_topics:
                st.markdown(f"""
                <div style="padding:10px;background:rgba(0,0,0,0.2);border-radius:10px;border:1px solid rgba(239,68,68,0.1);margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-size:12px;color:#fca5a5;font-weight:600;">{t}</span>
                    <span style="font-size:9px;color:#ef4444;font-weight:700;background:rgba(239,68,68,0.1);padding:2px 8px;border-radius:6px;border:1px solid rgba(239,68,68,0.15);">Needs Attention</span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("""
                <p style="font-size:10px;font-weight:700;color:#9e9ea7;text-transform:uppercase;margin:12px 0 8px;">Recommended Actions</p>
                <p style="font-size:11px;color:#6b6b7d;margin:0 0 4px;">• Review AI Notes for these topics</p>
                <p style="font-size:11px;color:#6b6b7d;margin:0 0 4px;">• Use SM-2 Spaced Flashcards</p>
                <p style="font-size:11px;color:#6b6b7d;margin:0;">• Ask the AI Chat Tutor</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, rgba(5,150,105,0.05), rgba(4,120,87,0.03));
                border: 1px solid rgba(5,150,105,0.15);
                border-radius: 16px;
                padding: 20px;
                text-align:center;
            ">
                <div style="font-size:40px;margin-bottom:8px;">✅</div>
                <h4 style="font-size:14px;font-weight:700;color:#34d399;margin:0 0 4px;">No Weak Topics</h4>
                <p style="font-size:12px;color:#6b6b7d;margin:0;">Great job! Your quiz scores indicate strong understanding across all topics.</p>
            </div>
            """, unsafe_allow_html=True)

    # ── Motivation ──
    motivation = dash_data.get("motivation", {})
    if motivation:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(99,102,241,0.05), rgba(139,92,246,0.05));
            border: 1px solid rgba(99,102,241,0.1);
            border-radius: 16px;
            padding: 20px;
            margin-top: 20px;
        ">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                <span style="font-size:18px;">💪</span>
                <h4 style="font-size:12px;font-weight:700;color:#818cf8;text-transform:uppercase;letter-spacing:0.08em;margin:0;">Daily Motivation</h4>
            </div>
            <p style="font-size:13px;color:#c4c4d0;font-style:italic;">"{motivation.get('daily_motivation', 'Keep learning!')}"</p>
        </div>
        """, unsafe_allow_html=True)

