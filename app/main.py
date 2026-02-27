import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import json
import datetime
import time
import logging
import plotly.graph_objects as go

from core import database, auth, pdf_processor, text_analyzer
import core.multidoc_analyzer as multidoc_analyzer
import core.arxiv_client as arxiv_client
from app import styles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="PaperIQ", layout="wide")

# PHASE 2: Health Check & Environment Config
if st.query_params.get("health") == "1":
    st.write("OK")
    st.stop()

SESSION_FILE = ".session.json"


def save_session(user_id):
    try:
        with open(SESSION_FILE, "w") as f:
            json.dump({"user_id": user_id, "timestamp": str(datetime.datetime.now())}, f)
    except Exception as e:
        logger.error(f"Error saving session: {e}")


def load_session():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as f:
                data = json.load(f)
                return data.get("user_id")
        except Exception as e:
            logger.error(f"Error loading session: {e}")
    return None


def clear_session():
    if os.path.exists(SESSION_FILE):
        try:
            os.remove(SESSION_FILE)
        except Exception as e:
            logger.error(f"Error clearing session: {e}")


# Initialize session state from file if not already set
if "user" not in st.session_state or st.session_state["user"] is None:
    cached_user_id = load_session()
    if cached_user_id:
        user = database.get_user_by_id(cached_user_id)
        if user:
            st.session_state["user"] = user
            st.session_state["page"] = "dashboard"
        else:
            # Cached user no longer exists, clear the invalid session
            clear_session()

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
    if user and auth.verify_password(user['password_hash'], user['salt'] if user['salt'] else None, password):
        st.session_state["user"] = user
        st.session_state["page"] = "dashboard"
        save_session(user['id'])
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
        st.success("Account created successfully. Please login.")
        time.sleep(2)
        navigate_to("login")
    else:
        st.error("Username or Email already exists")


def handle_logout():
    st.session_state["user"] = None
    st.session_state["page"] = "login"
    st.session_state["current_analysis"] = None
    clear_session()
    st.rerun()


def load_analysis_from_history(analysis_id):
    try:
        analysis = database.get_analysis_details(analysis_id)
        if analysis:
            sections_data = {}
            results_data = None
            keywords_data = []

            try:
                if analysis["sections_json"]:
                    sections_data = json.loads(analysis["sections_json"])
                if analysis["results_json"]:
                    results_data = json.loads(analysis["results_json"])
                if analysis["keywords_json"]:
                    keywords_data = json.loads(analysis["keywords_json"])
            except json.JSONDecodeError as e:
                logger.error(f"JSON corruption in analysis {analysis_id}: {e}")
                st.error("This analysis record is corrupted and cannot be loaded.")
                return

            st.session_state["current_analysis"] = {
                "id": analysis["id"],
                "filename": analysis["filename"],
                "sections": sections_data,
                "keywords": keywords_data,
                "timestamp": analysis["upload_time"],
                "results": results_data
            }
            logger.info(f"Loaded: {analysis['filename']} (ID: {analysis_id})")
        else:
            st.error("Analysis not found in database.")
    except Exception as e:
        logger.error(f"Error loading history: {e}")
        st.error(f"Could not load analysis: {str(e)}")


def _render_stat_card(label, value):
    st.markdown(
        f'<div class="stat-card">'
        f'<div class="stat-label">{label}</div>'
        f'<div class="stat-value">{value}</div>'
        f'</div>',
        unsafe_allow_html=True
    )


def _render_keyword_chips(keywords):
    if not keywords:
        return
    chips_html = '<div class="keywords-container"><strong>Top Keywords</strong><br/>'
    for kw, score in keywords[:12]:
        chips_html += f'<span class="keyword-chip">{kw} <span class="score-pill">{score:.3f}</span></span>'
    chips_html += '</div>'
    st.markdown(chips_html, unsafe_allow_html=True)


def _render_structural_checklist(found, missing):
    html = '<div style="margin: 0.5rem 0;">'
    for s in found:
        html += f'<span class="struct-found">{s}</span>'
    for s in missing:
        html += f'<span class="struct-missing">{s}</span>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


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


