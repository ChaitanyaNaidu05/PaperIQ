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
import logging

import database
import auth
import styles
import pdf_processor
import text_analyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    if user and auth.verify_password(user['password_hash'], None, password):
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
        sections_data = None
        results_data = None
        keywords_data = None
        try:
            if analysis["sections_json"]:
                sections_data = json.loads(analysis["sections_json"])
            if analysis["results_json"]:
                results_data = json.loads(analysis["results_json"])
            if analysis["keywords_json"]:
                keywords_data = json.loads(analysis["keywords_json"])
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error for analysis {analysis_id}: {e}")
        
        st.session_state["current_analysis"] = {
            "id": analysis["id"],
            "filename": analysis["filename"],
            "sections": sections_data if sections_data else {},
            "keywords": keywords_data if keywords_data else [],
            "timestamp": analysis["upload_time"],
            "results": results_data if results_data else None
        }
        logger.info(f"Loaded analysis from history: {analysis['filename']} (ID: {analysis_id})")

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
        html += f'<span class="struct-found">{s}</span>'
    for s in missing:
        html += f'<span class="struct-missing">{s}</span>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

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
        if st.button("Search Papers"):
            navigate_to("search")
        if st.button("Fetch from arXiv"):
            navigate_to("arxiv")

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

        col_domain, col_download = st.columns([3, 1])
        with col_domain:
            domain = results.get("domain", "General")
            st.markdown(f'<span class="domain-badge">{domain}</span>', unsafe_allow_html=True)
        with col_download:
            section_scores = results.get("section_scores", [])
            pdf_bytes = text_analyzer.create_pdf_report(filename, results, section_scores)
            st.download_button("Download Report", pdf_bytes, "report.pdf", "application/pdf")

        doc_summary = results.get("document_summary", "")
        if doc_summary:
            st.markdown("#### Document Summary")
            st.markdown(f'<div class="summary-box">{doc_summary}</div>', unsafe_allow_html=True)

        keywords = results.get("keywords", [])
        _render_keyword_chips(keywords)

        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
            "Radar & Scores", "Statistics", "Structure", "Section Analysis", "Entities", "Issues", "Sections", "Advanced Analysis"
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
                        st.text_area(f"Full content - {section_name}", content, height=200,
                                     key=f"section_{section_name}")

        with tab8:
            st.markdown("##### Quality Prediction")
            advanced = results.get("advanced", {})
            quality = advanced.get("quality_prediction", {})
            
            if quality:
                quality_score = quality.get("quality_score", 0)
                grade = quality.get("grade", "N/A")
                percentile = quality.get("percentile_estimate", 0)
                
                col_q1, col_q2, col_q3 = st.columns(3)
                col_q1.metric("Quality Score", f"{quality_score}/100")
                col_q2.metric("Grade", grade)
                col_q3.metric("Estimated Percentile", f"{percentile}th")
                
                strengths = quality.get("strengths", [])
                if strengths:
                    st.markdown("**Strengths:**")
                    for s in strengths:
                        st.markdown(f'<div class="success-card">{s}</div>', unsafe_allow_html=True)
                
                weaknesses = quality.get("weaknesses", [])
                if weaknesses:
                    st.markdown("**Areas for Improvement:**")
                    for w in weaknesses:
                        st.markdown(f'<div class="warning-card">{w}</div>', unsafe_allow_html=True)
                
                recommendations = quality.get("recommendations", [])
                if recommendations:
                    st.markdown("**Recommendations:**")
                    for r in recommendations:
                        st.markdown(f"- {r}")
                
                st.markdown("---")
                st.markdown("##### Acceptance Probability")
                acceptance = advanced.get("acceptance_probability", {})
                predictions = acceptance.get("predictions", {})
                
                if predictions:
                    for tier, data in predictions.items():
                        prob = data.get("probability", 0)
                        venue = data.get("venue_type", "")
                        st.markdown(f"**{venue}**: {prob}%")
            
            st.markdown("---")
            st.markdown("##### Writing Quality")
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
                
                suggestions = writing.get("suggestions", [])
                if suggestions:
                    st.markdown("**Suggestions:**")
                    for s in suggestions:
                        st.markdown(f"- {s}")
            
            st.markdown("---")
            st.markdown("##### Reproducibility")
            reproducibility = advanced.get("reproducibility", {})
            if reproducibility:
                rep_score = reproducibility.get("score", 0)
                rep_grade = reproducibility.get("grade", "N/A")
                
                col_r1, col_r2 = st.columns(2)
                col_r1.metric("Reproducibility Score", f"{rep_score}/100")
                col_r2.metric("Grade", rep_grade)
                
                recommendations = reproducibility.get("recommendations", [])
                if recommendations:
                    st.markdown("**To Improve Reproducibility:**")
                    for r in recommendations:
                        st.markdown(f"- {r}")
            
            st.markdown("---")
            st.markdown("##### Ethical Compliance")
            ethical = advanced.get("ethical_compliance", {})
            if ethical:
                compliance_score = ethical.get("compliance_score", 0)
                status = ethical.get("status", "unknown")
                
                col_e1, col_e2 = st.columns(2)
                col_e1.metric("Compliance Score", f"{compliance_score}/100")
                col_e2.markdown(f"**Status:** {status.replace('_', ' ').title()}")
                
                missing = ethical.get("missing_requirements", [])
                if missing:
                    st.markdown("**Missing Requirements:**")
                    for m in missing:
                        st.markdown(f'<div class="warning-card">{m}</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("##### Statistical Rigor")
            statistical = advanced.get("statistical_rigor", {})
            if statistical:
                stat_score = statistical.get("score", 0)
                stat_grade = statistical.get("grade", "N/A")
                
                col_s1, col_s2 = st.columns(2)
                col_s1.metric("Statistical Rigor Score", f"{stat_score}/100")
                col_s2.metric("Grade", stat_grade)
                
                tests_used = statistical.get("indicators", {}).get("tests_used", [])
                if tests_used:
                    st.markdown(f"**Statistical Tests Used:** {', '.join(tests_used)}")
                
                recommendations = statistical.get("recommendations", [])
                if recommendations:
                    st.markdown("**Recommendations:**")
                    for r in recommendations:
                        st.markdown(f"- {r}")

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
                    st.text_area(f"Content – {section_name}", content, height=200,
                                 key=f"hist_section_{section_name}")

    else:
        st.markdown("#### Upload a research paper to analyze")
        uploaded_file = st.file_uploader("Upload Document", type=["pdf", "docx", "txt"])

        if uploaded_file and st.button("Analyze Document", type="primary"):
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
            else:
                status_text.text("Step 5: Performing section-wise analysis...")
                progress_bar.progress(70)
                
                section_scores = text_analyzer.analyze_sections_full(sections)
                results["section_scores"] = section_scores
                
                status_text.text("Step 6: Saving analysis results...")
                progress_bar.progress(85)

                database.save_analysis(
                    user_id=user['id'],
                    filename=uploaded_file.name,
                    sections_count=len(sections),
                    keywords=list(results["scores"].keys()),
                    sections_data=db_sections,
                    results_data=results
                )

                st.session_state["current_analysis"] = {
                    "filename": uploaded_file.name,
                    "sections": db_sections,
                    "results": results,
                    "section_scores": section_scores,
                    "timestamp": str(datetime.datetime.now())
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

    st.markdown("Select documents to compare (2-5 documents):")
    
    selected_ids = []
    for item in history:
        date_str = item['upload_time'].split(' ')[0]
        label = f"{item['filename']} ({date_str})"
        if st.checkbox(label, key=f"compare_{item['id']}"):
            selected_ids.append(item['id'])

    if len(selected_ids) < 2:
        st.warning("Please select at least 2 documents to compare.")
    else:
        if st.button("Compare Selected Documents", type="primary"):
            analyses = []
            for analysis_id in selected_ids[:5]:
                analysis = database.get_analysis_details(analysis_id)
                if analysis and analysis.get("results_json"):
                    try:
                        results = json.loads(analysis["results_json"])
                        results["filename"] = analysis["filename"]
                        analyses.append(results)
                    except json.JSONDecodeError:
                        continue
            
            if len(analyses) < 2:
                st.error("Could not load selected documents for comparison.")
            else:
                import multidoc_analyzer
                comparison = multidoc_analyzer.compare_multiple_documents(analyses)
                
                if "error" not in comparison:
                    summary = multidoc_analyzer.generate_comparison_summary(comparison)
                    st.success(summary)
                    
                    st.markdown("##### Overall Rankings")
                    rankings = comparison.get("rankings", {}).get("by_composite_score", [])
                    for i, rank in enumerate(rankings, 1):
                        st.markdown(
                            f"**{i}.** {rank['filename']} - "
                            f"Score: {rank['composite_score']:.1f}/100"
                        )
                    
                    st.markdown("##### Metrics Comparison")
                    metrics_tabs = st.tabs([
                        "Composite", "Language", "Coherence", "Technical Depth",
                        "Novelty", "Readability"
                    ])
                    
                    metric_map = {
                        "Composite": "Composite",
                        "Language": "Language",
                        "Coherence": "Coherence",
                        "Technical Depth": "Technical Depth",
                        "Novelty": "Novelty Signal",
                        "Readability": "Readability"
                    }
                    
                    for i, tab in enumerate(metrics_tabs):
                        with tab:
                            metric_name = list(metric_map.values())[i]
                            metric_data = None
                            for md in comparison.get("metrics_comparison", []):
                                if md.get("metric") == metric_name:
                                    metric_data = md
                                    break
                            
                            if metric_data:
                                values = sorted(
                                    metric_data.get("values", []),
                                    key=lambda x: x["value"],
                                    reverse=True
                                )
                                for v in values:
                                    st.markdown(
                                        f"**{v['filename']}:** {v['value']:.1f}"
                                    )
                    
                    st.markdown("##### Best in Category")
                    best_in_cat = comparison.get("best_in_category", {})
                    cols = st.columns(3)
                    categories = [
                        "Technical Depth", "Novelty Signal", "Structural Completeness",
                        "Language", "Coherence", "Readability"
                    ]
                    for i, cat in enumerate(categories):
                        if cat in best_in_cat:
                            best = best_in_cat[cat]
                            with cols[i % 3]:
                                st.markdown(
                                    f"**{cat}**\n\n"
                                    f"{best.get('document', 'N/A')[:25]}...\n\n"
                                    f"Score: {best.get('score', 0):.1f}"
                                )
                    
                    st.markdown("##### Average Scores Across Documents")
                    avg_scores = comparison.get("average_scores", {})
                    avg_cols = st.columns(5)
                    avg_metrics = ["Composite", "Language", "Coherence", 
                                   "Technical Depth", "Novelty Signal"]
                    for i, metric in enumerate(avg_metrics):
                        if metric in avg_scores:
                            avg_cols[i].metric(
                                metric,
                                f"{avg_scores[metric]:.1f}/100"
                            )
                else:
                    st.error(comparison.get("error", "Comparison failed"))


def render_search_page():
    user = st.session_state["user"]

    with st.sidebar:
        st.markdown(f"### Hello, {user['username']}")
        if st.button("Logout"):
            handle_logout()
        st.markdown("---")
        if st.button("Back to Dashboard"):
            navigate_to("dashboard")

    st.markdown('<div class="main-header">PaperIQ</div>', unsafe_allow_html=True)
    st.markdown("#### Semantic Search")
    st.markdown("Search across all your analyzed papers using natural language queries.")

    query = st.text_input("Enter your search query:", placeholder="e.g., machine learning classification methods")

    if query:
        import semantic_search
        results = semantic_search.search_papers(query, top_k=10)

        if results:
            st.markdown(f"Found {len(results)} relevant papers:")
            for i, result in enumerate(results, 1):
                with st.expander(f"Result {i} - Score: {result['score']:.3f}"):
                    st.markdown(f"**Snippet:** {result['snippet']}")
                    if st.button(f"View Analysis", key=f"view_{result['doc_id']}"):
                        load_analysis_from_history(result['doc_id'])
                        navigate_to("dashboard")
                        st.rerun()
        else:
            st.info("No papers found matching your query. Try different keywords.")


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
    st.markdown("Search and fetch paper metadata directly from arXiv.")

    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("Search Query:", placeholder="e.g., deep learning image classification")
    with col2:
        max_results = st.number_input("Max Results:", min_value=1, max_value=50, value=10)

    sort_options = ["relevance", "lastUpdatedDate", "submittedDate"]
    sort_by = st.selectbox("Sort By:", sort_options)

    if search_query and st.button("Search arXiv", type="primary"):
        import arxiv_client
        with st.spinner("Searching arXiv..."):
            papers = arxiv_client.search_arxiv(
                query=search_query,
                max_results=max_results,
                sort_by=sort_by
            )

            if papers:
                st.markdown(f"Found {len(papers)} papers:")
                for i, paper in enumerate(papers):
                    with st.expander(f"{i+1}. {paper.title[:100]}..."):
                        st.markdown(f"**Authors:** {', '.join(paper.authors[:5])}")
                        if len(paper.authors) > 5:
                            st.markdown(f"*...and {len(paper.authors)-5} more authors*")
                        st.markdown(f"**Published:** {paper.published[:10] if paper.published else 'N/A'}")
                        st.markdown(f"**Categories:** {', '.join(paper.categories[:5])}")
                        st.markdown(f"**Abstract:** {paper.abstract[:500]}...")
                        col_pdf, col_arxiv = st.columns(2)
                        with col_pdf:
                            if paper.pdf_url:
                                st.link_button("View PDF", paper.pdf_url)
                        with col_arxiv:
                            if paper.arxiv_url:
                                st.link_button("View on arXiv", paper.arxiv_url)
            else:
                st.info("No papers found. Try a different search query.")


if st.session_state["page"] == "login":
    render_login_page()
elif st.session_state["page"] == "signup":
    render_signup_page()
elif st.session_state["page"] == "dashboard":
    render_dashboard()
elif st.session_state["page"] == "compare":
    render_compare_page()
elif st.session_state["page"] == "search":
    render_search_page()
elif st.session_state["page"] == "arxiv":
    render_arxiv_page()
