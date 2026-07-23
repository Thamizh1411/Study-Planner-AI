"""Reusable sidebar component matching React dark theme."""

import datetime
import streamlit as st
from components.utils import fetch_dashboard, logout as auth_logout

PAGES = {
    "Dashboard": "📊",
    "Study Planner": "📅",
    "Learning Desk": "📖",
    "Practice Quiz": "❓",
    "AI Tutor": "💬",
    "Analytics Report": "📈",
}


def render_sidebar():
    """Render the glass sidebar with navigation, user profile, streak, exam countdown."""
    with st.sidebar:
        # Custom CSS for sidebar
        st.markdown("""
        <style>
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(15,15,20,0.95), rgba(10,10,15,0.98)) !important;
            border-right: 1px solid rgba(255,255,255,0.06) !important;
            backdrop-filter: blur(20px) !important;
        }
        [data-testid="stSidebar"] [data-testid="stSidebarNav"] {
            display: none !important;
        }
        [data-testid="stSidebar"] .stButton button {
            width: 100%;
            text-align: left;
            background: transparent;
            border: none;
            color: #9e9ea7;
            font-size: 14px;
            font-weight: 500;
            padding: 12px 16px;
            border-radius: 12px;
            transition: all 0.2s ease;
        }
        [data-testid="stSidebar"] .stButton button:hover {
            background: rgba(255,255,255,0.05);
            color: #ffffff;
        }
        [data-testid="stSidebar"] .stButton button[kind="primary"] {
            background: linear-gradient(135deg, rgba(37,99,235,0.2), rgba(79,70,229,0.2));
            border: 1px solid rgba(59,112,255,0.3);
            color: #60a5fa;
            font-weight: 600;
        }
        /* Hide default sidebar elements */
        .css-1d391kg, .css-1wrcr25 {display: none;}
        section[data-testid="stSidebar"] > div:first-child {
            padding-top: 0 !important;
        }
        section[data-testid="stSidebar"] > div:nth-child(2) {
            padding-top: 0 !important;
        }
        </style>
        """, unsafe_allow_html=True)

        # ── Logo Header ──
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;padding:20px 16px 16px;margin-bottom:8px;">
            <div style="
                background:linear-gradient(135deg,#2563eb,#4f46e5);
                border-radius:12px;
                padding:10px;
                font-size:18px;
                box-shadow:0 4px 15px rgba(59,112,255,0.2);
                line-height:1;
            ">📚</div>
            <div>
                <div style="font-size:18px;font-weight:800;color:#ffffff;letter-spacing:-0.02em;">
                    StudyPlanner <span style="color:#60a5fa;">AI</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── User Profile ──
        user = st.session_state.get("user", {})
        if user:
            initial = (user.get("name", "U") or "U")[0].upper()
            st.markdown(f"""
            <div style="
                margin:0 12px 16px;
                padding:14px;
                background:rgba(255,255,255,0.03);
                border:1px solid rgba(255,255,255,0.06);
                border-radius:14px;
                display:flex;
                align-items:center;
                gap:12px;
            ">
                <div style="
                    width:40px;height:40px;
                    background:linear-gradient(135deg,#7c3aed,#4f46e5);
                    border-radius:50%;
                    display:flex;align-items:center;justify-content:center;
                    color:white;font-weight:700;font-size:16px;
                ">{initial}</div>
                <div style="overflow:hidden;">
                    <div style="font-weight:600;font-size:13px;color:#ffffff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                        {user.get("name", "Student")}
                    </div>
                    <div style="font-size:11px;color:#6b6b7d;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                        {user.get("email", "student@edu.com")}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Study Streak & Exam Countdown ──
        dash_data = st.session_state.get("dashboard_data", {})
        if not dash_data:
            dash_data = fetch_dashboard()

        active_streak = dash_data.get("active_streak", 0) if dash_data else 0
        exam_data = dash_data.get("exam", None) if dash_data else None
        days_left = 0
        exam_name = "No exam set"
        if exam_data:
            try:
                exam_date_str = exam_data.get("exam_date", "")
                if isinstance(exam_date_str, str):
                    exam_date = datetime.datetime.strptime(exam_date_str, "%Y-%m-%d").date()
                else:
                    exam_date = exam_date_str
                days_left = (exam_date - datetime.date.today()).days
                exam_name = exam_data.get("name", "Exam")
            except Exception:
                pass

        st.markdown(f"""
        <div style="
            margin:0 12px 16px;
            padding:14px;
            background:linear-gradient(135deg,rgba(249,115,22,0.08),rgba(245,158,11,0.05));
            border:1px solid rgba(249,115,22,0.15);
            border-radius:14px;
        ">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                <span style="font-size:20px;">🔥</span>
                <div>
                    <div style="font-size:10px;font-weight:700;color:#fb923c;text-transform:uppercase;letter-spacing:0.08em;">Study Streak</div>
                    <div style="font-size:16px;font-weight:700;color:#fed7aa;">{active_streak} Days</div>
                </div>
            </div>
            {f'''
            <div style="display:flex;align-items:center;gap:10px;padding-top:8px;border-top:1px solid rgba(255,255,255,0.05);">
                <span style="font-size:16px;">📅</span>
                <div>
                    <div style="font-size:10px;font-weight:600;color:#60a5fa;text-transform:uppercase;letter-spacing:0.05em;">{exam_name}</div>
                    <div style="font-size:14px;font-weight:700;color:#93c5fd;">{days_left} Days Left</div>
                </div>
            </div>
            ''' if exam_data else ''}
        </div>
        """, unsafe_allow_html=True)

        # ── Navigation ──
        st.markdown('<div style="padding:0 12px;margin-bottom:8px;">', unsafe_allow_html=True)

        current_page = st.session_state.get("page", "Dashboard")

        for page_name, icon in PAGES.items():
            is_active = current_page == page_name
            btn_type = "primary" if is_active else "secondary"

            if st.button(
                f"{icon}  {page_name}",
                key=f"nav_{page_name}",
                type=btn_type,
                use_container_width=True,
            ):
                st.session_state.page = page_name
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        # ── Logout ──
        st.markdown('<div style="padding:0 12px;margin-top:24px;">', unsafe_allow_html=True)
        if st.button("🚪  Sign Out", use_container_width=True):
            auth_logout()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

