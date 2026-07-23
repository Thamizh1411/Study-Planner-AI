"""Reusable card components for the dark theme UI."""

import streamlit as st


def STAT_CARD(title, value, subtitle, icon_emoji, accent_color="#3b70ff"):
    """Render a stat card with icon, value, and subtitle."""
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, rgba(30,30,40,0.8), rgba(20,20,30,0.6));
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 16px;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: all 0.3s ease;
        ">
            <div>
                <div style="font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #9e9ea7; margin-bottom: 6px;">{title}</div>
                <div style="font-size: 28px; font-weight: 800; color: #ffffff; line-height: 1.2;">{value}</div>
                <div style="font-size: 11px; color: #6b6b7d; margin-top: 4px;">{subtitle}</div>
            </div>
            <div style="
                background: {accent_color}15;
                border: 1px solid {accent_color}30;
                border-radius: 14px;
                padding: 14px;
                font-size: 26px;
                line-height: 1;
            ">{icon_emoji}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def GLASS_CARD(content, padding="20px", extra_css=""):
    """Wrapper for a glassmorphism card - call with inner content already as HTML."""
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, rgba(30,30,40,0.7), rgba(20,20,30,0.5));
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 16px;
            padding: {padding};
            transition: all 0.3s ease;
            {extra_css}
        ">
            {content}
        </div>
        """,
        unsafe_allow_html=True,
    )


def SECTION_TITLE(title, subtitle=""):
    """Render a section title with optional subtitle."""
    st.markdown(
        f"""
        <div style="margin-bottom: 16px;">
            <h2 style="font-size: 22px; font-weight: 800; color: #ffffff; margin: 0; letter-spacing: -0.02em;">{title}</h2>
            {f'<p style="font-size: 13px; color: #6b6b7d; margin: 4px 0 0;">{subtitle}</p>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def BADGE(text, color="#3b70ff", bg_opacity="15"):
    """Render a small badge/tag."""
    return f'<span style="font-size: 10px; font-weight: 700; color: {color}; background: {color}{bg_opacity}; padding: 3px 10px; border-radius: 20px; border: 1px solid {color}30; text-transform: uppercase; letter-spacing: 0.05em;">{text}</span>'


def BUTTON_HTML(text, primary=True, full_width=False):
    """Generate HTML for a styled button."""
    if primary:
        return f"""
        <div style="
            display: inline-flex; align-items: center; gap: 8px;
            background: linear-gradient(135deg, #2563eb, #4f46e5);
            color: white; font-weight: 700; font-size: 13px;
            padding: 10px 20px; border-radius: 12px;
            border: none; cursor: pointer;
            box-shadow: 0 4px 15px rgba(59,112,255,0.15);
            transition: all 0.2s ease;
            {('width: 100%; justify-content: center;' if full_width else '')}
        ">{text}</div>"""
    return f"""
    <div style="
        display: inline-flex; align-items: center; gap: 8px;
        background: rgba(30,30,40,0.8); color: #c4c4d0; font-weight: 600; font-size: 13px;
        padding: 10px 20px; border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.08); cursor: pointer;
        transition: all 0.2s ease;
        {('width: 100%; justify-content: center;' if full_width else '')}
    ">{text}</div>"""

