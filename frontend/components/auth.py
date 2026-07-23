"""Authentication components (Login / Signup)."""

import httpx
import streamlit as st
from components.utils import login, signup


def render_auth_page():
    """Render the full-page login/signup interface matching React dark theme."""
    st.markdown("""
        <style>
        .auth-container {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 20px;
        }
        .auth-card {
            background: linear-gradient(135deg, rgba(30,30,40,0.9), rgba(20,20,30,0.8));
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 24px;
            padding: 40px;
            width: 100%;
            max-width: 420px;
            box-shadow: 0 25px 60px rgba(0,0,0,0.5);
        }
        .auth-logo {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 32px;
        }
        .auth-logo-icon {
            background: linear-gradient(135deg, #2563eb, #4f46e5);
            border-radius: 12px;
            padding: 10px;
            font-size: 22px;
            box-shadow: 0 4px 15px rgba(59,112,255,0.2);
        }
        .auth-logo-text {
            font-size: 22px;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: -0.02em;
        }
        .auth-logo-text span {
            color: #60a5fa;
        }
        .auth-title {
            font-size: 26px;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 4px;
        }
        .auth-subtitle {
            font-size: 13px;
            color: #6b6b7d;
            margin-bottom: 28px;
        }
        .auth-divider {
            border-top: 1px solid rgba(255,255,255,0.06);
            margin: 24px 0;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="auth-container">
        <div class="auth-card">
            <div class="auth-logo">
                <div class="auth-logo-icon">📚</div>
                <div class="auth-logo-text">StudyPlanner <span>AI</span></div>
            </div>
        """, unsafe_allow_html=True)

        auth_mode = st.radio(
            "Authentication",
            ["Login", "Sign Up"],
            horizontal=True,
            label_visibility="collapsed",
            key="auth_mode_radio",
        )

        if auth_mode == "Login":
            st.markdown('<div class="auth-title">Welcome Back</div>', unsafe_allow_html=True)
            st.markdown('<div class="auth-subtitle">Sign in to continue your study journey</div>', unsafe_allow_html=True)

            email = st.text_input("Email", key="login_email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")

            if st.button("🔑 Sign In", type="primary", use_container_width=True):
                if not email.strip() or not password:
                    st.error("Please enter both email and password.")
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
            st.markdown('<div class="auth-title">Create Account</div>', unsafe_allow_html=True)
            st.markdown('<div class="auth-subtitle">Start your AI-powered study plan</div>', unsafe_allow_html=True)

            name = st.text_input("Full Name", key="signup_name", placeholder="John Doe")
            email = st.text_input("Email", key="signup_email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="signup_password", placeholder="Create a strong password")

            if st.button("📝 Create Account", type="primary", use_container_width=True):
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

        st.markdown('<div class="auth-divider"></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align:center;font-size:11px;color:#4a4a5a;">API: localhost:8000</div>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

