"""Learning Desk component with AI Notes, Flashcards, OCR, and PDF Chat (RAG)."""

import random
import streamlit as st
from components.utils import (
    fetch_exams, fetch_exam_topics, fetch_topic_notes,
    fetch_topic_flashcards, review_flashcard, ocr_upload,
    pdf_upload, pdf_query
)
from components.cards import SECTION_TITLE, BADGE


def render_learning_desk():
    """Render the complete Learning Desk page."""
    SECTION_TITLE("📖 Learning Desk", "Review summaries, practice spaced recall cards, and search document resources.")

    try:
        exams = fetch_exams()
    except Exception as e:
        st.error(f"⚠️ Cannot connect to backend: {e}")
        st.info("Make sure the FastAPI backend is running on port 8000.")
        return

    if not exams:
        st.warning("⚠️ No exams found. Create an exam on the Dashboard first.")
        return

    exam_options = {f"{ex['name']} ({ex.get('exam_date', 'N/A')})": ex['id'] for ex in exams}
    selected_label = st.selectbox("Choose Exam", list(exam_options.keys()), key="ld_exam_select")
    selected_exam_id = exam_options[selected_label]

    # Fetch topics if needed
    ld_topics_key = f"ld_topics_{selected_exam_id}"
    if ld_topics_key not in st.session_state or st.session_state.get("ld_last_exam_id") != selected_exam_id:
        with st.spinner("Loading topics..."):
            try:
                st.session_state[ld_topics_key] = fetch_exam_topics(selected_exam_id)
                st.session_state.ld_last_exam_id = selected_exam_id
            except Exception as e:
                st.error(f"Failed to load topics: {e}")
                st.session_state[ld_topics_key] = []
        st.rerun()

    topics = st.session_state[ld_topics_key]
    if not topics:
        st.info("📭 No topics available. Go to **Dashboard** and generate a Study Plan first.")
        return

    # Topic selector
    topic_names = {t["title"]: t for t in topics}
    selected_topic_name = st.selectbox("Select Topic", list(topic_names.keys()), key="ld_topic_select")
    selected_topic = topic_names[selected_topic_name]

    # Tabs as styled buttons
    tab_cols = st.columns(4)
    tab_labels = ["📝 AI Notes", "🃏 Flashcards", "📷 OCR Scan", "📄 PDF Chat"]
    active_tab = st.session_state.get("ld_active_tab", "📝 AI Notes")

    for i, (col, label) in enumerate(zip(tab_cols, tab_labels)):
        with col:
            is_active = active_tab == label
            btn_type = "primary" if is_active else "secondary"
            if st.button(label, key=f"ld_tab_{i}", type=btn_type, use_container_width=True):
                st.session_state.ld_active_tab = label
                st.rerun()

    if active_tab == "📝 AI Notes":
        _render_notes(selected_topic)
    elif active_tab == "🃏 Flashcards":
        _render_flashcards(selected_topic)
    elif active_tab == "📷 OCR Scan":
        _render_ocr(selected_topic)
    elif active_tab == "📄 PDF Chat":
        _render_pdf_rag()


def _render_notes(topic):
    """Render AI Notes tab."""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(30,30,40,0.7), rgba(20,20,30,0.5));
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 24px;
    ">
        <div style="display:flex;justify-content:space-between;align-items:center;padding-bottom:16px;border-bottom:1px solid rgba(255,255,255,0.06);margin-bottom:16px;">
            <div>
                <h3 style="font-size:18px;font-weight:700;color:#ffffff;margin:0;">{topic['title']}</h3>
                <span style="font-size:11px;color:#6b6b7d;">{topic.get('subject_name', '')}</span>
            </div>
            <div style="display:flex;gap:8px;">{BADGE("Markdown", "#3b70ff")}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("📖 Load AI Notes", type="primary", key="load_notes_btn"):
        with st.spinner("Fetching AI-generated notes..."):
            try:
                content = fetch_topic_notes(topic["id"])
                st.session_state.notes_content = content
                if content and len(content) < 50:
                    st.info("Notes are minimal. Generate a Study Plan for comprehensive AI notes.")
            except Exception as e:
                st.error(f"Failed to load notes: {e}")
                st.session_state.notes_content = ""
        st.rerun()

    if st.session_state.get("notes_content"):
        st.markdown(st.session_state.notes_content)
    else:
        st.info("💡 Click **'Load AI Notes'** to view AI-generated study notes for this topic.")


