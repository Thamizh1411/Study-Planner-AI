"""AI Tutor chat component with ChatGPT-like interface."""

import streamlit as st
from components.utils import chat_tutor
from components.cards import SECTION_TITLE


def render_tutor():
    """Render the AI Tutor chat interface."""
    SECTION_TITLE("💬 AI Study Tutor", "Ask for a clear explanation, worked example, or revision help.")

    # Topic input
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(30,30,40,0.7), rgba(20,20,30,0.5));
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 16px 20px;
        margin-bottom: 20px;
    ">
        <label style="font-size:10px;font-weight:700;color:#9e9ea7;text-transform:uppercase;letter-spacing:0.08em;">Current Topic</label>
    </div>
    """, unsafe_allow_html=True)

    topic_title = st.text_input(
        "Topic Title",
        key="tutor_topic",
        placeholder="For example: Limits and Continuity",
        label_visibility="collapsed",
    )

    # Chat container
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(30,30,40,0.7), rgba(20,20,30,0.5));
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        overflow: hidden;
        margin-bottom: 20px;
    ">
    """, unsafe_allow_html=True)

    # Chat messages
    chat_container = st.container()
    with chat_container:
        messages = st.session_state.get("chat_history", [])
        if not messages:
            st.markdown("""
            <div style="padding: 32px 24px; text-align: center;">
                <div style="font-size: 40px; margin-bottom: 12px;">🤖</div>
                <p style="font-size: 14px; color: #6b6b7d;">
                    Hello! Tell me the topic and ask any study question. I can explain concepts, formulas, and mistakes step by step.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in messages:
                role = msg["role"]
                content = msg["content"]
                is_user = role == "user"

                if is_user:
                    st.markdown(f"""
                    <div style="display:flex;justify-content:flex-end;margin-bottom:12px;padding:0 16px;">
                        <div style="
                            max-width: 80%;
                            background: linear-gradient(135deg, #2563eb, #4f46e5);
                            border-radius: 14px 14px 4px 14px;
                            padding: 12px 16px;
                        ">
                            <p style="font-size:13px;color:#ffffff;margin:0;line-height:1.5;">{content}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="display:flex;gap:12px;margin-bottom:12px;padding:0 16px;">
                        <div style="
                            width:32px;height:32px;
                            background:linear-gradient(135deg, #2563eb, #4f46e5);
                            border-radius:50%;
                            display:flex;align-items:center;justify-content:center;
                            font-size:14px;flex-shrink:0;
                        ">🤖</div>
                        <div style="
                            max-width: 80%;
                            background: rgba(0,0,0,0.3);
                            border: 1px solid rgba(255,255,255,0.06);
                            border-radius: 14px 14px 14px 4px;
                            padding: 12px 16px;
                        ">
                            <p style="font-size:13px;color:#c4c4d0;margin:0;line-height:1.6;white-space:pre-wrap;">{content}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Input area
    col1, col2 = st.columns([5, 1])
    with col1:
        question = st.text_input(
            "Your question",
            key="tutor_question",
            placeholder="Ask a question about the selected topic...",
            label_visibility="collapsed",
        )
    with col2:
        if st.button("💬 Ask", type="primary", use_container_width=True):
            if not topic_title.strip() or not question.strip():
                st.error("Enter both a topic title and a question.")
            else:
                try:
                    with st.spinner("Tutor is thinking..."):
                        response = chat_tutor(topic_title, question, st.session_state.chat_history)

                    if "chat_history" not in st.session_state:
                        st.session_state.chat_history = []
                    st.session_state.chat_history.append({"role": "user", "content": question})
                    st.session_state.chat_history.append({"role": "assistant", "content": response["answer"]})
                    st.rerun()
                except Exception as exc:
                    st.error(f"Chat tutor failed: {exc}")

    # Clear chat button
    if st.session_state.get("chat_history"):
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

