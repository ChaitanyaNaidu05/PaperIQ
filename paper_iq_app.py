import streamlit as st
import re
import numpy as np
import json
import datetime
import time
import pdfplumber
import docx
from textblob import TextBlob
import plotly.graph_objects as go
from fpdf import FPDF
import heapq

import database
import auth
import styles
import pdf_processor
import text_analyzer

st.set_page_config(page_title="PaperIQ", layout="wide")

if "page" not in st.session_state:
    st.session_state["page"] = "login"
if "user" not in st.session_state:
    st.session_state["user"] = None
if "current_analysis" not in st.session_state:
    st.session_state["current_analysis"] = None

database.init_db()

st.markdown(styles.get_app_styles(), unsafe_allow_html=True)


def navigate_to(page):
    st.session_state["page"] = page
    st.rerun()


def handle_login(username, password):
    user = database.get_user_by_username(username)
    if user and auth.verify_password(user['password_hash'], user['salt'], password):
        st.session_state["user"] = user
        st.session_state["page"] = "dashboard"
        st.toast(f"Welcome back, {user['username']}!")
        time.sleep(1)
        st.rerun()
    else:
        st.error("Invalid username or password")


def handle_signup(username, email, password, confirm_password):
    if password != confirm_password:
        st.error("Passwords do not match")
        return
    if len(password) < 6:
        st.error("Password must be at least 6 characters")
        return
    salt = auth.generate_salt()
    password_hash = auth.hash_password(password, salt)
    if database.create_user(username, email, password_hash, salt):
        st.success("Account created successfully! Please login.")
        time.sleep(2)
        navigate_to("login")
    else:
        st.error("Username or Email already exists")


def handle_logout():
    st.session_state["user"] = None
    st.session_state["page"] = "login"
    st.session_state["current_analysis"] = None
    st.rerun()


def load_analysis_from_history(analysis_id):
    analysis = database.get_analysis_details(analysis_id)
    if analysis:
        st.session_state["current_analysis"] = {
            "filename": analysis["filename"],
            "sections": json.loads(analysis["sections_json"]),
            "keywords": json.loads(analysis["keywords_json"]),
            "timestamp": analysis["upload_time"],
            "results": None
        }