def _render_flashcards(topic):
    """Render Flashcards tab with SM-2 review."""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(30,30,40,0.7), rgba(20,20,30,0.5));
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 24px;
    ">
        <div style="display:flex;justify-content:space-between;align-items:center;padding-bottom:16px;border-bottom:1px solid rgba(255,255,255,0.06);margin-bottom:16px;">
            <div>
                <h3 style="font-size:18px;font-weight:700;color:#ffffff;margin:0;">{topic['title']}</h3>
                <span style="font-size:11px;color:#6b6b7d;">SM-2 Spaced Repetition</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔄 Load Flashcards", type="primary", key="load_flashcards_btn"):
        with st.spinner("Loading flashcards..."):
            try:
                cards = fetch_topic_flashcards(topic["id"])
                st.session_state.flashcards = cards if cards else []
                st.session_state.flipped_card_id = None
                st.session_state.fc_idx = 0
            except Exception as e:
                st.error(f"Failed to load flashcards: {e}")
                st.session_state.flashcards = []
        st.rerun()

    cards = st.session_state.get("flashcards", [])
    if not cards:
        st.info("💡 No flashcards for this topic. Click **'Load Flashcards'** above, or generate a Study Plan first.")
        return

    if "fc_idx" not in st.session_state:
        st.session_state.fc_idx = 0

    current_idx = st.session_state.fc_idx
    if current_idx >= len(cards):
        current_idx = 0
        st.session_state.fc_idx = 0

    card = cards[current_idx]
    is_flipped = st.session_state.get("flipped_card_id") == card.get("id")

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(20,20,30,0.8), rgba(15,15,25,0.6));
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 32px; min-height: 160px;
        text-align: center; cursor: pointer;
        margin: 16px 0;
        display:flex;flex-direction:column;justify-content:center;
    ">
        <p style="font-size:10px;font-weight:700;color:#6b6b7d;text-transform:uppercase;letter-spacing:0.08em;margin:0 0 12px;">
            {'Answer' if is_flipped else 'Question'}
        </p>
        <p style="font-size:16px;font-weight:600;color:#e4e4ec;margin:0;line-height:1.5;">
            {card.get('answer' if is_flipped else 'question', '(No content)')}
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("👆 Click to Flip", use_container_width=True, key="flip_card_btn"):
        st.session_state.flipped_card_id = None if is_flipped else card.get("id")
        st.rerun()

    nav_cols = st.columns([1, 1, 1, 1, 1])
    with nav_cols[0]:
        if st.button("◀ Prev", use_container_width=True):
            st.session_state.fc_idx = (current_idx - 1) % len(cards)
            st.session_state.flipped_card_id = None
            st.rerun()
    with nav_cols[1]:
        st.markdown(f"<p style='text-align:center;font-size:12px;color:#6b6b7d;padding-top:8px;'>{current_idx+1}/{len(cards)}</p>", unsafe_allow_html=True)
    with nav_cols[2]:
        if st.button("Next ▶", use_container_width=True):
            st.session_state.fc_idx = (current_idx + 1) % len(cards)
            st.session_state.flipped_card_id = None
            st.rerun()
    with nav_cols[3]:
        if st.button("🔀 Shuffle", use_container_width=True):
            random.shuffle(cards)
            st.session_state.flashcards = cards
            st.session_state.fc_idx = 0
            st.session_state.flipped_card_id = None
            st.rerun()

    if is_flipped:
        st.markdown('<p style="font-size:10px;font-weight:700;color:#9e9ea7;text-transform:uppercase;letter-spacing:0.08em;margin:16px 0 8px;">Rate Recall Quality (SM-2)</p>', unsafe_allow_html=True)
        rating_cols = st.columns(5)
        labels_map = {1: "❌", 2: "🤔", 3: "👍", 4: "⭐", 5: "🏆"}
        for val in [1, 2, 3, 4, 5]:
            with rating_cols[val - 1]:
                if st.button(f"{labels_map[val]}", key=f"rate_{card.get('id')}_{val}", use_container_width=True):
                    try:
                        result = review_flashcard(card.get("id"), val)
                        if result:
                            st.success(f"Rated {val}/5 - Spaced interval updated!")
                            st.rerun()
                        else:
                            st.error("Backend rating failed.")
                    except Exception as e:
                        st.error(f"Rating failed: {e}")


