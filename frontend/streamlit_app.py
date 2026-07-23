"""
Study Planner - Streamlit Frontend
====================================
Dark-themed UI matching the React frontend design.
All backend API calls and functionality preserved.
"""

import streamlit as st
from components.utils import init_session_state
from components.sidebar import render_sidebar
from components.auth import render_auth_page
from components.dashboard import render_dashboard
from components.study_planner import render_create_exam, render_generate_plan
from components.quiz import render_quiz
from components.tutor import render_tutor
from components.learning_desk import render_learning_desk
from components.analytics import render_analytics

# ── Page Configuration ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="StudyPlanner AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Initialize Session State ────────────────────────────────────────────────
init_session_state()

# ── Custom CSS - Dark Theme (Matching React Frontend) ───────────────────────
st.markdown(
    """
<style>
    /* ── Base Styles ── */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: #0a0a0c;
        background-image: 
            radial-gradient(at 0% 0%, rgba(59, 112, 255, 0.06) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(147, 51, 234, 0.06) 0px, transparent 50%);
    }
    
    /* ── Typography ── */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        color: #ffffff;
    }
    
    p, span, div, label {
        font-family: 'Outfit', sans-serif;
    }
    
    /* ── Main Content Area ── */
    .main > div {
        padding: 2rem 2.5rem;
    }
    
    @media (max-width: 768px) {
        .main > div {
            padding: 1rem;
        }
    }
    
    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        min-width: 280px !important;
        max-width: 280px !important;
        width: 280px !important;
        background: linear-gradient(180deg, rgba(15,15,20,0.98), rgba(10,10,15,0.99)) !important;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
        backdrop-filter: blur(20px) !important;
    }
    
    section[data-testid="stSidebar"] > div {
        padding: 0 !important;
        background: transparent !important;
    }
    
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
        display: none !important;
    }
    
    /* ── Buttons ── */
    .stButton button {
        font-family: 'Outfit', sans-serif;
        border-radius: 12px;
        font-weight: 600;
        font-size: 14px;
        padding: 10px 20px;
        transition: all 0.2s ease;
        border: none;
    }
    
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb, #4f46e5) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 15px rgba(59,112,255,0.15) !important;
        border: none !important;
    }
    
    .stButton button[kind="primary"]:hover {
        background: linear-gradient(135deg, #3b70ff, #6366f1) !important;
        box-shadow: 0 6px 20px rgba(59,112,255,0.25) !important;
        transform: translateY(-1px);
    }
    
    .stButton button[kind="secondary"] {
        background: rgba(30,30,40,0.6) !important;
        color: #c4c4d0 !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
    }
    
    .stButton button[kind="secondary"]:hover {
        background: rgba(40,40,55,0.8) !important;
        color: #ffffff !important;
        border-color: rgba(255,255,255,0.15) !important;
    }
    
    /* Sidebar nav buttons */
    section[data-testid="stSidebar"] .stButton button {
        width: 100%;
        text-align: left;
        padding: 12px 16px;
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 2px;
    }
    
    section[data-testid="stSidebar"] .stButton button[kind="primary"] {
        background: linear-gradient(135deg, rgba(37,99,235,0.2), rgba(79,70,229,0.2)) !important;
        border: 1px solid rgba(59,112,255,0.25) !important;
        color: #60a5fa !important;
        font-weight: 600;
        box-shadow: none !important;
    }
    
    section[data-testid="stSidebar"] .stButton button[kind="secondary"] {
        background: transparent !important;
        color: #9e9ea7 !important;
        border: none !important;
    }
    
    section[data-testid="stSidebar"] .stButton button[kind="secondary"]:hover {
        background: rgba(255,255,255,0.04) !important;
        color: #ffffff !important;
    }
    
    /* ── Input Fields ── */
    .stTextInput input, .stTextArea textarea, .stSelectbox select, .stNumberInput input {
        background: rgba(0,0,0,0.4) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 12px !important;
        color: #e4e4ec !important;
        font-family: 'Outfit', sans-serif;
        font-size: 14px;
        padding: 10px 14px !important;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: rgba(59,112,255,0.5) !important;
        box-shadow: 0 0 0 2px rgba(59,112,255,0.1) !important;
    }
    
    .stTextInput input::placeholder, .stTextArea textarea::placeholder {
        color: #4a4a5a !important;
    }
    
    /* ── Select Box ── */
    .stSelectbox div[data-baseweb="select"] {
        background: rgba(0,0,0,0.4) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 12px !important;
    }
    
    .stSelectbox div[data-baseweb="select"]:hover {
        border-color: rgba(59,112,255,0.3) !important;
    }
    
    /* ── Metric Cards ── */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(30,30,40,0.7), rgba(20,20,30,0.5));
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(12px);
    }
    
    [data-testid="stMetric"] > div {
        background: transparent !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #9e9ea7 !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 28px !important;
        font-weight: 800 !important;
    }
    
    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(0,0,0,0.3);
        border-radius: 14px;
        padding: 4px;
        border: 1px solid rgba(255,255,255,0.06);
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 8px 18px;
        font-size: 13px;
        font-weight: 500;
        color: #6b6b7d;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(30,30,45,0.8) !important;
        color: #ffffff !important;
    }
    
    /* ── Radio Buttons ── */
    .stRadio div[role="radiogroup"] {
        background: rgba(0,0,0,0.3);
        border-radius: 14px;
        padding: 4px;
        border: 1px solid rgba(255,255,255,0.06);
        gap: 2px;
    }
    
    .stRadio div[role="radiogroup"] label {
        border-radius: 10px;
        padding: 6px 16px;
        font-size: 13px;
        font-weight: 500;
        color: #6b6b7d !important;
        background: transparent;
    }
    
    .stRadio div[role="radiogroup"] label[data-checked="true"] {
        background: rgba(59,112,255,0.15) !important;
        color: #60a5fa !important;
        border: 1px solid rgba(59,112,255,0.2);
    }
    
    /* ── Info/Warning/Success/Error Boxes ── */
    .stAlert {
        border-radius: 12px;
        border: none;
        backdrop-filter: blur(8px);
    }
    
    .stAlert > div {
        border-radius: 12px;
        padding: 12px 16px;
    }
    
    /* ── Progress Bar ── */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #2563eb, #4f46e5) !important;
        border-radius: 10px;
    }
    
    .stProgress > div {
        background: rgba(255,255,255,0.06) !important;
        border-radius: 10px;
        height: 8px;
    }
    
    /* ── File Uploader ── */
    .stFileUploader section {
        border: 2px dashed rgba(255,255,255,0.1) !important;
        border-radius: 16px !important;
        background: rgba(0,0,0,0.2) !important;
    }
    
    .stFileUploader section:hover {
        border-color: rgba(59,112,255,0.3) !important;
    }
    
    /* ── Divider ── */
    hr {
        border-color: rgba(255,255,255,0.06) !important;
        margin: 20px 0 !important;
    }
    
    /* ── Expander ── */
    .streamlit-expanderHeader {
        background: rgba(30,30,40,0.5) !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 12px !important;
        color: #e4e4ec !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    
    .streamlit-expanderContent {
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
        background: rgba(0,0,0,0.15) !important;
        padding: 16px !important;
    }
    
    /* ── Spinner ── */
    .stSpinner > div {
        border-top-color: #60a5fa !important;
    }
    
    /* ── Form ── */
    [data-testid="stForm"] {
        background: linear-gradient(135deg, rgba(30,30,40,0.7), rgba(20,20,30,0.5));
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 24px;
    }
    
    /* ── Dataframe ── */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* ── Custom Scrollbar ── */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0a0a0c;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255,255,255,0.1);
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255,255,255,0.2);
    }
    
    /* ── Plotly chart container ── */
    .js-plotly-plot {
        border-radius: 12px;
        background: transparent !important;
    }
    
    /* ── Image ── */
    .stImage img {
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
    }
    
    /* ── Markdown within cards ── */
    .element-container p, .element-container li {
        color: #c4c4d0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ── App Routing ────────────────────────────────────────────────────────────

# Check authentication
if not st.session_state.auth_token:
    render_auth_page()
    st.stop()

# Render sidebar navigation
render_sidebar()

# Render the selected page
page = st.session_state.get("page", "Dashboard")

# Page routing
if page == "Dashboard":
    render_dashboard()
elif page == "Study Planner":
    # Study Planner has two sub-sections: Create Exam and Generate Plan
    planner_tabs = st.tabs(["📝 Configure Study Plan", "🧠 Generate Study Plan"])
    with planner_tabs[0]:
        render_create_exam()
    with planner_tabs[1]:
        render_generate_plan()
elif page == "Learning Desk":
    render_learning_desk()
elif page == "Practice Quiz":
    render_quiz()
elif page == "AI Tutor":
    render_tutor()
elif page == "Analytics Report":
    render_analytics()
else:
    render_dashboard()