def render_login_page():
    st.markdown('<div class="main-header">PaperIQ</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.container(border=True):
            st.markdown("### Sign In")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login", type="primary"):
                handle_login(username, password)
            st.markdown("---")
            st.markdown("Don't have an account?")
            if st.button("Create Account"):
                navigate_to("signup")


def render_signup_page():
    st.markdown('<div class="main-header">PaperIQ</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.container(border=True):
            st.markdown("### Create Account")
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            if st.button("Sign Up", type="primary"):
                handle_signup(username, email, password, confirm_password)
            st.markdown("---")
            if st.button("Back to Login"):
                navigate_to("login")


# ═══════════════════════════════════════════════════════════
# HELPER RENDERERS
# ═══════════════════════════════════════════════════════════

def _render_stat_card(label, value):
    """Render a single styled stat card."""
    st.markdown(
        f'<div class="stat-card">'
        f'<div class="stat-label">{label}</div>'
        f'<div class="stat-value">{value}</div>'
        f'</div>',
        unsafe_allow_html=True
    )


def _render_keyword_chips(keywords):
    """Render keyword chips from list of (keyword, score) tuples."""
    if not keywords:
        return
    chips_html = '<div class="keywords-container"><strong>Top Keywords</strong><br/>'
    for kw, score in keywords[:12]:
        chips_html += f'<span class="keyword-chip">{kw} <span class="score-pill">{score:.3f}</span></span>'
    chips_html += '</div>'
    st.markdown(chips_html, unsafe_allow_html=True)


def _render_structural_checklist(found, missing):
    """Render structural completeness as colored tags."""
    html = '<div style="margin: 0.5rem 0;">'
    for s in found:
        html += f'<span class="struct-found">✓ {s}</span>'
    for s in missing:
        html += f'<span class="struct-missing">✗ {s}</span>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════

def render_dashboard():
    user = st.session_state["user"]

    # ── Sidebar ──
    with st.sidebar:
        st.markdown(f"### Hello, {user['username']}")
        if st.button("Logout"):
            handle_logout()
        st.markdown("---")
        st.markdown("### Analysis History")
        if st.button("New Analysis", type="primary"):
            st.session_state["current_analysis"] = None
            st.rerun()
        history = database.get_user_history(user['id'])
        if history:
            for item in history:
                date_str = item['upload_time'].split(' ')[0]
                label = f"{item['filename']} ({date_str})"
                if st.button(label, key=f"history_{item['id']}"):
                    load_analysis_from_history(item['id'])
                    st.rerun()
        else:
            st.info("No history yet.")

    st.markdown('<div class="main-header">PaperIQ</div>', unsafe_allow_html=True)

    current_analysis = st.session_state.get("current_analysis")

    # ═════════════════════════════════════════════════════
    # RESULTS VIEW
    # ═════════════════════════════════════════════════════
    if current_analysis and current_analysis.get("results"):
        results = current_analysis["results"]
        filename = current_analysis["filename"]
        scores = results["scores"]

        # ── Top metric row ──
        metric_cols = st.columns(6)
        top_metrics = ["Composite", "Language", "Coherence", "Reasoning", "Readability", "Sophistication"]
        for col, metric in zip(metric_cols, top_metrics):
            val = scores.get(metric, 0)
            col.metric(metric, f"{val}/100")

        # ── Second row: new metrics ──
        metric_cols2 = st.columns(5)
        new_metrics = ["Citation Density", "Technical Depth", "Novelty Signal",
                        "Structural Completeness", "Vocabulary Richness"]
        for col, metric in zip(metric_cols2, new_metrics):
            val = scores.get(metric, 0)
            col.metric(metric, f"{val}/100")

        # ── Domain badge + download ──
        col_domain, col_download = st.columns([3, 1])
        with col_domain:
            domain = results.get("domain", "General")
            st.markdown(f'<span class="domain-badge">📚 {domain}</span>', unsafe_allow_html=True)
        with col_download:
            pdf_bytes = text_analyzer.create_pdf_report(filename, results)
            st.download_button("📄 Download Report", pdf_bytes, "report.pdf", "application/pdf")

        # ── Document Summary ──
        doc_summary = results.get("document_summary", "")
        if doc_summary:
            st.markdown("#### 📝 Document Summary")
            st.markdown(f'<div class="summary-box">{doc_summary}</div>', unsafe_allow_html=True)

        # ── Keywords ──
        keywords = results.get("keywords", [])
        _render_keyword_chips(keywords)

        # ── Tabs ──
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Radar & Scores", "📈 Statistics", "🧩 Structure", "⚠️ Issues", "📋 Sections"
        ])

        # ── Tab 1: Radar chart + sentiment + complexity pie ──
        with tab1:
            col_radar, col_right = st.columns([3, 2])
            with col_radar:
                radar_fig = text_analyzer.build_radar_chart(scores)
                st.plotly_chart(radar_fig, use_container_width=True)
            with col_right:
                st.markdown("##### Sentiment")
                gauge_fig = text_analyzer.build_sentiment_gauge(results["sentiment"])
                st.plotly_chart(gauge_fig, use_container_width=True)

                st.markdown("##### Sentence Complexity")
                complexity = results.get("sentence_complexity", {})
                if complexity:
                    pie_fig = text_analyzer.build_complexity_pie(complexity)
                    st.plotly_chart(pie_fig, use_container_width=True)

        # ── Tab 2: Statistics as cards + bar chart + domain chart ──
        with tab2:
            stats = results["stats"]

            # Stat cards in columns
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                _render_stat_card("Word Count", f"{stats['word_count']:,}")
                _render_stat_card("Avg Word Length", f"{stats['avg_word_len']} chars")
            with c2:
                _render_stat_card("Sentence Count", f"{stats['sentence_count']:,}")
                _render_stat_card("Avg Sentence Length", f"{stats['avg_sentence_len']} words")
            with c3:
                _render_stat_card("Total Citations", str(stats.get('total_citations', 0)))
                _render_stat_card("Citation Density", f"{stats.get('citation_density_per_1k', 0)} / 1k words")
            with c4:
                _render_stat_card("Complex Word Ratio", f"{stats.get('complex_word_ratio', 0):.0%}")
                _render_stat_card("Type-Token Ratio", f"{stats.get('type_token_ratio', 0):.4f}")

            st.markdown("---")
            col_bar, col_domain_chart = st.columns([3, 2])
            with col_bar:
                st.markdown("##### Document Metrics")
                bar_fig = text_analyzer.build_bar_chart(stats)
                st.plotly_chart(bar_fig, use_container_width=True)
            with col_domain_chart:
                st.markdown("##### Domain Classification")
                domain_scores = results.get("domain_scores", {})
                if domain_scores:
                    domain_fig = text_analyzer.build_domain_bar(domain_scores)
                    st.plotly_chart(domain_fig, use_container_width=True)

        # ── Tab 3: Structural completeness ──
        with tab3:
            structural_score = scores.get("Structural Completeness", 0)
            st.metric("Structural Completeness Score", f"{structural_score}/100")
            st.markdown("##### Detected Sections")
            found = results.get("structural_found", [])
            missing = results.get("structural_missing", [])
            _render_structural_checklist(found, missing)

            st.markdown("---")
            st.markdown("##### Novelty Indicators")
            novelty_count = stats.get("novelty_phrases_found", 0)
            st.info(f"**{novelty_count}** novelty/contribution phrases detected "
                    f"(e.g. 'we propose', 'novel', 'outperforms')")

            st.markdown("##### Reasoning & Transitions")
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Transition Words", stats.get("transition_words_found", 0))
            with col_b:
                st.metric("Reasoning Indicators", stats.get("reasoning_indicators", 0))

        # ── Tab 4: Issues (overly long sentences) ──
        with tab4:
            issues = results.get("issues", [])
            if issues:
                st.warning(f"**{len(issues)}** sentences exceed 30 words:")
                for i, sentence in enumerate(issues, 1):
                    st.warning(f"**{i}.** {sentence}")
            else:
                st.success("No overly long sentences detected.")

        # ── Tab 5: Extracted sections with summaries ──
        with tab5:
            sections = current_analysis.get("sections", {})
            if sections:
                for section_name, content in sections.items():
                    if isinstance(content, dict):
                        content = content.get("content", "")
                    word_count = len(content.split())
                    with st.expander(f"📄 {section_name} ({word_count} words)"):
                        summary = text_analyzer.extractive_summarize(content)
                        if summary:
                            st.markdown(f'<div class="summary-box"><strong>Summary:</strong> {summary}</div>',
                                        unsafe_allow_html=True)
                        st.text_area(f"Full content – {section_name}", content, height=200,
                                     key=f"section_{section_name}")

    # ═════════════════════════════════════════════════════
    # SAVED ANALYSIS (no results, just sections from history)
    # ═════════════════════════════════════════════════════
    elif current_analysis and not current_analysis.get("results"):
        st.info(f"Viewing saved analysis for: **{current_analysis['filename']}**")
        sections = current_analysis.get("sections", {})
        if sections:
            for section_name, content in sections.items():
                if isinstance(content, dict):
                    content = content.get("content", "")
                with st.expander(f"📄 {section_name} ({len(content.split())} words)"):
                    summary = text_analyzer.extractive_summarize(content)
                    if summary:
                        st.markdown(f'<div class="summary-box"><strong>Summary:</strong> {summary}</div>',
                                    unsafe_allow_html=True)
                    st.text_area(f"Content – {section_name}", content, height=200,
                                 key=f"hist_section_{section_name}")

    # ═════════════════════════════════════════════════════
    # UPLOAD VIEW
    # ═════════════════════════════════════════════════════
    else:
        st.markdown("#### Upload a research paper to analyze")
        uploaded_file = st.file_uploader("Upload Document", type=["pdf", "docx", "txt"])

        if uploaded_file and st.button("Analyze Document", type="primary"):
            with st.spinner("Analyzing document... this may take a moment."):
                if uploaded_file.name.endswith(".pdf"):
                    text = pdf_processor.extract_text_from_pdf(uploaded_file)
                elif uploaded_file.name.endswith(".docx"):
                    text = pdf_processor.extract_text_from_docx(uploaded_file)
                else:
                    text = uploaded_file.getvalue().decode("utf-8")

                cleaned_text = pdf_processor.clean_text(text)
                results = text_analyzer.analyze_full_document(cleaned_text)

                if results is None:
                    st.error("Could not extract meaningful text from this document.")
                else:
                    sections = text_analyzer.extract_sections(cleaned_text)
                    db_sections = {k: {"content": v, "keywords": []} for k, v in sections.items()}

                    database.save_analysis(
                        user_id=user['id'],
                        filename=uploaded_file.name,
                        sections_count=len(sections),
                        keywords=list(results["scores"].keys()),
                        sections_data=db_sections
                    )

                    st.session_state["current_analysis"] = {
                        "filename": uploaded_file.name,
                        "sections": db_sections,
                        "results": results,
                        "timestamp": str(datetime.datetime.now())
                    }

                    st.toast("Analysis complete!")
                    st.rerun()


if st.session_state["page"] == "login":
    render_login_page()
elif st.session_state["page"] == "signup":
    render_signup_page()
elif st.session_state["page"] == "dashboard":
    render_dashboard()