def _render_ocr(topic):
    """Render OCR Scan tab."""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(30,30,40,0.7), rgba(20,20,30,0.5));
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
    ">
        <div style="font-size:48px;margin-bottom:12px;">📷</div>
        <h4 style="font-size:16px;font-weight:700;color:#ffffff;margin:0 0 8px;">OCR Upload Tool</h4>
        <p style="font-size:12px;color:#6b6b7d;max-width:400px;margin:0 auto 20px;">
            Upload photos of handwritten pages or textbook sheets to convert them into markdown summaries and quizzes.
        </p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg", "webp"], key="ocr_uploader")
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Image", width=300)
        if st.button("🔍 Process Image OCR", type="primary", use_container_width=True):
            with st.spinner("Scanning contents with AI..."):
                try:
                    result = ocr_upload(uploaded_file, topic["id"])
                    if result:
                        st.session_state.ocr_result = result
                        st.success("✅ OCR completed!")
                        st.rerun()
                    else:
                        st.error("OCR processing returned no result.")
                except Exception as e:
                    st.error(f"OCR failed: {e}")

    ocr_result = st.session_state.get("ocr_result")
    if ocr_result:
        with st.expander("📝 Extracted Text", expanded=True):
            st.markdown(ocr_result.get("extracted_text", "No text extracted."))
        if ocr_result.get("quiz"):
            st.markdown("### 📋 Generated Quiz")
            for idx, q in enumerate(ocr_result["quiz"]):
                st.markdown(f"**Q{idx+1}:** {q['question_text']}")
                st.markdown(f"*Answer:* {q.get('correct_answer', 'N/A')}")


def _render_pdf_rag():
    """Render PDF Chat (RAG) tab."""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(30,30,40,0.7), rgba(20,20,30,0.5));
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
    ">
        <h4 style="font-size:14px;font-weight:700;color:#ffffff;margin:0 0 4px;">📄 RAG Document Indexer</h4>
        <p style="font-size:12px;color:#6b6b7d;margin:0;">Upload course PDFs, slide decks, or papers. The system indexes them for search queries.</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"], key="rag_pdf_uploader")
    if uploaded_pdf:
        if st.button("📤 Index PDF", type="primary", use_container_width=True):
            with st.spinner("Indexing PDF chunks..."):
                try:
                    result = pdf_upload(uploaded_pdf)
                    if result:
                        st.success(f"✅ {result.get('message', 'PDF indexed successfully!')}")
                except Exception as e:
                    st.error(f"PDF upload failed: {e}")

    st.markdown("### 🔍 Ask Questions")
    query = st.text_input("Search your notes", key="rag_query", placeholder="E.g., Explain TCP congestion control...")
    if st.button("🔎 Search", type="primary", use_container_width=True):
        if query.strip():
            with st.spinner("Searching..."):
                try:
                    result = pdf_query(query)
                    st.session_state.rag_answer = result.get("answer", "")
                    st.session_state.rag_sources = result.get("sources", [])
                except Exception as e:
                    st.error(f"Query failed: {e}")
            st.rerun()

    if st.session_state.get("rag_answer"):
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(99,102,241,0.05),rgba(139,92,246,0.05));border:1px solid rgba(99,102,241,0.1);border-radius:16px;padding:20px;margin-top:16px;">
            <p style="font-size:13px;color:#c4c4d0;line-height:1.6;white-space:pre-wrap;">{st.session_state.rag_answer}</p>
        </div>
        """, unsafe_allow_html=True)
        sources = st.session_state.get("rag_sources", [])
        if sources:
            st.markdown("**Sources:**")
            for src in sources:
                st.markdown(f"- `{src}`")