def render_dashboard():
    user = st.session_state["user"]

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

        st.markdown("---")
        st.markdown("### Tools")
        if st.button("Compare Documents"):
            navigate_to("compare")
        if st.button("Fetch from arXiv"):
            navigate_to("arxiv")
        if st.button("Trends Dashboard"):
            navigate_to("trends")

    st.markdown('<div class="main-header">PaperIQ</div>', unsafe_allow_html=True)

    current_analysis = st.session_state.get("current_analysis")

    if current_analysis and current_analysis.get("results"):
        results = current_analysis["results"]
        filename = current_analysis["filename"]
        scores = results["scores"]

        metric_cols = st.columns(6)
        top_metrics = ["Composite", "Language", "Coherence", "Reasoning", "Readability", "Sophistication"]
        for col, metric in zip(metric_cols, top_metrics):
            val = scores.get(metric, 0)
            col.metric(metric, f"{val}/100")

        metric_cols2 = st.columns(5)
        new_metrics = ["Citation Density", "Technical Depth", "Novelty Signal",
                        "Structural Completeness", "Vocabulary Richness"]
        for col, metric in zip(metric_cols2, new_metrics):
            val = scores.get(metric, 0)
            col.metric(metric, f"{val}/100")

        classification = results.get("classification", {})
        col_type, col_meth, col_align = st.columns(3)
        with col_type:
            st.markdown(f"**Paper Type:** {classification.get('type', 'N/A')}")
        with col_meth:
            st.markdown(f"**Methodology:** {classification.get('methodology', 'N/A')}")
        with col_align:
            alignment = results.get("alignment", (0, "N/A"))
            st.markdown(f"**Story Alignment:** {alignment[0]}% ({alignment[1]})")

        col_domain, col_pdf, col_json, col_csv = st.columns([3, 1, 1, 1])
        with col_domain:
            domain = results.get("domain", "General")
            st.markdown(f'<span class="domain-badge">{domain}</span>', unsafe_allow_html=True)
        with col_pdf:
            section_scores = results.get("section_scores", [])
            pdf_bytes = text_analyzer.create_pdf_report(filename, results, section_scores)
            st.download_button("PDF", pdf_bytes, f"{filename}_report.pdf", "application/pdf")
        with col_json:
            json_bytes = text_analyzer.create_json_export(results)
            st.download_button("JSON", json_bytes, f"{filename}_data.json", "application/json")
        with col_csv:
            csv_bytes = text_analyzer.create_csv_export(results)
            st.download_button("CSV", csv_bytes, f"{filename}_data.csv", "text/csv")

        doc_summary = results.get("document_summary", "")
        if doc_summary:
            st.markdown("#### Document Summary")
            st.markdown(f'<div class="summary-box">{doc_summary}</div>', unsafe_allow_html=True)

        keywords = results.get("keywords", [])
        _render_keyword_chips(keywords)

        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
            "Radar & Scores", "Statistics", "Structure", "Section Analysis",
            "Entities", "Issues", "Sections", "Advanced Analysis", "Bibliography"
        ])

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

        with tab2:
            stats = results["stats"]
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

            elements = results.get("elements", {})
            e1, e2, e3 = st.columns(3)
            with e1:
                _render_stat_card("Figures", str(elements.get("figures", 0)))
            with e2:
                _render_stat_card("Tables", str(elements.get("tables", 0)))
            with e3:
                _render_stat_card("Equations", str(elements.get("equations", 0)))
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

        with tab4:
            st.markdown("##### Section-wise Scores")
            section_scores = results.get("section_scores", [])
            if section_scores:
                for sec in section_scores:
                    sec_name = sec.get("section", "Unknown")
                    sec_score = sec.get("score", 0)
                    sec_words = sec.get("word_count", 0)
                    sec_clarity = sec.get("clarity_score", 0)
                    sec_readability = sec.get("readability", 0)
                    bar_width = min(100, sec_score)
                    st.markdown(f"""
                    <div class="section-score-card">
                        <div class="section-score-header">
                            <span class="section-score-name">{sec_name}</span>
                            <span class="section-score-value">{sec_score:.1f}/100</span>
                        </div>
                        <div class="section-score-bar">
                            <div class="section-score-fill" style="width: {bar_width}%"></div>
                        </div>
                        <div style="margin-top: 0.5rem; font-size: 0.85rem; color: #64748B;">
                            Words: {sec_words} | Clarity: {sec_clarity:.1f} | Readability: {sec_readability:.1f}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Section-wise analysis not available for this document.")

        with tab5:
            st.markdown("##### Extracted Entities")
            entities = results.get("entities", {})
            if entities and entities.get("summary"):
                entity_summary = entities["summary"]
                col1, col2, col3 = st.columns(3)
                with col1:
                    if "methods" in entity_summary:
                        methods = entity_summary["methods"]
                        st.markdown(f"**Research Methods** ({methods['unique_entities']})")
                        for m in methods.get("top_entities", [])[:5]:
                            st.markdown(f"- {m['text']} ({m['count']})")
                    if "software" in entity_summary:
                        software = entity_summary["software"]
                        st.markdown(f"**Software & Tools** ({software['unique_entities']})")
                        for s in software.get("top_entities", [])[:5]:
                            st.markdown(f"- {s['text']} ({s['count']})")
                with col2:
                    if "datasets" in entity_summary:
                        datasets = entity_summary["datasets"]
                        st.markdown(f"**Datasets** ({datasets['unique_entities']})")
                        for d in datasets.get("top_entities", [])[:5]:
                            st.markdown(f"- {d['text']} ({d['count']})")
                    if "institutions" in entity_summary:
                        institutions = entity_summary["institutions"]
                        st.markdown(f"**Institutions** ({institutions['unique_entities']})")
                        for i in institutions.get("top_entities", [])[:5]:
                            st.markdown(f"- {i['text']} ({i['count']})")
                with col3:
                    if "technical_terms" in entity_summary:
                        terms = entity_summary["technical_terms"]
                        st.markdown(f"**Technical Terms** ({terms['unique_entities']})")
                        for t in terms.get("top_entities", [])[:8]:
                            st.markdown(f"- {t['text']} ({t['count']})")
                st.markdown("---")
                authors = entities.get("authors", [])
                if authors:
                    st.markdown(f"**Potential Authors Mentioned:** {', '.join(authors[:10])}")
                research_questions = entities.get("research_questions", [])
                if research_questions:
                    st.markdown("**Research Questions Detected:**")
                    for rq in research_questions[:3]:
                        st.markdown(f"- {rq}")
                contributions = entities.get("contributions", [])
                if contributions:
                    st.markdown("**Contributions Detected:**")
                    for c in contributions[:3]:
                        st.markdown(f"- {c}")
            else:
                st.info("Entity extraction not available for this document.")

        with tab6:
            issues = results.get("issues", [])
            if issues:
                st.warning(f"**{len(issues)}** sentences exceed 30 words:")
                for i, sentence in enumerate(issues, 1):
                    st.warning(f"**{i}.** {sentence}")
            else:
                st.success("No overly long sentences detected.")

        with tab7:
            sections = current_analysis.get("sections", {})
            if sections:
                for section_name, content in sections.items():
                    if isinstance(content, dict):
                        content = content.get("content", "")
                    word_count = len(content.split())
                    with st.expander(f"{section_name} ({word_count} words)"):
                        summary = text_analyzer.extractive_summarize(content)
                        if summary:
                            st.markdown(f'<div class="summary-box"><strong>Summary:</strong> {summary}</div>',
                                        unsafe_allow_html=True)
                        st.markdown("**Full content:**")
                        st.markdown(f"""
                        <div style="max-height: 300px; overflow-y: auto; background: #f8fafc;
                            padding: 1rem; border-radius: 8px; border: 1px solid #e2e8f0;">
                        <pre style="white-space: pre-wrap; word-wrap: break-word; color: #1e293b;">{content}</pre>
                        </div>
                        """, unsafe_allow_html=True)

        with tab8:
            st.markdown("##### Advanced Analysis & Intelligence")
            advanced = results.get("advanced", {})

            # Sub-tabs within Advanced Analysis for better organization
            adv_tab1, adv_tab2, adv_tab3, adv_tab4 = st.tabs([
                "Quality & Acceptance", "Writing & Clarity", "Reproducibility", "Ethics & Rigor"
            ])

            with adv_tab1:
                quality = advanced.get("quality_prediction", {})
                if quality:
                    quality_score = quality.get("quality_score", 0)
                    grade = quality.get("grade", "N/A")
                    percentile = quality.get("percentile_estimate", 0)
                    col_q1, col_q2, col_q3 = st.columns(3)
                    col_q1.metric("Quality Score", f"{quality_score}/100")
                    col_q2.metric("Grade", grade)
                    col_q3.metric("Estimated Percentile", f"{percentile}th")

                    st.markdown("**Strengths:**")
                    for s in quality.get("strengths", ["Adequate structural quality"]):
                        st.markdown(f'<div class="success-card">{s}</div>', unsafe_allow_html=True)

                    st.markdown("**Areas for Improvement:**")
                    for w in quality.get("weaknesses", ["No major weaknesses"]):
                        st.markdown(f'<div class="warning-card">{w}</div>', unsafe_allow_html=True)

                    st.markdown("---")
                    st.markdown("##### Acceptance Probability")
                    acceptance = advanced.get("acceptance_probability", {})
                    predictions = acceptance.get("predictions", {})
                    if predictions:
                        for tier, data in predictions.items():
                            prob = data.get("probability", 0)
                            venue = data.get("venue_type", "")
                            st.markdown(f"**{venue}**: {prob}%")

            with adv_tab2:
                writing = advanced.get("writing_quality", {})
                if writing:
                    clarity_score = writing.get("clarity_score", 0)
                    avg_sent_len = writing.get("avg_sentence_length", 0)
                    passive_ratio = writing.get("passive_voice_ratio", 0)
                    col_w1, col_w2, col_w3 = st.columns(3)
                    col_w1.metric("Clarity Score", f"{clarity_score}/100")
                    col_w2.metric("Avg Sentence Length", f"{avg_sent_len} words")
                    col_w3.metric("Passive Voice", f"{passive_ratio*100:.1f}%")

                    issues = writing.get("issues", [])
                    if issues:
                        st.markdown("**Writing Issues:**")
                        for issue in issues:
                            st.markdown(f'<div class="warning-card">{issue.get("message", "")}</div>', unsafe_allow_html=True)

                    st.markdown("**Suggestions:**")
                    for s in writing.get("suggestions", ["Maintain current writing style"]):
                        st.markdown(f"- {s}")

            with adv_tab3:
                reproducibility = advanced.get("reproducibility", {})
                if reproducibility:
                    rep_score = reproducibility.get("score", 0)
                    rep_grade = reproducibility.get("grade", "N/A")
                    col_r1, col_r2 = st.columns(2)
                    col_r1.metric("Reproducibility Score", f"{rep_score}/100")
                    col_r2.metric("Grade", rep_grade)

                    st.markdown("**To Improve Reproducibility:**")
                    for r in reproducibility.get("recommendations", ["N/A"]):
                        st.markdown(f"- {r}")

            with adv_tab4:
                ethical = advanced.get("ethical_compliance", {})
                if ethical:
                    compliance_score = ethical.get("compliance_score", 0)
                    col_e1, col_e2 = st.columns(2)
                    col_e1.metric("Compliance Score", f"{compliance_score}/100")
                    col_e2.markdown(f"**Status:** {ethical.get('status', 'N/A').replace('_', ' ').title()}")

                st.markdown("---")
                statistical = advanced.get("statistical_rigor", {})
                if statistical:
                    stat_score = statistical.get("score", 0)
                    col_s1, col_s2 = st.columns(2)
                    col_s1.metric("Statistical Rigor Score", f"{stat_score}/100")
                    col_s2.metric("Grade", statistical.get("grade", "N/A"))

        with tab9:
            references = results.get("references", [])
            if references:
                st.markdown(f"##### Detected References ({len(references)})")
                for i, ref in enumerate(references, 1):
                    with st.expander(f"[{i}] {ref.get('authors', 'Unknown Authors')} ({ref.get('year', 'N/A')})"):
                        if ref.get("title"):
                            st.markdown(f"**Title:** {ref['title']}")
                        st.markdown(f"**Raw:** {ref['raw']}")
            else:
                st.info("No bibliography section detected or parsed.")

    elif current_analysis and not current_analysis.get("results"):
        st.info(f"Viewing saved analysis for: **{current_analysis['filename']}**")
        sections = current_analysis.get("sections", {})
        if sections:
            for section_name, content in sections.items():
                if isinstance(content, dict):
                    content = content.get("content", "")
                with st.expander(f"{section_name} ({len(content.split())} words)"):
                    summary = text_analyzer.extractive_summarize(content)
                    if summary:
                        st.markdown(f'<div class="summary-box"><strong>Summary:</strong> {summary}</div>',
                                    unsafe_allow_html=True)
                    st.markdown("**Full content:**")
                    st.markdown(f"""
                    <div style="max-height: 300px; overflow-y: auto; background: #f8fafc;
                        padding: 1rem; border-radius: 8px; border: 1px solid #e2e8f0;">
                    <pre style="white-space: pre-wrap; word-wrap: break-word; color: #1e293b;">{content}</pre>
                    </div>
                    """, unsafe_allow_html=True)

    else:
        st.markdown("#### Upload a research paper to analyze")
        # Enforce 10MB limit for Render free-tier stability
        uploaded_file = st.file_uploader("Upload Document (Max 10MB)", type=["pdf", "docx", "txt"])

        if uploaded_file:
            if uploaded_file.size > 10 * 1024 * 1024:
                st.error("File size exceeds 10MB limit. Please upload a smaller document.")
                st.stop()

            if st.button("Analyze Document", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()

                status_text.text("Step 1: Extracting text from document...")
                progress_bar.progress(10)

                if uploaded_file.name.endswith(".pdf"):
                    text = pdf_processor.extract_text_from_pdf(uploaded_file)
                elif uploaded_file.name.endswith(".docx"):
                    text = pdf_processor.extract_text_from_docx(uploaded_file)
                else:
                    text = uploaded_file.getvalue().decode("utf-8")

                status_text.text("Step 2: Cleaning and preprocessing text...")
                progress_bar.progress(25)

                cleaned_text = pdf_processor.clean_text(text)

                status_text.text("Step 3: Extracting document sections...")
                progress_bar.progress(40)

                sections = text_analyzer.extract_sections(cleaned_text)
                db_sections = {k: {"content": v, "keywords": []} for k, v in sections.items()}

                status_text.text("Step 4: Analyzing document metrics...")
                progress_bar.progress(55)

                results = text_analyzer.analyze_full_document(cleaned_text)

                if results is None:
                    progress_bar.empty()
                    status_text.empty()
                    st.error("Could not extract meaningful text from this document.")
                elif cleaned_text.startswith("[Error:"):
                    progress_bar.empty()
                    status_text.empty()
                    st.error(cleaned_text)
                else:
                    status_text.text("Step 5: Performing section-wise analysis...")
                    progress_bar.progress(70)

                    section_scores = text_analyzer.analyze_sections_full(sections)
                    results["section_scores"] = section_scores

                    status_text.text("Step 6: Saving analysis results...")
                    progress_bar.progress(85)

                    paper_dir = "data/research_papers"
                    if not os.path.exists(paper_dir):
                        os.makedirs(paper_dir)

                    saved_path = os.path.join(paper_dir, f"{int(time.time())}_{uploaded_file.name}")
                    with open(saved_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    database.save_analysis(
                        user_id=user['id'],
                        filename=uploaded_file.name,
                        sections_count=len(sections),
                        keywords=list(results["scores"].keys()),
                        sections_data=db_sections,
                        results_data=results,
                        file_path=saved_path
                    )

                    st.session_state["current_analysis"] = {
                        "filename": uploaded_file.name,
                        "sections": db_sections,
                        "results": results,
                        "section_scores": section_scores,
                        "timestamp": str(datetime.datetime.now()),
                        "file_path": saved_path
                    }

                    progress_bar.progress(100)
                    status_text.text("Analysis complete!")
                    time.sleep(0.5)
                    progress_bar.empty()
                    status_text.empty()
                    st.toast("Analysis complete!")
                    st.rerun()

def render_compare_page():
    user = st.session_state["user"]

    with st.sidebar:
        st.markdown(f"### Hello, {user['username']}")
        if st.button("Logout"):
            handle_logout()
        st.markdown("---")
        if st.button("Back to Dashboard"):
            navigate_to("dashboard")

    st.markdown('<div class="main-header">PaperIQ</div>', unsafe_allow_html=True)
    st.markdown("#### Multi-Document Comparison")

    history = database.get_user_history(user['id'])
    if not history or len(history) < 2:
        st.info("You need at least 2 analyses in your history to compare documents.")
        if st.button("Go to Dashboard"):
            navigate_to("dashboard")
        return

    st.markdown("Select 2 to 5 documents to compare:")

    selected_ids = []
    for item in history:
        date_str = item['upload_time'].split(' ')[0]
        label = f"{item['filename']} ({date_str})"
        if st.checkbox(label, key=f"compare_{item['id']}"):
            selected_ids.append(item['id'])

    if len(selected_ids) < 2:
        st.warning("Please select at least 2 documents to compare.")
        return

    if len(selected_ids) > 5:
        st.warning("Maximum 5 documents. Only the first 5 will be compared.")
        selected_ids = selected_ids[:5]

    if not st.button("Compare Selected Documents", type="primary"):
        return

    analyses = []
    for analysis_id in selected_ids:
        analysis = database.get_analysis_details(analysis_id)
        if analysis and analysis["results_json"]:
            try:
                results = json.loads(analysis["results_json"])
                results["filename"] = analysis["filename"]
                analyses.append(results)
            except json.JSONDecodeError:
                continue

    if len(analyses) < 2:
        st.error("Could not load selected documents for comparison.")
        return

    comparison = multidoc_analyzer.compare_multiple_documents(analyses)

    if "error" in comparison:
        st.error(comparison.get("error", "Comparison failed"))
        return

    summary = multidoc_analyzer.generate_comparison_summary(comparison)
    st.success(summary)

    st.markdown("---")
    st.markdown("##### Overall Rankings")
    rankings = comparison.get("rankings", [])
    for i, rank in enumerate(rankings, 1):
        score = rank.get("composite_score", 0)
        st.markdown(f"**{i}.** {rank['filename']} — Composite: **{score:.1f}/100**")

    st.markdown("---")
    st.markdown("##### Key Insights")
    insights = comparison.get("insights", [])
    if insights:
        for insight in insights:
            st.info(insight)
    else:
        st.info("No significant performance gaps detected between documents.")

    universal_kws = comparison.get("universal_keywords", [])
    if universal_kws:
        st.markdown("**Shared themes across all documents:**")
        kw_html = "".join(f'<span class="keyword-chip">{kw}</span>' for kw in universal_kws[:10])
        st.markdown(f'<div class="keywords-container">{kw_html}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("##### Metric Analysis")

    metric_scores = comparison.get("metric_scores", {})
    metrics = list(metric_scores.keys())
    if metrics:
        selected_metric = st.selectbox("Select metric to explore:", metrics)
        data = metric_scores.get(selected_metric, {})
        ranked = data.get("ranked", [])

        col_chart, col_detail = st.columns([3, 2])
        with col_chart:
            fig = go.Figure()
            doc_names = [r["filename"][:30] for r in ranked]
            doc_values = [r["value"] for r in ranked]
            avg = data.get("average", 0)
            fig.add_trace(go.Bar(
                x=doc_names,
                y=doc_values,
                marker_color=["#4F8EF7" if v >= avg else "#F47B4F" for v in doc_values],
                text=[f"{v:.1f}" for v in doc_values],
                textposition="outside"
            ))
            fig.add_hline(y=avg, line_dash="dash", line_color="#888",
                          annotation_text=f"Avg: {avg:.1f}")
            fig.update_layout(
                title=f"{selected_metric} — Score Comparison",
                yaxis=dict(range=[0, 110]),
                height=350,
                margin=dict(t=50, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_detail:
            st.markdown(f"**Spread:** {data.get('spread', 0):.1f} pts")
            st.markdown(f"**Average:** {data.get('average', 0):.1f}")
            st.markdown(f"**Std Dev:** {data.get('std_dev', 0):.1f}")
            best = data.get("best", {})
            worst = data.get("worst", {})
            st.markdown(f"**Best:** {best.get('filename', 'N/A')} ({best.get('value', 0):.1f})")
            st.markdown(f"**Lowest:** {worst.get('filename', 'N/A')} ({worst.get('value', 0):.1f})")

    st.markdown("---")
    st.markdown("##### Pairwise Comparisons")
    pairwise = comparison.get("pairwise", [])
    if pairwise:
        pair_labels = [f"{p['doc_a'][:20]} vs {p['doc_b'][:20]}" for p in pairwise]
        selected_pair_idx = st.selectbox("Select pair:", range(len(pair_labels)), format_func=lambda i: pair_labels[i])
        pair = pairwise[selected_pair_idx]

        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown(f"**{pair['doc_a']}**")
            strengths_a = pair.get("strengths_a", [])
            if strengths_a:
                for s in strengths_a:
                    st.markdown(f'<div class="success-card">{s}</div>', unsafe_allow_html=True)
            else:
                st.markdown("No decisive advantages detected.")

        with col_right:
            st.markdown(f"**{pair['doc_b']}**")
            strengths_b = pair.get("strengths_b", [])
            if strengths_b:
                for s in strengths_b:
                    st.markdown(f'<div class="success-card">{s}</div>', unsafe_allow_html=True)
            else:
                st.markdown("No decisive advantages detected.")

        st.markdown("**Per-Metric Delta**")
        metric_deltas = pair.get("metric_deltas", {})
        rows = []
        for metric, delta_info in metric_deltas.items():
            rows.append({
                "Metric": metric,
                pair['doc_a'][:20]: delta_info["doc_a"],
                pair['doc_b'][:20]: delta_info["doc_b"],
                "Gap": delta_info["delta"],
                "Leader": delta_info["leader"][:20] if delta_info["leader"] != "tied" else "Tied",
                "Assessment": delta_info["interpretation"]
            })
        if rows:
            import pandas as pd
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)

        kw_overlap = pair.get("keyword_overlap", {})
        if kw_overlap:
            st.markdown("**Keyword & Topic Overlap**")
            col_k1, col_k2, col_k3 = st.columns(3)
            with col_k1:
                st.markdown(f"Overlap: **{kw_overlap.get('overlap_percent', 0)}%** ({kw_overlap.get('topic_similarity', 'N/A')})")
                shared = kw_overlap.get("shared", [])
                if shared:
                    st.markdown("Shared: " + ", ".join(shared[:8]))
            with col_k2:
                unique_a = kw_overlap.get("unique_a", [])
                if unique_a:
                    st.markdown(f"Unique to {pair['doc_a'][:15]}:")
                    st.markdown(", ".join(unique_a[:6]))
            with col_k3:
                unique_b = kw_overlap.get("unique_b", [])
                if unique_b:
                    st.markdown(f"Unique to {pair['doc_b'][:15]}:")
                    st.markdown(", ".join(unique_b[:6]))

        section_cov = pair.get("section_coverage", {})
        if section_cov:
            st.markdown("**Section Coverage**")
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                shared_secs = section_cov.get("shared", [])
                st.markdown("Both have: " + (", ".join(shared_secs) if shared_secs else "None"))
            with col_s2:
                only_a = section_cov.get("only_in_a", [])
                if only_a:
                    st.markdown(f"Only in {pair['doc_a'][:15]}: " + ", ".join(only_a))
            with col_s3:
                only_b = section_cov.get("only_in_b", [])
                if only_b:
                    st.markdown(f"Only in {pair['doc_b'][:15]}: " + ", ".join(only_b))

        st.markdown(f"**Domain Agreement:** "
                    f"{'Same domain (' + pair.get('domain_a', '') + ')' if pair.get('domain_agreement') else pair.get('domain_a', 'N/A') + ' vs ' + pair.get('domain_b', 'N/A')}")


def render_arxiv_page():
    user = st.session_state["user"]

    with st.sidebar:
        st.markdown(f"### Hello, {user['username']}")
        if st.button("Logout"):
            handle_logout()
        st.markdown("---")
        if st.button("Back to Dashboard"):
            navigate_to("dashboard")

    st.markdown('<div class="main-header">PaperIQ</div>', unsafe_allow_html=True)
    st.markdown("#### Fetch Papers from arXiv")
    st.markdown("Search paper titles and abstracts directly on arXiv for accurate topic results.")

    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("Search Query:", placeholder="e.g., quantum computing error correction")
    with col2:
        max_results = st.number_input("Max Results:", min_value=1, max_value=50, value=10)

    col3, col4 = st.columns([2, 2])
    with col3:
        sort_options = ["relevance", "lastUpdatedDate", "submittedDate"]
        sort_by = st.selectbox("Sort By:", sort_options)
    with col4:
        category_options = {
            "Any": None,
            "Computer Science": "cs",
            "Physics": "physics",
            "Mathematics": "math",
            "Statistics": "stat",
            "Electrical Engineering": "eess",
            "Quantitative Biology": "q-bio",
            "Economics": "econ",
        }
        chosen_cat_label = st.selectbox("Category Filter:", list(category_options.keys()))
        chosen_cat = category_options[chosen_cat_label]

    if search_query and st.button("Search arXiv", type="primary"):
        with st.spinner("Searching arXiv..."):
            papers = arxiv_client.search_arxiv(
                query=search_query,
                max_results=max_results,
                sort_by=sort_by,
                category=chosen_cat
            )

        if papers:
            st.markdown(f"Found **{len(papers)}** papers:")
            for i, paper in enumerate(papers):
                title_display = paper.title if len(paper.title) <= 120 else paper.title[:117] + "..."
                with st.expander(f"{i+1}. {title_display}"):
                    authors_display = ", ".join(paper.authors[:5])
                    if len(paper.authors) > 5:
                        authors_display += f" and {len(paper.authors)-5} more"
                    st.markdown(f"**Authors:** {authors_display}")
                    published_display = paper.published[:10] if paper.published else "N/A"
                    st.markdown(f"**Published:** {published_display}")
                    categories_display = ", ".join(paper.categories[:5]) if paper.categories else "N/A"
                    st.markdown(f"**Categories:** {categories_display}")
                    abstract_clean = " ".join(paper.abstract.split())
                    abstract_display = abstract_clean[:600] + "..." if len(abstract_clean) > 600 else abstract_clean
                    st.markdown(f"**Abstract:** {abstract_display}")
                    col_pdf, col_arxiv, col_analyze = st.columns(3)
                    with col_pdf:
                        if paper.pdf_url:
                            st.link_button("View PDF", paper.pdf_url)
                    with col_arxiv:
                        if paper.arxiv_url:
                            st.link_button("View on arXiv", paper.arxiv_url)
                    with col_analyze:
                        if paper.pdf_url and st.button("Analyze & Save", key=f"analyze_{paper.paper_id}"):
                            with st.status("Ingesting arXiv paper...", expanded=True) as status:
                                paper_dir = "data/research_papers"
                                if not os.path.exists(paper_dir): os.makedirs(paper_dir)

                                safe_title = re.sub(r'[^\w\s-]', '', paper.title).replace(' ', '_')[:50]
                                filename = f"{paper.paper_id}_{safe_title}.pdf"
                                save_path = os.path.join(paper_dir, filename)

                                st.write("Downloading PDF...")
                                if arxiv_client.download_paper_pdf(paper.pdf_url, save_path):
                                    st.write("Extracting and analyzing...")
                                    text = pdf_processor.extract_text_from_pdf(save_path)
                                    cleaned_text = pdf_processor.clean_text(text)
                                    sections = text_analyzer.extract_sections(cleaned_text)
                                    db_sections = {k: {"content": v, "keywords": []} for k, v in sections.items()}
                                    results = text_analyzer.analyze_full_document(cleaned_text)

                                    if results:
                                        section_scores = text_analyzer.analyze_sections_full(sections)
                                        results["section_scores"] = section_scores

                                        database.save_analysis(
                                            user_id=user['id'],
                                            filename=filename,
                                            sections_count=len(sections),
                                            keywords=list(results["scores"].keys()),
                                            sections_data=db_sections,
                                            results_data=results,
                                            file_path=save_path
                                        )
                                        status.update(label="Ingestion complete!", state="complete")
                                        st.success(f"Analysis saved! View it in your history.")
                                    else:
                                        status.update(label="Analysis failed.", state="error")
                                else:
                                    status.update(label="Download failed.", state="error")
        else:
            st.info("No papers found. Try adjusting the query or removing the category filter.")


def render_trends_page():
    user = st.session_state["user"]

    with st.sidebar:
        st.markdown(f"### Hello, {user['username']}")
        if st.button("Logout"):
            handle_logout()
        st.markdown("---")
        if st.button("Back to Dashboard"):
            navigate_to("dashboard")

    st.markdown('<div class="main-header">PaperIQ</div>', unsafe_allow_html=True)
    st.markdown("#### Research Trends & Analytics")

    history = database.get_user_history(user['id'])
    if not history:
        st.info("No analysis history found. Start by analyzing some papers!")
        return

    analyses = []
    for item in history:
        details = database.get_analysis_details(item['id'])
        if details and details['results_json']:
            try:
                res = json.loads(details['results_json'])
                res['filename'] = details['filename']
                res['date'] = details['upload_time']
                analyses.append(res)
            except: continue

    if not analyses:
        st.warning("Could not process historical data.")
        return

    # Aggregate Analytics
    total_papers = len(analyses)
    avg_composite = sum(a['scores'].get('Composite', 0) for a in analyses) / total_papers

    domains = [a.get('domain', 'General') for a in analyses]
    from collections import Counter
    domain_counts = Counter(domains)

    st.markdown(f"Analyzed **{total_papers}** papers with an average composite score of **{avg_composite:.1f}/100**.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Domain Distribution")
        fig = go.Figure(go.Pie(labels=list(domain_counts.keys()), values=list(domain_counts.values()), hole=0.4))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("##### Score Progression")
        scores = [a['scores'].get('Composite', 0) for a in analyses][::-1]
        fig = go.Figure(go.Scatter(x=list(range(1, total_papers+1)), y=scores, mode='lines+markers', name='Composite Score'))
        fig.update_layout(xaxis_title="Paper # (Chronological)", yaxis_title="Score", height=350)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("##### Topic Heatmap (Common Keywords)")
    all_kws = []
    for a in analyses:
        all_kws.extend([k[0] for k in a.get('keywords', [])[:5]])

    if all_kws:
        common = Counter(all_kws).most_common(15)
        kw_html = "".join(f'<span class="keyword-chip">{k} <span class="score-pill">{v}</span></span>' for k, v in common)
        st.markdown(f'<div class="keywords-container">{kw_html}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("##### Structural Trends")
    elements_data = {
        "Figures": sum(a.get('elements', {}).get('figures', 0) for a in analyses),
        "Tables": sum(a.get('elements', {}).get('tables', 0) for a in analyses),
        "Equations": sum(a.get('elements', {}).get('equations', 0) for a in analyses)
    }
    c1, c2, c3 = st.columns(3)
    with c1: _render_stat_card("Total Figures", str(elements_data["Figures"]))
    with c2: _render_stat_card("Total Tables", str(elements_data["Tables"]))
    with c3: _render_stat_card("Total Equations", str(elements_data["Equations"]))


if st.session_state["page"] == "login":
    render_login_page()
elif st.session_state["page"] == "signup":
    render_signup_page()
elif st.session_state["page"] == "dashboard":
    render_dashboard()
elif st.session_state["page"] == "compare":
    render_compare_page()
elif st.session_state["page"] == "arxiv":
    render_arxiv_page()
elif st.session_state["page"] == "trends":
    render_trends_page()
