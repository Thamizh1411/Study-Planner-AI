"""Plotly chart generation functions for analytics."""

import datetime
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def study_hours_chart(logs_data):
    """Generate a line chart of study hours over time."""
    if not logs_data:
        st.info("No study logs yet. Log study hours to see trends here.")
        return

    df_logs = pd.DataFrame(logs_data)
    df_logs["date"] = pd.to_datetime(df_logs["date"])
    df_logs = df_logs.sort_values("date")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_logs["date"],
        y=df_logs["study_hours"],
        mode="lines+markers",
        name="Study Hours",
        line=dict(color="#3b70ff", width=2.5),
        fill="tozeroy",
        fillcolor="rgba(59, 112, 255, 0.06)",
        marker=dict(size=6, color="#3b70ff", line=dict(width=1.5, color="#2563eb")),
    ))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Date",
        yaxis_title="Hours",
        height=300,
        margin=dict(l=10, r=10, t=10, b=10),
        hovermode="x unified",
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False),
        font=dict(color="#9e9ea7"),
    )
    st.plotly_chart(fig, use_container_width=True)


def quiz_scores_chart(logs_data):
    """Generate a bar chart of quiz scores over time."""
    if not logs_data:
        st.info("No quiz scores recorded yet. Complete quizzes to see scores here.")
        return

    df_scores = pd.DataFrame(logs_data)
    df_scores["date"] = pd.to_datetime(df_scores["date"])
    df_scores = df_scores.sort_values("date")
    df_scores = df_scores[df_scores["quiz_score"] > 0]

    if df_scores.empty:
        st.info("No quiz scores recorded yet. Complete quizzes to see scores here.")
        return

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_scores["date"],
        y=df_scores["quiz_score"],
        name="Quiz Score",
        marker_color="#a855f7",
        marker_line_color="#7c3aed",
        marker_line_width=1.5,
        opacity=0.85,
        hovertemplate="%{y:.1f}%<extra></extra>",
    ))
    fig.add_hline(
        y=70,
        line_dash="dash",
        line_color="#34d399",
        annotation_text="70% Target",
        annotation_font_color="#34d399",
        annotation_font_size=11,
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Date",
        yaxis_title="Score (%)",
        yaxis=dict(range=[0, 100], gridcolor="rgba(255,255,255,0.04)", zeroline=False),
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
        height=300,
        margin=dict(l=10, r=10, t=10, b=10),
        hovermode="x unified",
        font=dict(color="#9e9ea7"),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_heatmap(logs_data):
    """Render a GitHub-style study consistency heatmap."""
    st.markdown("### 🔥 Study Consistency Heatmap")
    st.caption("Visualize daily study hours for the last 4 weeks. Darker cells = more hours studied.")

    today_dt = datetime.date.today()
    heatmap_data = {}
    if logs_data:
        for log in logs_data:
            log_date_str = log["date"]
            if isinstance(log_date_str, str):
                log_date = datetime.datetime.strptime(log_date_str, "%Y-%m-%d").date()
            else:
                log_date = log_date_str
            heatmap_data[log_date.isoformat()] = log.get("study_hours", 0)

    dates_list = [(today_dt - datetime.timedelta(days=i)) for i in range(27, -1, -1)]
    weekdays_labels = ["Mon", "", "Wed", "", "Fri", "", "Sun"]

    matrix = [[0] * 4 for _ in range(7)]
    for i, d in enumerate(dates_list):
        col_idx = i // 7
        row_idx = d.weekday()
        iso = d.isoformat()
        val = heatmap_data.get(iso, 0)
        matrix[row_idx][col_idx] = val

    def heat_color(val):
        if val == 0:
            return "#1a1a2e"
        if val < 1.5:
            return "#1e3a5f"
        if val < 3.0:
            return "#2563eb"
        return "#60a5fa"

    heat_html = '<table style="border-collapse: collapse;">'
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

